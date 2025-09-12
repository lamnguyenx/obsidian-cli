import shlex
import sys
from pathlib import Path
from typing import Annotated, Never

import tabulate
import typer

from .. import DEFAULT_VAULT_TEMPLATE, ObsidianConfig, create_vault, get_all_templates
from .. import open_vault as open_vault_in_obsidian
from .templates import app as templates_app

app = typer.Typer(no_args_is_help=True)
app.add_typer(templates_app)


@app.command(name="ls")
def list_vaults(
    long: Annotated[bool, typer.Option("-l", help="Use a long listing format, including all data.")] = False,
) -> None:
    """
    Lists directories registered as Obsidian vaults.
    """
    obsidian_config = ObsidianConfig.load()
    vaults = list((vault_id, vault) for vault_id, vault in obsidian_config.vaults.items())
    vaults.sort(key=lambda tup: tup[1].last_opened, reverse=True)
    if long:
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


def _complete_vault(incomplete: str, include_local_files: bool) -> list[tuple[str, str]]:
    allow_dotfiles = incomplete.startswith(".")
    results: list[tuple[str, str]] = []
    if include_local_files:
        results.extend(
            (file.name, "")
            for file in Path().iterdir()
            if file.is_dir() and (allow_dotfiles or not file.name.startswith("."))
        )
    results.extend((str(vault.path), vault_id) for vault_id, vault in ObsidianConfig.load().vaults.items())
    incomplete = incomplete.casefold()
    for i in range(len(results) - 1, -1, -1):
        item = results[i]
        quoted_item = shlex.quote(item[0])
        if item[0].casefold().startswith(incomplete) or quoted_item.casefold().startswith(incomplete):
            results[i] = (quoted_item, item[1])
        else:
            results.pop(i)
    return results


def _complete_vaults(incomplete: str) -> list[tuple[str, str]]:
    return _complete_vault(incomplete, include_local_files=False)


def _complete_vaults_and_local_files(incomplete: str) -> list[tuple[str, str]]:
    return _complete_vault(incomplete, include_local_files=True)


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
            autocompletion=_complete_vaults_and_local_files,
        ),
    ],
) -> None:
    """
    Opens the given directory as an Obsidian vault, registering it if necessary.
    """
    vault_id = ObsidianConfig.load().ensure_path_is_vault(path)
    open_vault_in_obsidian(vault_id)


@app.command(name="rm")
def remove_vault(
    path_or_id: Annotated[
        str, typer.Argument(help="The path to the vault, or the vault ID.", autocompletion=_complete_vaults)
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
            autocompletion=get_all_templates,
        ),
    ] = DEFAULT_VAULT_TEMPLATE,
    allow_non_empty: Annotated[
        bool, typer.Option("--allow-non-empty", help="Allow creating the vault in a non-empty directory.")
    ] = False,
    should_open_vault: Annotated[
        bool, typer.Option("--open/--no-open", help="Whether to open the new vault in Obsidian upon creation.")
    ] = True,
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

    create_vault(path, template)
    if should_open_vault:
        open_vault(path)


if __name__ == "__main__":
    app()
