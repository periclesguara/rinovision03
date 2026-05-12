from scripts.rinovision_healthcheck import run_healthcheck


def test_healthcheck_runs_without_exposing_secrets():
    report = run_healthcheck()
    text = str(report)
    assert "env_file_exists" in report
    assert "OPENAI_API_KEY=" not in text
    assert "sk-" not in text
    assert report["rinovision_import"]["ok"] is True
