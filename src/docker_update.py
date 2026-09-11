import json
import logging
import subprocess
import time
from pathlib import Path

from .config import Config

log = logging.getLogger(__name__)


def run_update(cfg: Config) -> tuple[str, list[str]]:
    before = _ps_snapshot()

    updated_containers: list[str] = []
    if cfg.compose_file:
        updated_containers = _compose_update(cfg)
    else:
        updated_containers = _socket_update(cfg)

    after = _ps_snapshot()
    changes = _diff(before, after)

    if changes and not cfg.dry_run:
        log.info("Changes detected, pruning...")
        subprocess.run(
            ["docker", "container", "prune", "-f"], capture_output=True, check=False
        )
        subprocess.run(
            ["docker", "image", "prune", "-f"], capture_output=True, check=False
        )

    return changes, updated_containers


def _ps_snapshot() -> list[str]:
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}} {{.Image}} {{.ImageID}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"docker ps failed: {result.stderr.strip()}")
    return sorted(result.stdout.splitlines())


def _compose_update(cfg: Config) -> list[str]:
    compose_dir = str(Path(cfg.compose_file).parent)
    base_cmd = ["docker", "compose", "-f", cfg.compose_file]
    if cfg.compose_env_file and Path(cfg.compose_env_file).exists():
        base_cmd += ["--env-file", cfg.compose_env_file]
        log.info("Using env file: %s", cfg.compose_env_file)

    if cfg.dry_run:
        log.info(
            "[dry-run] would run: docker compose pull (sequential) && up -d --remove-orphans"
        )
        return []

    result = subprocess.run(
        base_cmd + ["config", "--services"],
        capture_output=True,
        text=True,
        check=True,
        cwd=compose_dir,
    )
    services = result.stdout.splitlines()

    before_images = _compose_image_snapshot(base_cmd, compose_dir)

    for svc in services:
        for attempt in range(1, 4):
            try:
                subprocess.run(base_cmd + ["pull", svc], check=True, cwd=compose_dir)
                break
            except subprocess.CalledProcessError:
                if attempt < 3:
                    time.sleep(attempt * 5)
                else:
                    log.warning("Failed to pull %s after 3 attempts", svc)

    subprocess.run(
        base_cmd + ["up", "-d", "--remove-orphans"], check=True, cwd=compose_dir
    )

    after_images = _compose_image_snapshot(base_cmd, compose_dir)
    return [svc for svc in services if after_images.get(svc) != before_images.get(svc)]


def _compose_image_snapshot(base_cmd: list[str], compose_dir: str) -> dict[str, str]:
    result = subprocess.run(
        base_cmd + ["images", "--format", "{{.Service}}\t{{.ID}}"],
        capture_output=True,
        text=True,
        cwd=compose_dir,
        check=False,
    )
    snapshot: dict[str, str] = {}
    for line in result.stdout.splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2:
            snapshot[parts[0].strip()] = parts[1].strip()
    return snapshot


def _socket_update(cfg: Config) -> list[str]:
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Image}}"],
        capture_output=True,
        text=True,
        check=True,
    )
    images = sorted(set(result.stdout.splitlines()))

    if cfg.dry_run:
        log.info("[dry-run] would pull images: %s", " ".join(images))
        return []

    for image in images:
        r = subprocess.run(["docker", "pull", image], capture_output=True, check=False)
        if r.returncode != 0:
            log.warning("Failed to pull image: %s", image)

    updated: list[str] = []
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.ID}} {{.Image}}"],
        capture_output=True,
        text=True,
        check=True,
    )
    for line in result.stdout.splitlines():
        cid, image = line.split(None, 1)
        running = subprocess.run(
            ["docker", "inspect", "--format={{.Image}}", cid],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        latest = subprocess.run(
            ["docker", "inspect", "--format={{.Id}}", image],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        if latest and running != latest:
            name = (
                subprocess.run(
                    ["docker", "inspect", "--format={{.Name}}", cid],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                .stdout.strip()
                .lstrip("/")
            )
            if _recreate_container(cid, image, name):
                log.info("Recreated: %s", name)
                updated.append(name)
            else:
                log.warning("Failed to recreate: %s", name)

    return updated


def _append_runtime_options(cmd: list[str], info: dict) -> list[str]:
    """Append inspect-derived options needed to faithfully recreate a container."""
    hc = info.get("HostConfig") or {}
    container_cfg = info.get("Config") or {}

    rp = hc.get("RestartPolicy") or {}
    rp_name = rp.get("Name") or "no"
    if rp_name and rp_name != "no":
        retries = rp.get("MaximumRetryCount") or 0
        if rp_name == "on-failure" and retries:
            cmd += ["--restart", f"on-failure:{retries}"]
        else:
            cmd += ["--restart", rp_name]

    nm = hc.get("NetworkMode") or ""
    if nm and nm not in ("default", "bridge"):
        cmd += ["--network", nm]

    if container_cfg.get("User"):
        cmd += ["--user", str(container_cfg["User"])]
    if container_cfg.get("WorkingDir"):
        cmd += ["--workdir", str(container_cfg["WorkingDir"])]

    for env_var in container_cfg.get("Env") or []:
        cmd += ["-e", env_var]

    bind_targets: set[str] = set()
    for bind in hc.get("Binds") or []:
        cmd += ["-v", bind]
        parts = bind.split(":")
        if len(parts) >= 2:
            bind_targets.add(parts[1])

    for mount in info.get("Mounts") or []:
        mount_type = mount.get("Type")
        target = mount.get("Destination")
        source = mount.get("Name") or mount.get("Source")
        if not target or target in bind_targets or mount_type not in ("volume", "tmpfs"):
            continue
        if mount_type == "volume" and source:
            spec = f"{source}:{target}"
            if not mount.get("RW", True):
                spec += ":ro"
            cmd += ["-v", spec]
        elif mount_type == "tmpfs":
            cmd += ["--tmpfs", target]

    for cport, bindings in (hc.get("PortBindings") or {}).items():
        for b in bindings or []:
            hip = b.get("HostIp", "")
            hport = b.get("HostPort", "")
            cmd += ["-p", (f"{hip}:{hport}:{cport}" if hip else f"{hport}:{cport}")]

    for k, v in (container_cfg.get("Labels") or {}).items():
        cmd += ["-l", f"{k}={v}"]

    for cap in hc.get("CapAdd") or []:
        cmd += ["--cap-add", cap]
    for cap in hc.get("CapDrop") or []:
        cmd += ["--cap-drop", cap]
    if hc.get("Privileged"):
        cmd.append("--privileged")
    if hc.get("ReadonlyRootfs"):
        cmd.append("--read-only")
    if hc.get("Init"):
        cmd.append("--init")

    for device in hc.get("Devices") or []:
        src = device.get("PathOnHost")
        dst = device.get("PathInContainer")
        perms = device.get("CgroupPermissions") or "rwm"
        if src and dst:
            cmd += ["--device", f"{src}:{dst}:{perms}"]

    for dns in hc.get("Dns") or []:
        cmd += ["--dns", dns]
    for dns_search in hc.get("DnsSearch") or []:
        cmd += ["--dns-search", dns_search]
    for host in hc.get("ExtraHosts") or []:
        cmd += ["--add-host", host]
    for security_opt in hc.get("SecurityOpt") or []:
        cmd += ["--security-opt", security_opt]
    for key, value in (hc.get("Sysctls") or {}).items():
        cmd += ["--sysctl", f"{key}={value}"]
    for target, options in (hc.get("Tmpfs") or {}).items():
        spec = target if not options else f"{target}:{options}"
        cmd += ["--tmpfs", spec]

    memory = hc.get("Memory") or 0
    if memory > 0:
        cmd += ["--memory", str(memory)]
    nano_cpus = hc.get("NanoCpus") or 0
    if nano_cpus > 0:
        cmd += ["--cpus", str(nano_cpus / 1_000_000_000)]
    cpu_shares = hc.get("CpuShares") or 0
    if cpu_shares > 0:
        cmd += ["--cpu-shares", str(cpu_shares)]
    pids_limit = hc.get("PidsLimit")
    if isinstance(pids_limit, int) and pids_limit > 0:
        cmd += ["--pids-limit", str(pids_limit)]
    shm_size = hc.get("ShmSize") or 0
    if shm_size and shm_size != 64 * 1024 * 1024:
        cmd += ["--shm-size", str(shm_size)]

    log_cfg = hc.get("LogConfig") or {}
    if log_cfg.get("Type") and log_cfg["Type"] != "json-file":
        cmd += ["--log-driver", log_cfg["Type"]]
    for key, value in (log_cfg.get("Config") or {}).items():
        cmd += ["--log-opt", f"{key}={value}"]

    if container_cfg.get("StopSignal"):
        cmd += ["--stop-signal", container_cfg["StopSignal"]]

    return cmd


def _append_process_config(cmd: list[str], info: dict) -> list[str]:
    """Append the inspected entrypoint and command after the image name."""
    container_cfg = info.get("Config") or {}
    entrypoint = container_cfg.get("Entrypoint") or []
    original_cmd = container_cfg.get("Cmd") or []

    if isinstance(entrypoint, str):
        entrypoint = [entrypoint]
    if isinstance(original_cmd, str):
        original_cmd = [original_cmd]

    if entrypoint:
        cmd[1:1] = ["--entrypoint", str(entrypoint[0])]
        cmd.extend(str(item) for item in entrypoint[1:])
    cmd.extend(str(item) for item in original_cmd)
    return cmd


def _restore_original(name: str, backup_name: str) -> None:
    """Best-effort rollback to the stopped original container."""
    subprocess.run(["docker", "rm", "-f", name], capture_output=True, check=False)
    renamed = subprocess.run(
        ["docker", "rename", backup_name, name], capture_output=True, text=True, check=False
    )
    if renamed.returncode != 0:
        log.error("Rollback could not restore container name %s: %s", name, renamed.stderr.strip())
        return
    started = subprocess.run(
        ["docker", "start", name], capture_output=True, text=True, check=False
    )
    if started.returncode != 0:
        log.error("Rollback could not restart %s: %s", name, started.stderr.strip())


def _recreate_container(cid: str, image: str, name: str) -> bool:
    result = subprocess.run(
        ["docker", "inspect", cid], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        return False
    try:
        info = json.loads(result.stdout)[0]
    except (ValueError, IndexError):
        return False

    backup_name = f"{name}.idempotent-backup-{cid[:12]}"
    cmd = ["docker", "run", "--detach", "--name", name]
    _append_runtime_options(cmd, info)

    container_cfg = info.get("Config") or {}
    entrypoint = container_cfg.get("Entrypoint") or []
    if isinstance(entrypoint, str):
        entrypoint = [entrypoint]
    if entrypoint:
        cmd += ["--entrypoint", str(entrypoint[0])]

    cmd.append(image)
    if entrypoint:
        cmd.extend(str(item) for item in entrypoint[1:])
    original_cmd = container_cfg.get("Cmd") or []
    if isinstance(original_cmd, str):
        original_cmd = [original_cmd]
    cmd.extend(str(item) for item in original_cmd)

    stopped = subprocess.run(
        ["docker", "stop", cid], capture_output=True, text=True, check=False
    )
    if stopped.returncode != 0:
        log.error("Failed to stop %s: %s", name, stopped.stderr.strip())
        return False

    renamed = subprocess.run(
        ["docker", "rename", cid, backup_name], capture_output=True, text=True, check=False
    )
    if renamed.returncode != 0:
        log.error("Failed to reserve rollback container for %s: %s", name, renamed.stderr.strip())
        subprocess.run(["docker", "start", cid], capture_output=True, check=False)
        return False

    created = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if created.returncode != 0:
        log.error("Failed to recreate %s: %s; restoring original", name, created.stderr.strip())
        _restore_original(name, backup_name)
        return False

    running = subprocess.run(
        ["docker", "inspect", "--format={{.State.Running}}", name],
        capture_output=True,
        text=True,
        check=False,
    )
    if running.returncode != 0 or running.stdout.strip().lower() != "true":
        log.error("Replacement %s did not remain running; restoring original", name)
        _restore_original(name, backup_name)
        return False

    removed = subprocess.run(
        ["docker", "rm", backup_name], capture_output=True, text=True, check=False
    )
    if removed.returncode != 0:
        log.warning("Replacement is running but rollback container %s could not be removed: %s", backup_name, removed.stderr.strip())

    return True


def _diff(before: list[str], after: list[str]) -> str:
    before_set = set(before)
    after_set = set(after)
    lines = [f"< {line}" for line in sorted(before_set - after_set)] + [
        f"> {line}" for line in sorted(after_set - before_set)
    ]
    return "\n".join(lines)
