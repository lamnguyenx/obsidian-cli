import os
import secrets
import subprocess
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Annotated, Self

import platformdirs
from pydantic import BaseModel, Field, PlainSerializer

OBSIDIAN_CONFIG_DIR = Path(platformdirs.user_config_dir("obsidian", appauthor=False, roaming=True))
OBSIDIAN_CONFIG_FILE = OBSIDIAN_CONFIG_DIR / "obsidian.json"

IntDatetime = Annotated[datetime, PlainSerializer(lambda dt: int(dt.timestamp() * 1000), return_type=int)]


class Vault(BaseModel, extra="allow"):
    path: Path
    date_added: IntDatetime = Field(alias="ts")
    open: bool = False

    @staticmethod
    def generate_id() -> str:
        return secrets.token_hex(8)


class ObsidianConfig(BaseModel, extra="allow"):
    vaults: dict[str, Vault] = {}
    """A mapping from vault id to vault."""

    @classmethod
    def load(cls) -> Self:
        if not OBSIDIAN_CONFIG_FILE.exists():
            return cls()
        return cls.model_validate_json(OBSIDIAN_CONFIG_FILE.read_text("UTF8"))

    def save(self) -> None:
        OBSIDIAN_CONFIG_DIR.mkdir(exist_ok=True, parents=True)
        OBSIDIAN_CONFIG_FILE.write_text(self.model_dump_json(by_alias=True, exclude_defaults=True), encoding="UTF8")

    def find_vault_id_by_path(self, path: Path) -> str | None:
        """Returns the id of the vault with the given path, or None if not found."""
        for vault_id, vault in self.vaults.items():
            if vault.path == path:
                return vault_id
        return None


def _open_url(url: str) -> None:
    match os_platform := sys.platform:
        case "linux":
            subprocess.run(["xdg-open", url])
        case "win32":
            os.system(f'start "" "{url}"')
        case "darwin":
            subprocess.run(["open", url])
        case _:
            raise RuntimeError(f"Unsupported OS: {os_platform}")


def open_vault(vault_id: str, file: str | None = None) -> None:
    """
    Launches Obsidian with the given vault.

    See: https://help.obsidian.md/Extending+Obsidian/Obsidian+URI

    :vault_id: The 16-character hex id of the vault.
    :file: Optionally, a path from the vault root to a file to be opened. The .md extension may be omitted.
    """

    query_params = {"vault": vault_id}
    if file:
        query_params["file"] = file
    _open_url("obsidian://open?" + urllib.parse.urlencode(query_params))
