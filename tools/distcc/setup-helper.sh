#!/usr/bin/env bash
# Run this ON THE HELPER MACHINE (the Acer, or whichever box is lending its cores) — not on the
# master (ThinkPad) where the actual build runs. Installs and starts distccd, restricted to accept
# connections only from the master's IP. See docs/DISTCC_SETUP.md for the full picture; this script
# is only step 2 of that guide.
set -euo pipefail

usage() {
  cat <<'EOF'
usage: setup-helper.sh <master-ip> [port]

  <master-ip>  IP address of the machine that will run the actual build (the ThinkPad) —
               distccd will refuse connections from anyone else.
  [port]       Defaults to 3632, distcc's standard port.
EOF
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 1
fi

MASTER_IP="$1"
PORT="${2:-3632}"

if ! command -v distccd >/dev/null 2>&1; then
  echo "Installing distcc..."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y distcc
  else
    echo "error: no apt-get found — install distccd manually for your distro, then re-run this script" >&2
    exit 1
  fi
fi

NPROC=$(nproc)
echo "This machine has $NPROC cores — distccd will advertise that many job slots."

echo "Starting distccd, restricted to connections from $MASTER_IP on port $PORT..."
# --no-detach + a trap so Ctrl-C actually stops it, rather than backgrounding silently and leaving
# a stray daemon the user forgets about on a machine that isn't theirs to keep running indefinitely.
trap 'echo; echo "stopping distccd"; exit 0' INT TERM

distccd \
  --no-detach \
  --allow "$MASTER_IP" \
  --port "$PORT" \
  --jobs "$NPROC" \
  --log-stderr &
DISTCCD_PID=$!

echo "distccd running (pid $DISTCCD_PID), only accepting connections from $MASTER_IP:$PORT."
echo "Firewall reminder: if ufw/firewalld is active on this machine, allow inbound TCP $PORT from $MASTER_IP, e.g.:"
echo "  sudo ufw allow from $MASTER_IP to any port $PORT proto tcp"
echo "Press Ctrl-C to stop."
wait "$DISTCCD_PID"
