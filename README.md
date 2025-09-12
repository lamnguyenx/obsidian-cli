# Obsidian CLI

Command line utility to interact with Obsidian. Notable features:

* List Obsidian vaults (`obsidian ls -l`)
* Open folders as vaults from the command line (`obsidian open {PATH}`)
* Create vaults from templates (`obsidian new {PATH}`)
    * You can share vault settings (e.g. keybindings) with the template via hardlinks, so when you edit the template keybindings, it affects all vaults
* Customize the new vault template and create new vaults (`obsidian template edit`)

## Installation and Usage

Python 3.11 or newer required.

```shell
uv tool install obsidian-cli
obsidian --help
```

This package can also be used as a Python API for Obsidian:

```python
from obsidian_cli import ObsidianConfig, open_vault
from pathlib import Path

print(ObsidianConfig.load())

open_vault(Path(R"C:\example-vault"))
```
