import shlex
from pathlib import Path
from typing import TypeVar

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


def _get_local_files_autocompletion(incomplete: str) -> list[tuple[str, str]]:
    allow_dotfiles = incomplete.startswith(".")
    results: list[tuple[str, str]] = [
        (file.name, "")
        for file in Path().iterdir()
        if file.is_dir() and (allow_dotfiles or not file.name.startswith("."))
    ]
    return results


def complete_vaults(incomplete: str) -> list[tuple[str, str]]:
    return quote_and_filter_autocomplete_results(incomplete, _get_vaults_autocompletion())


def complete_vaults_and_local_files(incomplete: str) -> list[tuple[str, str]]:
    return quote_and_filter_autocomplete_results(
        incomplete, _get_vaults_autocompletion() + _get_local_files_autocompletion(incomplete)
    )


def complete_vault_file(incomplete: str) -> list[tuple[str, str]]:
    return []
