#!/usr/bin/env bash
# Run this ON THE MASTER MACHINE (the ThinkPad, wherever `pixelos sync` ran) — pushes the exact
# clang toolchain from the synced source tree to a helper machine over SSH. Plain (non-"pump")
# distcc only distributes the actual compile step — the master preprocesses locally — but the
# helper still needs the *identical* compiler binary, not just "a" clang, or every job silently
# falls back to local compilation and you get zero benefit with no obvious error.
#
# TODO(verify): the exact prebuilt clang path below matches the layout AOSP/LineageOS trees have
# used for years, but hasn't been checked against this specific lineage-16.0 sync yet — confirm
# with `ls "$SRC_DIR"/prebuilts/clang/host/linux-x86/` once you've actually run `pixelos sync`,
# and adjust CLANG_DIR_PATTERN below if the directory name differs.
set -euo pipefail

SRC_DIR="${PIXELOS_SRC_DIR:-$HOME/pixelos-src}"
CLANG_DIR_PATTERN="clang-*"

usage() {
  cat <<'EOF'
usage: sync-toolchain.sh <user@helper-host> [remote-dest-dir]

  <user@helper-host>  SSH target for the helper machine (the Acer), e.g. pixelos@192.168.1.50
  [remote-dest-dir]   Where to put the toolchain on the helper (default: pixelos-toolchain)
EOF
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 1
fi

HELPER="$1"
REMOTE_DEST="${2:-pixelos-toolchain}"

if [[ ! -d "$SRC_DIR/.repo" ]]; then
  echo "error: no synced source tree at $SRC_DIR — run 'pixelos sync' on this machine first" >&2
  exit 1
fi

clang_base="$SRC_DIR/prebuilts/clang/host/linux-x86"
# shellcheck disable=SC2206 # intentional word-splitting glob expansion into an array
local_clang_dirs=("$clang_base"/$CLANG_DIR_PATTERN)
if [[ ! -d "${local_clang_dirs[0]:-}" ]]; then
  echo "error: no clang toolchain found matching $clang_base/$CLANG_DIR_PATTERN — see the TODO(verify) comment at the top of this script" >&2
  exit 1
fi
if (( ${#local_clang_dirs[@]} > 1 )); then
  echo "warning: multiple clang dirs matched, syncing all of them: ${local_clang_dirs[*]}"
fi

echo "Syncing ${#local_clang_dirs[@]} clang toolchain dir(s) to $HELPER:$REMOTE_DEST/ ..."
echo "(first run copies several GB — expect minutes, not seconds, even on a fast LAN)"
# shellcheck disable=SC2029 # REMOTE_DEST is a local, non-attacker-controlled path — client-side expansion is intended
ssh "$HELPER" "mkdir -p $REMOTE_DEST"
rsync -az --info=progress2 "${local_clang_dirs[@]}" "$HELPER:$REMOTE_DEST/"

first_dir_name="$(basename "${local_clang_dirs[0]}")"
cat <<EOF

Done. On the helper machine, distccd needs this toolchain's bin/ dir on its PATH so the version
distcc dispatches to matches what the master expects — e.g. before running setup-helper.sh:

  export PATH="\$HOME/$REMOTE_DEST/$first_dir_name/bin:\$PATH"

Re-run this script after any 'pixelos sync' that updates the toolchain (rsync only re-transfers
what changed, so repeat runs are fast).
EOF
