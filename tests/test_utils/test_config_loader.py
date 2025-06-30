# tests/test_utils/test_config_loader.py

import os
import pytest
from pseudo_struct.utils.config_loader import load_config

def test_default_config(monkeypatch):
    monkeypatch.delenv("PS_ENV", raising=False)
    config = load_config()
    assert "logging" in config
    assert config["logging"]["level"] == "INFO"

def test_education_env(monkeypatch):
    monkeypatch.setenv("PS_ENV", "education")
    config = load_config()
    assert config["logging"]["level"] == "DEBUG"
    # 예: deep merge가 잘 되었는지 format 등도 추가로 검사

def test_nonexistent_env(monkeypatch):
    monkeypatch.setenv("PS_ENV", "nonexistent")
    config = load_config()
    assert "logging" in config  # default fallback 확인

def test_config_file_not_found(tmp_path, monkeypatch):
    # 임시 폴더에 config 파일 없음
    monkeypatch.setenv("PS_ENV", "default")
    from pseudo_struct.utils.config_loader import load_config
    with pytest.raises(FileNotFoundError):
        load_config(config_file="not_exist_config.yml")
