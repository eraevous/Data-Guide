import json
import os
import pytest
from pathlib import Path
from connectors.credentials import CredentialsValidationError, load_credentials


def test_load_from_file(tmp_path):
    creds_file = tmp_path / "sf.credentials.json"
    creds_file.write_text(json.dumps({
        "type": "snowflake",
        "account": "myaccount",
        "user": "myuser",
        "password": "secret",
        "warehouse": "WH",
        "database": "DB",
        "schema": "PUBLIC",
    }))
    result = load_credentials("snowflake", credentials_path=str(creds_file))
    assert result["account"] == "myaccount"
    assert result["type"] == "snowflake"


def test_load_from_env_vars(monkeypatch):
    monkeypatch.setenv("SF_ACCOUNT", "envaccount")
    monkeypatch.setenv("SF_USER", "envuser")
    monkeypatch.setenv("SF_PASSWORD", "envpass")
    monkeypatch.setenv("SF_WAREHOUSE", "WH")
    monkeypatch.setenv("SF_DATABASE", "DB")
    monkeypatch.setenv("SF_SCHEMA", "PUBLIC")
    result = load_credentials("snowflake")
    assert result["account"] == "envaccount"


def test_load_from_guide_credentials_file_env(tmp_path, monkeypatch):
    creds_file = tmp_path / "sf.credentials.json"
    creds_file.write_text(json.dumps({
        "type": "snowflake",
        "account": "fileenvaccount",
        "user": "u",
        "password": "p",
        "warehouse": "W",
        "database": "D",
        "schema": "S",
    }))
    monkeypatch.setenv("GUIDE_CREDENTIALS_FILE", str(creds_file))
    result = load_credentials("snowflake")
    assert result["account"] == "fileenvaccount"


def test_wrong_type_raises(tmp_path):
    creds_file = tmp_path / "bad.credentials.json"
    creds_file.write_text(json.dumps({"type": "csv"}))
    with pytest.raises(CredentialsValidationError, match="type mismatch"):
        load_credentials("snowflake", credentials_path=str(creds_file))


def test_missing_required_field_raises(tmp_path):
    creds_file = tmp_path / "incomplete.credentials.json"
    creds_file.write_text(json.dumps({
        "type": "snowflake",
        "account": "a",
        # missing user, password, warehouse, database, schema
    }))
    with pytest.raises(CredentialsValidationError, match="missing required field"):
        load_credentials("snowflake", credentials_path=str(creds_file))


def test_no_credentials_raises(monkeypatch):
    monkeypatch.delenv("GUIDE_CREDENTIALS_FILE", raising=False)
    for key in ["SF_ACCOUNT", "SF_USER", "SF_PASSWORD", "SF_WAREHOUSE", "SF_DATABASE", "SF_SCHEMA"]:
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(CredentialsValidationError, match="No credentials"):
        load_credentials("snowflake")
