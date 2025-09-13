import sys
from pathlib import Path
from typing import Annotated, Never

import typer

from .. import ObsidianConfig, SettingsCreationMode, vault_templates
from .. import open_vault as open_vault_in_obsidian
from . import autocomplete, templates

app = typer.Typer(no_args_is_help=True)
app.add_typer(templates.app)


@app.command(name="ls")
def list_vaults(
    long: Annotated[bool, typer.Option("-l", help="Use a long listing format, including all data.")] = False,
) -> None:
    """
    Lists directories registered as Obsidian vaults.
    """
    obsidian_config = ObsidianConfig.load()
    vaults = list(obsidian_config.vaults.items())
    vaults.sort(key=lambda tup: tup[1].last_opened, reverse=True)
    if long:
        import tabulate

        typer.echo(
            tabulate.tabulate(
                (
                    (vault_id, vault.path, vault.last_opened.astimezone().strftime("%Y-%m-%d %H:%M:%S"))
                    for vault_id, vault in vaults
                ),
                headers=["ID", "Path", "Last Opened"],
            )
        )
    else:
        for _vault_id, vault in vaults:
            typer.echo(vault.path)


def _exit_with_error(message: str, exit_code: int = 1) -> Never:
    typer.echo(message, file=sys.stderr)
    exit(exit_code)


@app.command(name="open", no_args_is_help=True)
def open_vault(
    path: Annotated[
        Path,
        typer.Argument(
            help="The vault directory.",
            file_okay=False,
            exists=True,
            autocompletion=autocomplete.complete_vaults_and_local_dirs,
        ),
    ],
    file: Annotated[
        str | None,
        typer.Argument(
            help="Open this file within the vault. A relative path from the vault root.",
            autocompletion=autocomplete.complete_vault_file,
        ),
    ] = None,
) -> None:
    """
    Opens the given directory as an Obsidian vault, registering it if necessary.
    """
    vault_id = ObsidianConfig.load().ensure_path_is_vault(path)
    open_vault_in_obsidian(vault_id, file)


@app.command(name="rm")
def remove_vault(
    path_or_id: Annotated[
        str, typer.Argument(help="The path to the vault, or the vault ID.", autocompletion=autocomplete.complete_vaults)
    ],
) -> None:
    """
    Unregisters the given vault from Obsidian. This does not remove the actual directory.
    """
    obsidian_config = ObsidianConfig.load()
    vault_id = (
        path_or_id if path_or_id in obsidian_config.vaults else obsidian_config.find_vault_id_by_path(Path(path_or_id))
    )
    if vault_id is None:
        _exit_with_error("The given path or id does not belong to a registered Obsidian vault.")
    obsidian_config.vaults.pop(vault_id)
    obsidian_config.save()


@app.command(name="new", no_args_is_help=True)
def new_vault(
    path: Annotated[Path, typer.Argument(help="The path of the root directory of the new vault.", file_okay=False)],
    template: Annotated[
        str,
        typer.Option(
            help="The name of the template to use when creating the vault. Defaults to the 'default' template.",
            autocompletion=vault_templates.get_all_templates,
        ),
    ] = vault_templates.DEFAULT_VAULT_TEMPLATE,
    allow_non_empty: Annotated[
        bool, typer.Option("--allow-non-empty", help="Allow creating the vault in a non-empty directory.")
    ] = False,
    should_open_vault: Annotated[
        bool, typer.Option("--open/--no-open", help="Whether to open the new vault in Obsidian upon creation.")
    ] = True,
    settings_creation_mode: Annotated[SettingsCreationMode, typer.Option()] = SettingsCreationMode.hardlink,
) -> None:
    """
    Creates a new Obsidian vault at the given path.
    """

    if path.exists():
        if not path.is_dir():
            _exit_with_error("Path must be non-existent or of an empty directory, but a file path was provided.")
        if not allow_non_empty:
            try:
                next(path.iterdir())
            except StopIteration:
                pass
            else:
                _exit_with_error(
                    "A directory already exists at this path and isn't empty. Are you sure this is the right path?\n"
                    "If this is intended, run again with --allow-non-empty."
                )
    elif path.parent.exists():
        path.mkdir()
    else:
        _exit_with_error(f"Can't create vault within non-existent parent directory '{path.parent}'")

    vault_templates.create_vault(path, template, settings_creation_mode)
    if should_open_vault:
        open_vault(path)


if __name__ == "__main__":
    app()
