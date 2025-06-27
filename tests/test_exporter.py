from pathlib import Path
from core.db import init_db
from core.exporter import export_data


def test_export_json(tmp_path):
    init_db()
    path = tmp_path / "out.json"
    res = export_data("json", path, limit=0)
    assert path.exists()
    assert res == path


def test_export_csv(tmp_path):
    init_db()
    path = tmp_path / "out.csv"
    res = export_data("csv", path, limit=0)
    assert path.exists()
    text = path.read_text()
    assert "mac_address" in text


def test_export_sqlite(tmp_path):
    init_db()
    path = tmp_path / "out.sqlite"
    res = export_data("sqlite", path)
    assert path.exists()
    assert path.stat().st_size > 0
