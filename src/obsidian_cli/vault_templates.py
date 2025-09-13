import logging
import shutil
from enum import Enum
from pathlib import Path

from .obsidian import OBSIDIAN_CONFIG_DIR

VAULT_CONFIG_DIRNAME = ".obsidian"
VAULT_TEMPLATES_DIR = OBSIDIAN_CONFIG_DIR / "VaultTemplates"
DEFAULT_VAULT_TEMPLATE = "default"
SETTING_FILES_TO_NEVER_HARDLINK = {"workspace.json", "workspace-mobile.json"}


logger = logging.getLogger(__name__)


class SettingsCreationMode(Enum):
    copy = "copy"
    hardlink = "hardlink"


def get_all_templates() -> list[str]:
    if not VAULT_TEMPLATES_DIR.exists():
        return []
    return [template.name for template in VAULT_TEMPLATES_DIR.iterdir() if template.is_dir()]


def get_hardlink_count(template: str) -> int:
    template_dir = VAULT_TEMPLATES_DIR / template
    if not template_dir.exists() or not template_dir.is_dir():
        raise ValueError(f"Template not found: {template}")
    app_json_file = template_dir / VAULT_CONFIG_DIRNAME / "app.json"
    if not app_json_file.exists():
        return 0
    return app_json_file.stat().st_nlink - 1


def create_vault(
    target_directory: Path,
    vault_template: str = DEFAULT_VAULT_TEMPLATE,
    settings_creation_mode: SettingsCreationMode = SettingsCreationMode.hardlink,
) -> None:
    """
    Creates a new Obsidian vault from the given template.

    :param target_directory: The directory where the vault would be created.
    :param vault_template: The name of the template to use.
    :param settings_creation_mode: Defines how to create the settings of the new vault.

    :raises ValueError: If the template with the given name was not found.
    :raises OSError: If failed hardlinking files.
    """
    vault_template_dir = VAULT_TEMPLATES_DIR / vault_template
    if not vault_template_dir.exists():
        if vault_template != DEFAULT_VAULT_TEMPLATE:
            raise ValueError(f"Template not found: {vault_template}")
        return
    shutil.copytree(vault_template_dir, target_directory, symlinks=True, dirs_exist_ok=True)
    if settings_creation_mode == SettingsCreationMode.hardlink:
        target_obsidian_dir = target_directory / VAULT_CONFIG_DIRNAME
        for setting_file in (vault_template_dir / VAULT_CONFIG_DIRNAME).glob("*.json"):
            if setting_file.name in SETTING_FILES_TO_NEVER_HARDLINK:
                continue
            target_file = target_obsidian_dir / setting_file.name
            target_file.unlink()
            try:
                target_file.hardlink_to(setting_file)
            except OSError:
                logger.warning(
                    f"Failed creating hardlink '{target_file}' -> '{setting_file}', probably because it's on a"
                    "different drive than the template.\n"
                    "Falling back to copy mode. To suppress this warning, run with settings_creation_mode=copy."
                )
                shutil.copyfile(setting_file, target_file)
                break
