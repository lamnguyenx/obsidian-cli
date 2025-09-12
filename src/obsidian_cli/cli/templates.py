from typing import Annotated

import typer

from .. import DEFAULT_VAULT_TEMPLATE, VAULT_TEMPLATES_DIR, ObsidianConfig, get_all_templates, open_vault

app = typer.Typer(name="template", no_args_is_help=True, help="Commands to view and edit vault templates.")


@app.command()
def info() -> None:
    """
    Lists templates in the template directory.
    """
    templates = get_all_templates()
    typer.echo(f"Found {len(templates)} template(s) at {VAULT_TEMPLATES_DIR}")
    for template in templates:
        typer.echo(template)


@app.command()
def edit(
    template_name: Annotated[
        str, typer.Argument(help="The name of the template to edit. Defaults to 'default'.")
    ] = DEFAULT_VAULT_TEMPLATE,
) -> None:
    """
    Opens the given template in Obsidian for editing.
    """
    template_path = VAULT_TEMPLATES_DIR / template_name
    template_path.mkdir(parents=True, exist_ok=True)
    vault_id = ObsidianConfig.load().ensure_path_is_vault(template_path)
    open_vault(vault_id)
