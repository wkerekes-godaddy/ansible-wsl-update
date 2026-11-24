# ansible-wsl-update

Ansible playbook to run `apt update` and `dist-upgrade` across multiple WSL distributions on a single Windows machine. Uses a custom WSL connection plugin — no SSH required.

## Requirements

- Windows with WSL 2
- Ansible installed in at least one WSL distribution (the control node)
- `wsl.exe` accessible from your WSL environment (this is the default)

## Setup

Run the inventory builder to auto-detect your WSL distributions:

```bash
./build-inventory.sh
```

This generates `inventory.yml` from `wsl.exe -l -q`. Re-run it any time you add or remove distros.

Alternatively, copy and edit the example manually:

```bash
cp inventory.yml.example inventory.yml
```

## Usage

```bash
ansible-playbook update.yml
```

Dry run (check mode):

```bash
ansible-playbook update.yml --check
```

Target a single distro:

```bash
ansible-playbook update.yml --limit Claudebuntu
```

## How It Works

The `connection_plugins/wsl.py` plugin uses `wsl.exe -d <distro>` to execute commands in each distribution. This means:

- No SSH servers to install or manage
- No keys to distribute
- No ports to juggle
- All standard Ansible modules work (apt, copy, template, etc.)

The only requirement is that `wsl.exe` is on the PATH, which it is by default in any WSL distribution.
