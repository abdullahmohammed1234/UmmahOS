"""`.env` is loaded locally. Secrets must not override an already-set environment."""

from __future__ import annotations

from adapt.llm.config import load_dotenv, load_settings


def test_dotenv_loads_from_cwd(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    (tmp_path / ".env").write_text(
        "GEMINI_API_KEY=from-file\nGEMINI_MODEL=gemini-from-file\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    settings = load_settings()
    assert settings.api_key == "from-file"
    assert settings.model == "gemini-from-file"
    assert settings.credentials_present is True


def test_dotenv_does_not_override_existing_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "from-process")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-process")
    (tmp_path / ".env").write_text(
        "GEMINI_API_KEY=from-file\nGEMINI_MODEL=gemini-from-file\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    load_dotenv()
    settings = load_settings()
    assert settings.api_key == "from-process"
    assert settings.model == "gemini-process"


def test_nvidia_dotenv_loads_without_printing_secret(tmp_path, monkeypatch):
    from adapt.llm.config import load_nvidia_settings

    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("NVIDIA_MODEL", raising=False)
    (tmp_path / ".env").write_text(
        "NVIDIA_API_KEY=from-file\nNVIDIA_MODEL=meta/llama-3.3-70b-instruct\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    settings = load_nvidia_settings()
    assert settings.credentials_present is True
    assert settings.api_key == "from-file"
    assert settings.model == "meta/llama-3.3-70b-instruct"
