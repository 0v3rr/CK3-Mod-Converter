# CK3 Workshop Mod Converter

A lightweight Windows tool that converts mods downloaded via SteamCMD from workshop format to local mod format compatible with the Paradox launcher.

## What it does

For each mod it:
- Copies the mod folder to your Paradox mod directory
- Patches the `descriptor.mod` (fixes path, removes `remote_file_id`)
- Generates the `.mod` file required by the launcher
- Optionally deletes the source after a verified copy

## Usage

1. Download your mods via SteamCMD using `workshop_download_item`
2. Run `CK3ModConverter.exe`
3. Press Enter to use default paths or `c` to set custom ones
4. Choose whether to delete source files after conversion
5. Open the Paradox launcher — your mods will appear

## Default paths

| | Path |
|---|---|
| Source | `C:\Users\<you>\Downloads\STEAMCMD\steamapps\workshop\content\1158310` |
| Destination | `C:\Users\<you>\Documents\Paradox Interactive\Crusader Kings III\mod` |

Custom paths are saved in `config.json` and reused on next launch.

## Requirements

- Windows only
- No installation required

## License

MIT — free to use, modify and redistribute. See [LICENSE](LICENSE).
