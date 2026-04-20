from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

_SNOWFLAKE_REQUIRED = {"account", "user", "password", "warehouse", "database", "schema"}

_REQUIRED_BY_TYPE: dict[str, set[str]] = {
    "snowflake": _SNOWFLAKE_REQUIRED,
}


class CredentialsValidationError(Exception):
    pass


def _load_file(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise CredentialsValidationError(f"Credentials file not found: {path}")
    with p.open() as f:
        if p.suffix in {".yaml", ".yml"}:
            return yaml.safe_load(f)
        return json.load(f)


def _validate(creds: dict, connector_type: str) -> dict:
    if creds.get("type") and creds["type"] != connector_type:
        raise CredentialsValidationError(
            f"Credentials type mismatch: file says '{creds['type']}', "
            f"connector expects '{connector_type}'"
        )
    required = _REQUIRED_BY_TYPE.get(connector_type, set())
    for field in required:
        if not creds.get(field):
            raise CredentialsValidationError(
                f"Credentials missing required field: '{field}' for connector '{connector_type}'"
            )
    return creds


def load_credentials(
    connector_type: str,
    credentials_path: str | None = None,
) -> dict:
    """Resolve credentials using priority order:
    1. credentials_path argument (from --credentials CLI flag)
    2. GUIDE_CREDENTIALS_FILE env var (path to file)
    3. Individual connector env vars (SF_ACCOUNT etc.)
    4. Raise CredentialsValidationError
    """
    if credentials_path:
        return _validate(_load_file(credentials_path), connector_type)

    env_file = os.environ.get("GUIDE_CREDENTIALS_FILE")
    if env_file:
        return _validate(_load_file(env_file), connector_type)

    if connector_type == "snowflake":
        keys = ["SF_ACCOUNT", "SF_USER", "SF_PASSWORD", "SF_WAREHOUSE", "SF_DATABASE", "SF_SCHEMA"]
        env_vals = {k: os.environ.get(k) for k in keys}
        present = {k for k, v in env_vals.items() if v}
        if present == set(keys):
            return {
                "type": "snowflake",
                "account": env_vals["SF_ACCOUNT"],
                "user": env_vals["SF_USER"],
                "password": env_vals["SF_PASSWORD"],
                "warehouse": env_vals["SF_WAREHOUSE"],
                "database": env_vals["SF_DATABASE"],
                "schema": env_vals["SF_SCHEMA"],
            }
        if present:
            missing = sorted(set(keys) - present)
            raise CredentialsValidationError(
                f"Credentials missing required field: {missing} not set for connector 'snowflake'"
            )

    raise CredentialsValidationError(
        f"No credentials found for connector '{connector_type}'. "
        "Provide --credentials <file>, set GUIDE_CREDENTIALS_FILE, "
        "or set connector-specific env vars."
    )
