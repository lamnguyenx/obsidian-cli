from typing import Annotated

import typer

from .. import ObsidianConfig, open_vault, vault_templates

app = typer.Typer(name="template", no_args_is_help=True, help="Commands to view and edit vault templates.")


@app.command()
def info() -> None:
    """
    Lists templates in the template directory.
    """
    templates = vault_templates.get_all_templates()
    typer.echo(f"Found {len(templates)} template(s) at {vault_templates.VAULT_TEMPLATES_DIR}")
    if len(templates):
        typer.echo()
        import tabulate

        typer.echo(
            tabulate.tabulate(
                [(template, vault_templates.get_hardlink_count(template)) for template in templates],
                headers=("Name", "# Hardlinked Vaults"),
            )
        )


@app.command()
def edit(
    template_name: Annotated[
        str,
        typer.Argument(
            help="The name of the template to edit. Defaults to 'default'.",
            autocompletion=vault_templates.get_all_templates,
        ),
    ] = vault_templates.DEFAULT_VAULT_TEMPLATE,
) -> None:
    """
    Opens the given template in Obsidian for editing, creating it if necessary.
    """
    template_path = vault_templates.VAULT_TEMPLATES_DIR / template_name
    template_path.mkdir(parents=True, exist_ok=True)
    vault_id = ObsidianConfig.load().ensure_path_is_vault(template_path)
    open_vault(vault_id)
