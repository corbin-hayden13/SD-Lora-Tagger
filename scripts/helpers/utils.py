import os
from glob import glob
import sys
from importlib import import_module
from pathlib import Path

from scripts.helpers.tag_manager import write_files_by_network
from scripts.globals import out, networks, models_dir

from modules import paths_internal


def import_lora_lycoris():
    lora = None
    extra_networks_lora = None
    lycoris = None

    # Paths used from modules/paths_internal.py
    non_std_module_paths = [f'{os.path.join(paths_internal.extensions_builtin_dir, "Lora")}',
                            f'{os.path.join(paths_internal.extensions_builtin_dir, "a1111-sd-webui-lycoris")}'] # Not included in A1111
    for module_path in non_std_module_paths:
        if module_path not in sys.path:
            sys.path.append(module_path)

    try:
        lora = import_module("lora")
        extra_networks_lora = import_module("extra_networks_lora")
    except ModuleNotFoundError:
        out("The Lora extension is not installed in the \"extensions-builtin\" file path, cannot overwrite")

    try:
        lycoris = import_module("lycoris")
    except ModuleNotFoundError:
        out("The LyCORIS extension is not installed in the \"extensions-builtin\" file path, cannot overwrite")

    return lora, extra_networks_lora, lycoris


lora, extra_networks_lora, lycoris = import_lora_lycoris()


def make_network_path(network_type):
    # Necessary to find embeddings for AUTOMATIC1111/stable-diffusion-webui
    if network_type == "embeddings" and not os.path.exists(os.path.join(models_dir, f"{network_type}/")):
        return "./embeddings"
    else: return os.path.join(models_dir, f"{network_type}/")


def init_extra_network_tags(models_path, descriptions_path, included_networks=None):
    """
    This is used in conjunction with the refresh feature for extra networks to update tag files for each network
    :param models_path:
    :param descriptions_path:
    :param included_networks: A dictionary of str: list as "network_folder_name": ["desired","file", "extensions"].  If not None, will extend existing known file extensions with provided ones
    :return: None
    """

    if included_networks is not None:
        for key in included_networks:
            try:
                networks[key].extend(included_networks[key])
            except KeyError:
                networks[key] = included_networks[key]

    for network in networks:
        path = make_network_path(network)

        if not os.path.exists(path):
            out(f"No folder for {network} found in models directory")
            continue

        files = [file for file in os.listdir(path) if os.path.splitext(file)[1].lstrip(".") in networks[network]]
        write_files_by_network(network, files)


def get_or_create_tags_file(base_path, filename):
    path = os.path.join(base_path, f"{os.path.basename(filename).split('.')[0]}.txt")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            search_terms = f.read()

        return search_terms
    except FileNotFoundError:
        if not os.path.isdir(base_path):
            Path(base_path).mkdir(parents=True)  # All directories might not exist

        with open(path, 'w', encoding='utf-8') as f:
            search_terms = os.path.basename(filename).split('.')[0]
            f.write(search_terms)

        return search_terms


def clear_js_overrides(directory):
    # https://stackoverflow.com/questions/61821102/how-can-i-delete-files-by-extension-in-subfolders-of-a-folder
    for (dirname, dirs, files) in os.walk(directory):
        for file in files:
            if file.endswith('.js'):
                source_file = os.path.join(dirname, file)
                os.remove(source_file)


def load_tags(descriptions_path):
    files = glob(os.path.join(descriptions_path, "**/*.txt"), recursive=True)
    all_tags = {}

    for file in files:
        with open(file) as f:
            tags = f.read().split(",")

            for tag in tags:
                try:
                    all_tags[tag].append(file)
                except KeyError:
                    all_tags[tag] = [file]

    return all_tags
