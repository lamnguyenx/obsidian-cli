from datetime import UTC, datetime
from pathlib import Path

import typer

from .. import ObsidianConfig, Vault
from .. import open_vault as open_vault_in_obsidian

app = typer.Typer(no_args_is_help=True)


@app.command(name="ls")
def list_vaults() -> None:
    """
    Lists directories registered as Obsidian vaults.
    """
    obsidian_config = ObsidianConfig.load()
    for vault in obsidian_config.vaults.values():
        print(vault.path)


@app.command(name="open")
def open_vault(path: Path) -> None:
    """
    Opens the given directory as an Obsidian vault, registering it if necessary.
    """
    obsidian_config = ObsidianConfig.load()
    vault_id = obsidian_config.find_vault_id_by_path(path)
    if vault_id is None:
        local_time_now = datetime.now(tz=UTC).astimezone()
        vault_id = Vault.generate_id()
        obsidian_config.vaults[vault_id] = Vault(path=path, ts=local_time_now)
        obsidian_config.save()
    open_vault_in_obsidian(vault_id)


if __name__ == "__main__":
    app()
