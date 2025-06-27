from typer.testing import CliRunner
from unittest.mock import patch

from cli.main import app


def test_aggregate_command():
    runner = CliRunner()
    with patch("cli.main.aggregator.aggregate") as mock_agg:
        mock_agg.return_value = [{"mac_address": "AA"}]
        result = runner.invoke(
            app, ["aggregate", "--endpoint", "url1", "--endpoint", "url2"]
        )
        assert result.exit_code == 0
        assert "AA" in result.output
        mock_agg.assert_called_once_with(["url1", "url2"])


def test_export_command(tmp_path):
    runner = CliRunner()
    out = tmp_path / "data.json"
    result = runner.invoke(app, ["export", "--format", "json", str(out), "--limit", "0"])
    assert result.exit_code == 0
    assert out.exists()
