import json
from types import SimpleNamespace

from src import docker_update


def result(returncode=0, stdout="", stderr=""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def test_runtime_options_preserve_security_and_resource_settings():
    info = {
        "Config": {
            "User": "1000:1000",
            "WorkingDir": "/app",
            "Env": ["A=1"],
            "Labels": {"example": "yes"},
            "StopSignal": "SIGTERM",
        },
        "HostConfig": {
            "RestartPolicy": {"Name": "unless-stopped", "MaximumRetryCount": 0},
            "NetworkMode": "backend",
            "Binds": ["/host/data:/data:ro"],
            "PortBindings": {"8080/tcp": [{"HostIp": "127.0.0.1", "HostPort": "18080"}]},
            "CapAdd": ["NET_ADMIN"],
            "CapDrop": ["MKNOD"],
            "ReadonlyRootfs": True,
            "Devices": [{"PathOnHost": "/dev/fuse", "PathInContainer": "/dev/fuse", "CgroupPermissions": "rwm"}],
            "Dns": ["1.1.1.1"],
            "ExtraHosts": ["db:10.0.0.2"],
            "SecurityOpt": ["no-new-privileges"],
            "Sysctls": {"net.ipv4.ip_forward": "1"},
            "Memory": 536870912,
            "NanoCpus": 1500000000,
            "PidsLimit": 128,
            "LogConfig": {"Type": "local", "Config": {"max-size": "10m"}},
        },
        "Mounts": [],
    }

    cmd = ["docker", "run", "--detach", "--name", "demo"]
    docker_update._append_runtime_options(cmd, info)

    expected = [
        ("--restart", "unless-stopped"),
        ("--network", "backend"),
        ("--user", "1000:1000"),
        ("--workdir", "/app"),
        ("-e", "A=1"),
        ("-v", "/host/data:/data:ro"),
        ("-p", "127.0.0.1:18080:8080/tcp"),
        ("-l", "example=yes"),
        ("--cap-add", "NET_ADMIN"),
        ("--cap-drop", "MKNOD"),
        ("--device", "/dev/fuse:/dev/fuse:rwm"),
        ("--dns", "1.1.1.1"),
        ("--add-host", "db:10.0.0.2"),
        ("--security-opt", "no-new-privileges"),
        ("--sysctl", "net.ipv4.ip_forward=1"),
        ("--memory", "536870912"),
        ("--cpus", "1.5"),
        ("--pids-limit", "128"),
        ("--log-driver", "local"),
        ("--log-opt", "max-size=10m"),
        ("--stop-signal", "SIGTERM"),
    ]
    for flag, value in expected:
        i = cmd.index(flag)
        assert cmd[i + 1] == value
    assert "--read-only" in cmd


def test_recreate_rolls_back_when_new_container_fails(monkeypatch):
    cid = "1234567890abcdef"
    name = "demo"
    backup = f"{name}.idempotent-backup-{cid[:12]}"
    info = {
        "Config": {"Env": [], "Labels": {}, "Entrypoint": ["/entrypoint"], "Cmd": ["serve"]},
        "HostConfig": {"RestartPolicy": {"Name": "no"}, "Binds": [], "PortBindings": {}},
        "Mounts": [],
    }
    calls = []

    def fake_run(cmd, *args, **kwargs):
        calls.append(cmd)
        if cmd == ["docker", "inspect", cid]:
            return result(stdout=json.dumps([info]))
        if cmd == ["docker", "run", "--detach", "--name", name, "--entrypoint", "/entrypoint", "example:latest", "serve"]:
            return result(returncode=1, stderr="boom")
        return result()

    monkeypatch.setattr(docker_update.subprocess, "run", fake_run)

    assert docker_update._recreate_container(cid, "example:latest", name) is False
    assert ["docker", "stop", cid] in calls
    assert ["docker", "rename", cid, backup] in calls
    assert ["docker", "rm", "-f", name] in calls
    assert ["docker", "rename", backup, name] in calls
    assert ["docker", "start", name] in calls


def test_recreate_removes_backup_only_after_replacement_is_running(monkeypatch):
    cid = "abcdef1234567890"
    name = "demo"
    backup = f"{name}.idempotent-backup-{cid[:12]}"
    info = {
        "Config": {"Env": [], "Labels": {}, "Entrypoint": [], "Cmd": []},
        "HostConfig": {"RestartPolicy": {"Name": "no"}, "Binds": [], "PortBindings": {}},
        "Mounts": [],
    }
    calls = []

    def fake_run(cmd, *args, **kwargs):
        calls.append(cmd)
        if cmd == ["docker", "inspect", cid]:
            return result(stdout=json.dumps([info]))
        if cmd == ["docker", "inspect", "--format={{.State.Running}}", name]:
            return result(stdout="true\n")
        return result()

    monkeypatch.setattr(docker_update.subprocess, "run", fake_run)

    assert docker_update._recreate_container(cid, "example:latest", name) is True
    assert calls.index(["docker", "inspect", "--format={{.State.Running}}", name]) < calls.index(["docker", "rm", backup])
