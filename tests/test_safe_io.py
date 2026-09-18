import os
import zipfile

import pytest

from fcn_3DPrinting import safe_io


def test_atomic_write_keeps_old_file_when_replace_fails(tmp_path, monkeypatch):
    target = tmp_path / "db.csv"
    safe_io.atomic_write_csv(str(target), ["a"], [[1]])
    assert target.read_bytes() == b"a\r\n1\r\n"

    def boom(src, dst):
        raise OSError("disk full")
    monkeypatch.setattr(safe_io.os, "replace", boom)
    with pytest.raises(OSError):
        safe_io.atomic_write_csv(str(target), ["a"], [[2]])
    assert target.read_bytes() == b"a\r\n1\r\n"
    assert not [p for p in os.listdir(tmp_path) if p.endswith(".tmp")]


def test_rotate_backups_keeps_newest_first(tmp_path):
    target = str(tmp_path / "db.json")
    for content in ("A", "B", "C"):
        safe_io.rotate_backups(target, keep=2)
        safe_io.atomic_write_text(target, content)
    assert open(target).read() == "C"
    assert open(target + ".bak1").read() == "B"
    assert open(target + ".bak2").read() == "A"
    assert not os.path.exists(target + ".bak3")


def test_read_json_safe_returns_default_on_missing_or_corrupt(tmp_path):
    missing = str(tmp_path / "nope.json")
    assert safe_io.read_json_safe(missing, {"d": 1}) == {"d": 1}
    corrupt = tmp_path / "bad.json"
    corrupt.write_text("{not json")
    assert safe_io.read_json_safe(str(corrupt), []) == []


def test_safe_extract_zip_rejects_traversal_and_flattens(tmp_path):
    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("../evil.txt", "x")
        zf.writestr("filaments_3d_db.csv", "a")
    dest = tmp_path / "dest"
    dest.mkdir()
    with pytest.raises(ValueError):
        safe_io.safe_extract_zip(str(bad), str(dest), {"filaments_3d_db.csv"})
    assert not (dest / "filaments_3d_db.csv").exists()
    assert not (tmp_path / "evil.txt").exists()

    good = tmp_path / "good.zip"
    with zipfile.ZipFile(good, "w") as zf:
        zf.writestr("folder/filaments_3d_db.csv", "a")
        zf.writestr("readme.txt", "ignored")
    extracted = safe_io.safe_extract_zip(str(good), str(dest), {"filaments_3d_db.csv"})
    assert extracted == ["filaments_3d_db.csv"]
    assert (dest / "filaments_3d_db.csv").read_text() == "a"
    assert not (dest / "readme.txt").exists()

    only_junk = tmp_path / "junk.zip"
    with zipfile.ZipFile(only_junk, "w") as zf:
        zf.writestr("readme.txt", "x")
    with pytest.raises(ValueError):
        safe_io.safe_extract_zip(str(only_junk), str(dest), {"filaments_3d_db.csv"})


def test_snapshot_database_zips_existing_files_and_prunes(db_dir):
    from fcn_3DPrinting.db_paths import get_3dp_db_file, get_backup_dir
    assert safe_io.snapshot_database("nothing yet") is None
    safe_io.atomic_write_text(get_3dp_db_file("materials"), "m")
    safe_io.atomic_write_text(get_3dp_db_file("mix_red"), "{}")
    paths = [safe_io.snapshot_database("import zip", keep=2) for _ in range(3)]
    assert all(p and os.path.exists(p) for p in paths[1:])
    with zipfile.ZipFile(paths[-1]) as zf:
        assert sorted(zf.namelist()) == ["filaments_3d_db.csv", "filaments_mix_red_db.json"]
    remaining = [f for f in os.listdir(get_backup_dir()) if f.startswith("pre_")]
    assert len(remaining) == 2 and all(f.startswith("pre_import_zip_") for f in remaining)
