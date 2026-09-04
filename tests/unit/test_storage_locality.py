from __future__ import annotations

from pathlib import Path

import pytest

from athena.storage.locality import ActiveStateLocalityError, assert_active_state_root_local


def test_windows_unc_active_state_is_rejected_without_drive_probe() -> None:
    probes: list[str] = []

    with pytest.raises(ActiveStateLocalityError, match="UNC/network path"):
        assert_active_state_root_local(
            Path(r"\\server\share\ATHENA\state"),
            _platform_name="nt",
            _windows_drive_type_fn=lambda root: probes.append(root) or 3,
        )

    assert probes == []


def test_windows_mapped_network_drive_is_rejected() -> None:
    with pytest.raises(ActiveStateLocalityError, match="mapped network drive"):
        assert_active_state_root_local(
            Path(r"Z:\ATHENA\state"),
            _platform_name="nt",
            _windows_drive_type_fn=lambda _root: 4,
        )


def test_windows_fixed_drive_is_allowed() -> None:
    assert_active_state_root_local(
        Path(r"C:\ATHENA\state"),
        _platform_name="nt",
        _windows_drive_type_fn=lambda _root: 3,
    )


@pytest.mark.parametrize("drive_type", [0, 1])
def test_windows_unverifiable_drive_is_rejected(drive_type: int) -> None:
    with pytest.raises(ActiveStateLocalityError, match="could not verify"):
        assert_active_state_root_local(
            Path(r"C:\ATHENA\state"),
            _platform_name="nt",
            _windows_drive_type_fn=lambda _root: drive_type,
        )


def test_linux_nfs_mount_is_rejected() -> None:
    mountinfo = "36 25 0:32 / / rw,relatime - ext4 /dev/root rw\n37 36 0:44 / /mnt/shared rw - nfs4 server:/data rw\n"

    with pytest.raises(ActiveStateLocalityError, match=r"network filesystem \(nfs4\)"):
        assert_active_state_root_local(
            Path("/mnt/shared/ATHENA/state"),
            _platform_name="posix",
            _linux_mountinfo_text=mountinfo,
        )


def test_linux_longest_mount_match_allows_local_nested_mount() -> None:
    mountinfo = "36 25 0:32 / / rw - ext4 /dev/root rw\n37 36 0:44 / /mnt rw - nfs server:/mnt rw\n38 37 8:2 / /mnt/local rw - ext4 /dev/sdb2 rw\n"

    assert_active_state_root_local(
        Path("/mnt/local/ATHENA/state"),
        _platform_name="posix",
        _linux_mountinfo_text=mountinfo,
    )


def test_linux_mountinfo_escaped_space_is_matched() -> None:
    mountinfo = "36 25 0:32 / / rw - ext4 /dev/root rw\n37 36 0:44 / /mnt/network\\040share rw - cifs //server/share rw\n"

    with pytest.raises(ActiveStateLocalityError, match=r"network filesystem \(cifs\)"):
        assert_active_state_root_local(
            Path("/mnt/network share/ATHENA/state"),
            _platform_name="posix",
            _linux_mountinfo_text=mountinfo,
        )
