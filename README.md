# ansible-wsl-update

Ansible playbook to update all WSL distributions on a single Windows machine. Supports Debian/Ubuntu (apt) and Fedora/RHEL/Rocky/Alma (dnf). Uses a custom WSL connection plugin — no SSH required.

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
ansible-playbook update.yml --limit MyDistro
```

Use dist-upgrade instead of safe upgrade (Debian/Ubuntu only):

```bash
ansible-playbook update.yml -e apt_upgrade_mode=dist
```

The `apt_upgrade_mode` variable accepts `safe` (default), `full`, or `dist`.

## Supported Distro Families

| Family | Package manager | Detected via |
|--------|----------------|--------------|
| Debian/Ubuntu | apt | `ansible_os_family == "Debian"` |
| Fedora/RHEL/Rocky/Alma | dnf | `ansible_os_family == "RedHat"` |

Ansible auto-detects the distro family via facts gathering — no manual configuration needed.

## How It Works

The `connection_plugins/wsl.py` plugin uses `wsl.exe -d <distro>` to execute commands in each distribution. This means:

- No SSH servers to install or manage
- No keys to distribute
- No ports to juggle
- All standard Ansible modules work (apt, dnf, copy, template, etc.)
- Run from any WSL distro — no localhost dependency

The only requirement is that `wsl.exe` is on the PATH, which it is by default in any WSL distribution.
