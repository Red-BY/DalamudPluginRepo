import json
import os
import re
from pathlib import Path
from time import time
from urllib.parse import urlparse

import requests

DOWNLOAD_URL = "{}/releases/download/v{}/latest.zip"
GITHUB_RELEASE_TAG_API_URL = "https://api.github.com/repos/{}/{}/releases/tags/v{}"

DEFAULTS = {
    "IsHide": False,
    "IsTestingExclusive": False,
    "ApplicableVersion": "any",
}

DUPLICATES = {
    "DownloadLinkInstall": ["DownloadLinkTesting", "DownloadLinkUpdate"],
}

TRIMMED_KEYS = [
    "Author",
    "Name",
    "Punchline",
    "Description",
    "Changelog",
    "InternalName",
    "AssemblyVersion",
    "RepoUrl",
    "ApplicableVersion",
    "Tags",
    "CategoryTags",
    "DalamudApiLevel",
    "IconUrl",
    "ImageUrls",
]

PLUGINS_DIR = Path("./plugins")
PLUGINMASTER_PATH = Path("pluginmaster.json")


def main():
    master = extract_manifests()
    master = [trim_manifest(manifest) for manifest in master]
    add_extra_fields(master)
    get_last_updated_times(master)
    write_master(master)


def extract_manifests():
    manifests = []

    for dirpath, _, filenames in os.walk(PLUGINS_DIR):
        plugin_dir = Path(dirpath)
        plugin_name = plugin_dir.name
        manifest_name = f"{plugin_name}.json"

        if not filenames or manifest_name not in filenames:
            continue

        with open(plugin_dir / manifest_name, encoding="utf-8") as f:
            manifests.append(json.load(f))

    return manifests


def add_extra_fields(manifests):
    for manifest in manifests:
        manifest["DownloadLinkInstall"] = DOWNLOAD_URL.format(
            manifest["RepoUrl"], manifest["AssemblyVersion"]
        )

        for key, value in DEFAULTS.items():
            if key not in manifest:
                manifest[key] = value

        for source, keys in DUPLICATES.items():
            for key in keys:
                if key not in manifest:
                    manifest[key] = manifest[source]

        owner, repo = parse_github_repo(manifest.get("RepoUrl", ""))
        if owner and repo:
            manifest["DownloadCount"] = get_release_download_count(
                owner, repo, manifest["AssemblyVersion"]
            )
        else:
            manifest["DownloadCount"] = 0


def parse_github_repo(repo_url):
    if not repo_url:
        return None, None

    path = urlparse(repo_url).path.strip("/")
    match = re.fullmatch(r"([^/]+)/([^/]+?)(?:\.git)?", path)
    if not match:
        return None, None

    return match.group(1), match.group(2)


def get_release_download_count(owner, repo, version):
    url = GITHUB_RELEASE_TAG_API_URL.format(owner, repo, version)
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return 0

        data = response.json()
        return sum(asset.get("download_count", 0) for asset in data.get("assets", []))
    except requests.RequestException as exc:
        print(f"Failed to fetch download count for {owner}/{repo}@v{version}: {exc}")
        return 0


def get_last_updated_times(manifests):
    previous_manifests = []
    if PLUGINMASTER_PATH.exists():
        with open(PLUGINMASTER_PATH, encoding="utf-8") as f:
            previous_manifests = json.load(f)

    for manifest in manifests:
        manifest["LastUpdate"] = str(int(time()))

        for previous_manifest in previous_manifests:
            if manifest["InternalName"] != previous_manifest["InternalName"]:
                continue

            if manifest["AssemblyVersion"] == previous_manifest["AssemblyVersion"]:
                manifest["LastUpdate"] = previous_manifest["LastUpdate"]

            break


def write_master(master):
    with open(PLUGINMASTER_PATH, "w", encoding="utf-8") as f:
        json.dump(master, f, indent=4)
        f.write("\n")


def trim_manifest(plugin):
    return {key: plugin[key] for key in TRIMMED_KEYS if key in plugin}


if __name__ == "__main__":
    main()
