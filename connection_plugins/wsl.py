from __future__ import annotations

import os
import shlex
import subprocess
from ansible.errors import AnsibleError
from ansible.plugins.connection import ConnectionBase

DOCUMENTATION = """
    name: wsl
    short_description: Connect to WSL distributions via wsl.exe
    description:
        - Run commands and transfer files to WSL distributions on the same
          Windows host using wsl.exe as the transport. No SSH required.
    options:
        distro:
            description: WSL distribution name (as shown by C(wsl --list)).
            vars:
                - name: ansible_wsl_distro
                - name: ansible_host
            required: true
        wsl_user:
            description: User to execute commands as inside the WSL distribution.
            vars:
                - name: ansible_wsl_user
                - name: ansible_user
            default: root
        wsl_exe:
            description: Path to the wsl.exe binary.
            vars:
                - name: ansible_wsl_exe
            default: wsl.exe
"""

class Connection(ConnectionBase):

    transport = "wsl"
    has_pipelining = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.distro = None
        self.wsl_user = None
        self.wsl_exe = None

    def _connect(self):
        if self._connected:
            return self

        self.distro = self.get_option("distro") or self._play_context.remote_addr
        self.wsl_user = self.get_option("wsl_user") or self._play_context.remote_user or "root"
        self.wsl_exe = self.get_option("wsl_exe") or "wsl.exe"

        self._connected = True
        return self

    def _build_command(self, cmd):
        return [
            self.wsl_exe,
            "-d", self.distro,
            "-u", self.wsl_user,
            "--", "sh", "-c", cmd,
        ]

    def exec_command(self, cmd, in_data=None, sudoable=True):
        super().exec_command(cmd, in_data=in_data, sudoable=sudoable)
        self._connect()

        full_cmd = self._build_command(cmd)
        self._display.vvv(f"WSL exec: {full_cmd}", host=self.distro)

        proc = subprocess.Popen(
            full_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate(in_data)
        return proc.returncode, stdout, stderr

    def put_file(self, in_path, out_path):
        super().put_file(in_path, out_path)
        self._connect()

        self._display.vvv(f"WSL put_file: {in_path} -> {out_path}", host=self.distro)

        with open(in_path, "rb") as f:
            file_data = f.read()

        full_cmd = [
            self.wsl_exe, "-d", self.distro, "-u", self.wsl_user,
            "--", "sh", "-c", f"cat > {shlex.quote(out_path)}",
        ]
        proc = subprocess.Popen(full_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = proc.communicate(file_data)
        if proc.returncode != 0:
            raise AnsibleError(f"Failed to put file to {self.distro}:{out_path}: {stderr.decode()}")

    def fetch_file(self, in_path, out_path):
        super().fetch_file(in_path, out_path)
        self._connect()

        self._display.vvv(f"WSL fetch_file: {in_path} -> {out_path}", host=self.distro)

        full_cmd = [
            self.wsl_exe, "-d", self.distro, "-u", self.wsl_user,
            "--", "cat", shlex.quote(in_path),
        ]
        proc = subprocess.Popen(full_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            raise AnsibleError(f"Failed to fetch file from {self.distro}:{in_path}: {stderr.decode()}")

        with open(out_path, "wb") as f:
            f.write(stdout)

    def close(self):
        self._connected = False
