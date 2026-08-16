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
