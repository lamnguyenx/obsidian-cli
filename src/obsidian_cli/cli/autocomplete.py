import shlex
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

import typer

from ..obsidian import ObsidianConfig

TAutocompleteResults = TypeVar("TAutocompleteResults", list[tuple[str, str]], list[str])


def quote_and_filter_autocomplete_results(incomplete: str, results: TAutocompleteResults) -> TAutocompleteResults:
    """
    Filters the given results list in-place to remove results that don't start with `incomplete`.

    Additionally, shell-escapes the suggestions.

    :returns: The same `results` instance.
    """
    incomplete = incomplete.casefold()
    for i in range(len(results) - 1, -1, -1):
        item = results[i]
        item_text = item[0] if isinstance(item, tuple) else item
        quoted_item_text = shlex.quote(item_text)
        if item_text.casefold().startswith(incomplete) or quoted_item_text.casefold().startswith(incomplete):
            if isinstance(item, tuple):
                results[i] = (quoted_item_text, item[1])  # pyright: ignore[reportArgumentType, reportCallIssue]
            else:
                results[i] = quoted_item_text  # pyright: ignore[reportArgumentType, reportCallIssue]
        else:
            results.pop(i)
    return results


def _get_vaults_autocompletion() -> list[tuple[str, str]]:
    return [(str(vault.path), vault_id) for vault_id, vault in ObsidianConfig.load().vaults.items()]


def _get_local_files_autocompletion(
    incomplete: str, *, predicate: Callable[[Path], bool] | None = None, from_root: Path | None = None
) -> list[tuple[str, str]]:
    incomplete_split = shlex.split(incomplete)
    incomplete = incomplete_split[0] if len(incomplete_split) == 1 else incomplete
    if from_root is None:
        from_root = Path()
    path_prefix = Path(from_root, incomplete)
    search_root = path_prefix if path_prefix.exists() and path_prefix.is_dir() else from_root
    allow_dotfiles = incomplete.startswith(".") or from_root.name.startswith(".")
    return [
        (str(file.relative_to(from_root)) if file.is_relative_to(from_root) else file.name, "")
        for file in search_root.iterdir()
        if (predicate is None or predicate(file)) and (allow_dotfiles or not file.name.startswith("."))
    ]


def complete_vaults(incomplete: str) -> list[tuple[str, str]]:
    return quote_and_filter_autocomplete_results(incomplete, _get_vaults_autocompletion())


def complete_vaults_and_local_dirs(incomplete: str) -> list[tuple[str, str]]:
    return quote_and_filter_autocomplete_results(
        incomplete, _get_vaults_autocompletion() + _get_local_files_autocompletion(incomplete, predicate=Path.is_dir)
    )


def complete_vault_file(ctx: typer.Context, incomplete: str) -> list[tuple[str, str]]:
    vault_path: str | None = ctx.params.get("path")
    if vault_path is None:
        return []
    return quote_and_filter_autocomplete_results(
        incomplete, _get_local_files_autocompletion(incomplete, from_root=Path(vault_path))
    )
