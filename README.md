# DalamudPluginRepo

Custom [Dalamud](https://github.com/goatcorp/Dalamud) / [XIVLauncher](https://github.com/goatcorp/FFXIVQuickLauncher) plugin repository.

## Installation

1. Open Dalamud Settings with `/xlsettings` (or the button at the bottom of the Plugin Installer).
2. Open the **Experimental** tab.
3. Paste the following URL into an empty **Custom Plugin Repositories** box:

   ```text
   https://raw.githubusercontent.com/Red-BY/DalamudPluginRepo/main/pluginmaster.json
   ```

4. Click **+**, then save with the disk icon.

Plugins from this repo will then appear in `/xlplugins`.

## Plugins

| Plugin | Description |
| --- | --- |
| [High Resolution Previews](https://github.com/Red-BY/XIVHighResPreviews) | Upscales in-game character preview windows (Character, Try On, Inspect, Glamour, Adventurer Plate, etc.). |

## Updating this repository

Each plugin lives under `plugins/<InternalName>/` with a `<InternalName>.json` manifest (copy from a release asset or the plugin build output).

When you publish a new plugin release:

1. Update `AssemblyVersion` (and optional `Changelog`) in that plugin's JSON.
2. Push to this repo, **or** trigger the **Regenerate PluginMaster** workflow.

`generate_pluginmaster.py` builds `pluginmaster.json` with download links pointing at each plugin's GitHub release (`…/releases/download/v{version}/latest.zip`).

```bash
pip install -r requirements.txt
python generate_pluginmaster.py
```

A GitHub Action also regenerates `pluginmaster.json` on push, on a 12-hour schedule, and via `repository_dispatch` (`plugin-released`).
