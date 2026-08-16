# Run this ON THE HELPER MACHINE, in an ADMINISTRATOR PowerShell — only needed when the helper is
# Windows 10 running distccd inside WSL2. Windows 10 doesn't have WSL2's "mirrored" networking mode
# (that's Windows 11 22H2+), so WSL2 sits behind its own internal NAT: nothing on your LAN — like
# the master machine — can reach distccd inside WSL2 without this port forward.
#
# WSL2's internal IP changes on reboot, so re-run this script any time you restart Windows or WSL2.
# See docs/DISTCC_SETUP.md's "Helper running Windows (via WSL2)" section for the full picture.

param(
    [int]$Port = 3632,
    [Parameter(Mandatory=$true)][string]$MasterIp
)

$wslIp = (wsl hostname -I).Trim().Split(" ")[0]
if (-not $wslIp) {
    Write-Error "Could not determine WSL2's IP — is a WSL2 distro actually running? Try 'wsl' first."
    exit 1
}

Write-Host "WSL2 IP: $wslIp   Forwarding 0.0.0.0:$Port -> ${wslIp}:$Port"

netsh interface portproxy delete v4tov4 listenport=$Port listenaddress=0.0.0.0 2>$null | Out-Null
netsh interface portproxy add v4tov4 listenport=$Port listenaddress=0.0.0.0 connectport=$Port connectaddress=$wslIp

$ruleName = "pixelos-distccd"
if (-not (Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP -LocalPort $Port -Action Allow -RemoteAddress $MasterIp | Out-Null
    Write-Host "Firewall rule '$ruleName' created, restricted to $MasterIp."
} else {
    Write-Host "Firewall rule '$ruleName' already exists — not duplicating it. Delete it manually first if the master's IP changed."
}

Write-Host "Done. distccd inside WSL2 should now be reachable at this machine's LAN IP on port $Port."
