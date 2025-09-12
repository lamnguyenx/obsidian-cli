import shutil
from pathlib import Path

from .obsidian import OBSIDIAN_CONFIG_DIR

VAULT_TEMPLATES_DIR = OBSIDIAN_CONFIG_DIR / "VaultTemplates"
DEFAULT_VAULT_TEMPLATE = "default"


def get_all_templates() -> list[str]:
    if not VAULT_TEMPLATES_DIR.exists():
        return []
    return [template.name for template in VAULT_TEMPLATES_DIR.iterdir() if template.is_dir()]


def create_vault(target_directory: Path, vault_template: str = DEFAULT_VAULT_TEMPLATE) -> None:
    vault_template_dir = VAULT_TEMPLATES_DIR / vault_template
    if not vault_template_dir.exists():
        if vault_template != DEFAULT_VAULT_TEMPLATE:
            raise ValueError(f"Template not found: {vault_template}")
        return
    shutil.copytree(vault_template_dir, target_directory, symlinks=True, dirs_exist_ok=True)
