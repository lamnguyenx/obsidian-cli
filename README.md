# Obsidian CLI

Command line utility to interact with Obsidian. Notable features:

* List Obsidian vaults (`obsidian ls`)
* Open folders as vaults from the command line (`obsidian open {PATH}`)
* Share vault settings (keybindings) between vaults via hardlinks
* Customize the new vault template and create new vaults (`obsidian new --help`)

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
