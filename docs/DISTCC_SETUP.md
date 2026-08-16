# distcc: offloading compile jobs to a second machine

If you have two machines — a **master** that actually runs the build (RAM/disk matter most here)
and a **helper** that just lends spare CPU cores — [distcc](https://github.com/distcc/distcc) can
distribute compile jobs between them. This doc assumes the ThinkPad (or whichever machine has the
250GB+ disk and does the real `pixelos sync`) is the master, and a second machine (e.g. an old Acer)
is the helper.

## Is this worth it for you?

Be honest with yourself before spending the setup time:

- distcc only distributes **compiling** (`.c`/`.cpp` → `.o`). Linking — the part that actually eats
  RAM and where OOM kills happen — always runs on the master. A weak/low-RAM master stays the
  bottleneck regardless of how many helpers you add.
- The helper's cores need to actually be *good* cores. An old, low-IPC helper CPU can net you less
  than you'd hope for relative to the setup effort — this isn't free performance, just borrowed
  performance, and old hardware borrows slowly.
- One-time setup is roughly 1-2 hours: installing distccd, getting the network/firewall right,
  and — the part people skip and then wonder why nothing sped up — getting the **exact same
  compiler binary** onto the helper (see step 2 below).

If that trade-off still looks better than a build that might get killed overnight anyway, here's
the setup.

## Prerequisites

- Both machines on the same LAN (Ethernet strongly preferred over Wi-Fi for this — old Wi-Fi chips
  on either end are a common source of "it works then randomly stalls").
- SSH access from the master to the helper (for `tools/distcc/sync-toolchain.sh`).
- The master has already run `pixelos sync` at least once — the helper needs a copy of the exact
  toolchain that sync produced, not just "some" clang.
- **The helper needs to run actual Linux.** The toolchain is a Linux ELF binary — it cannot run on
  bare Windows, Cygwin, or MSYS2 (those give you POSIX-ish source compatibility, not the ability to
  execute a foreign binary format). If your helper is a Windows machine, that means **WSL2**
  specifically (not WSL1, which doesn't run these binaries reliably either) — see the dedicated
  section below before continuing with steps 1-4, which otherwise assume a native Linux helper.

## Step 1: find the helper's IP

On the helper machine:

```bash
ip addr show | grep 'inet '
```

Note the LAN IP (e.g. `192.168.1.50`) — you'll need it on both ends.

## Step 2: push the matching toolchain to the helper

**On the master**, from this repo:

```bash
tools/distcc/sync-toolchain.sh pixelos@192.168.1.50
```

This rsyncs the clang toolchain your synced source tree actually uses. Skipping this step is the
#1 reason people set up distcc and see zero speedup: distcc silently falls back to local compilation
whenever the helper's compiler version doesn't match, with no obvious error — it just quietly isn't
helping. Re-run this script after any `pixelos sync` that updates the toolchain.

## Step 3: start distccd on the helper

**On the helper**, put the synced toolchain on `PATH` (the script prints the exact export command
at the end of step 2) then:

```bash
tools/distcc/setup-helper.sh 192.168.1.50-of-the-master
```

(Yes, the argument is the **master's** IP — distccd only accepts connections from it.) This installs
`distcc` if missing and runs `distccd` in the foreground, restricted to the master's IP. Leave this
running in a terminal (or a `screen`/`tmux` session) for the duration of the build.

## Helper running Windows (via WSL2)

If the helper is Windows, steps 2-3 above happen **inside a WSL2 Ubuntu distro**, not on bare
Windows — but reaching that distro from the master needs extra setup, and it differs by Windows
version.

### 0. Enable virtualization in the BIOS (if not already)

WSL2 needs hardware virtualization (AMD-V/SVM on AMD CPUs). Reboot into the BIOS setup (commonly
`F2` or `Del` at boot on Acer machines — the exact key and menu wording vary by BIOS version), look
under a tab like *Advanced* or *Configuration* for **"SVM Mode"** or **"Virtualization"**, set it to
*Enabled*, then save and exit (commonly `F10`). If you don't see any such option, check whether it's
already on by default — plenty of BIOS versions ship with it enabled and don't expose a toggle.

### 1. Install WSL2 + Ubuntu

In an **administrator** PowerShell or Command Prompt:

```powershell
wsl --install -d Ubuntu
```

Reboot if prompted. This needs Windows 10 build 19041+ — if `wsl --install` isn't recognized at all,
run `winver` to check your build and update Windows first. Once installed, launch "Ubuntu" from the
Start menu once to finish its first-run setup (creates a Unix user/password inside the distro).

### 2. Run steps 2-3 from above, inside WSL2

Open the "Ubuntu" app (this is now a real Ubuntu shell) and run `tools/distcc/setup-helper.sh` there
exactly as documented above — it's genuine Linux, nothing WSL-specific about that part. (You'll need
this repo's `tools/distcc/` scripts available inside WSL2 too — `git clone` the repo there, or just
copy the `tools/distcc/` directory in.)

### 3. Make distccd reachable from the LAN

This is the part that's actually different on Windows, and it depends on your Windows version:

- **Windows 11 22H2+**: WSL2 supports "mirrored" networking, where the distro shares the host's
  network interface directly — no port forwarding needed. Enable it by creating (or editing)
  `%UserProfile%\.wslconfig` with:
  ```ini
  [wsl2]
  networkingMode=mirrored
  ```
  then `wsl --shutdown` and relaunch. If this works, distccd is reachable at the helper's normal LAN
  IP with no further steps.

- **Windows 10** (no mirrored mode available): WSL2 sits behind its own internal NAT by default, so
  the master can't reach distccd inside WSL2 without forwarding the port through Windows first. Run,
  in an **administrator** PowerShell on the helper:
  ```powershell
  tools\distcc\windows-portproxy.ps1 -MasterIp 192.168.1.20
  ```
  (replace with the master's actual IP). This finds WSL2's current internal IP, forwards
  `<helper-LAN-IP>:3632` to it, and opens a Windows Firewall rule restricted to the master's IP.
  **Re-run this script after every Windows reboot or WSL2 restart** — WSL2's internal IP isn't
  stable across those.

Either way, once done, `PIXELOS_DISTCC_HOSTS` on the master just uses the helper's normal LAN IP —
the master doesn't need to know or care that the helper is Windows underneath.

## Step 4: point the master at the helper

**On the master**:

```bash
export PIXELOS_DISTCC_HOSTS="192.168.1.50/4"   # /4 = use 4 of the helper's job slots
tools/pixelos-cli/pixelos distcc-check          # confirms the helper is reachable
tools/pixelos-cli/pixelos build pixelos_x86_64 eng
```

`pixelos build` picks up `PIXELOS_DISTCC_HOSTS` automatically — it sets `DISTCC_HOSTS` (including
`localhost` so the master still compiles some jobs itself) and `CCACHE_PREFIX=distcc` so ccache
routes cache misses through distcc instead of the compiler directly.

## Verifying it's actually helping (not just "not erroring")

`pixelos distcc-check` only confirms the helper's port is reachable — that's necessary but not
sufficient. To confirm jobs are actually landing on the helper during a real build:

```bash
distccmon-text 1
```

in a second terminal on the master while a build is running. If every row shows `localhost`, jobs
aren't being distributed — almost always a toolchain mismatch (redo step 2) or a stale
`PIXELOS_DISTCC_HOSTS` value.

## Combine with the low-RAM guidance

distcc and `PIXELOS_JOBS`/swap (see `docs/GETTING_STARTED.md`) aren't mutually exclusive — you can
still cap the master's own parallelism with `PIXELOS_JOBS` while distcc sends *additional* jobs to
the helper. If the master is the low-RAM machine, that combination — few local jobs, several remote
ones — is exactly the point.
