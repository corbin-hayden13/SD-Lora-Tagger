import os
from glob import glob
import sys
from importlib import import_module
from scripts.helpers.paths import extension_paths
from pathlib import Path


def import_lora_lycoris():
    lora = None
    extra_networks_lora = None
    lycoris = None

    for module_path in extension_paths:
        if module_path not in sys.path:
            sys.path.append(module_path)

    try:
        lora = import_module("lora")
        extra_networks_lora = import_module("extra_networks_lora")
    except ModuleNotFoundError:
        print("The Lora extension is not installed in the \"extensions-builtin\" file path, cannot overwrite")

    try:
        lycoris = import_module("lycoris")
    except ModuleNotFoundError:
        print("The LyCORIS extension is not installed in the \"extensions-builtin\" file path, cannot overwrite")

    return lora, extra_networks_lora, lycoris


lora, extra_networks_lora, lycoris = import_lora_lycoris()


def init_extra_network_tags(models_path, descriptions_path, included_networks=None):
    """
    This is used in conjunction with the refresh feature for extra networks to update tag files for each network
    :param models_path:
    :param descriptions_path:
    :param included_networks: A dictionary of str: list as "network_folder_name": ["desired","file", "extensions"].  If not None, will extend existing known file extensions with provided ones
    :return: None
    """
    networks = {
        "Lora": ["safetensors"],
        "LyCORIS": ["safetensors"],
        "embeddings": ["pt", "safetensors"],
        "hypernetworks": ["pt"],
        "Stable-diffusion": ["safetensors", "ckpt"],
    }

    if included_networks is not None:
        for key in included_networks:
            try:
                networks[key].extend(included_networks[key])
            except KeyError:
                networks[key] = included_networks[key]

    for network in networks:
        if os.path.exists(os.path.join(descriptions_path, f"{network}_OLD/")):
            continue
        # Necessary to find embeddings for AUTOMATIC1111/stable-diffusion-webui
        if network == "embeddings" and not os.path.exists(os.path.join(models_path, f"{network}/")):
            path = "./embeddings"
        else: path = os.path.join(models_path, f"{network}/")

        if not os.path.exists(path):
            print(f"SD Lora Tagger: No folder for {network} found in models directory")
            continue

        files = [file.split(".")[0] for file in os.listdir(path) if file.split(".")[-1] in networks[network]]

        for file in files:
            if not os.path.exists(os.path.join(descriptions_path, f"{network}/{file}.txt")):
                if not os.path.exists(os.path.join(descriptions_path, f"{network}/")):
                    os.mkdir(os.path.join(descriptions_path, f"{network}/"))

                with open(os.path.join(descriptions_path, f"{network}/{file}.txt"), "w", encoding='utf8') as f:
                    f.write(file)


def clear_js_overrides(directory):
    # https://stackoverflow.com/questions/61821102/how-can-i-delete-files-by-extension-in-subfolders-of-a-folder
    for (dirname, dirs, files) in os.walk(directory):
        for file in files:
            if file.endswith('.js'):
                source_file = os.path.join(dirname, file)
                os.remove(source_file)


def load_tags(descriptions_path):
    files = [file for file in glob(os.path.join(descriptions_path, "**/*.txt"), recursive=True) if file.split(".")[-1] == "txt"]
    all_tags = {}

    for file in files:
        with open(file, encoding='utf-8') as f:
            file_name = os.path.basename(file).split(".")[0]
            tags = f.read().split(",")

            for tag in tags:
                try:
                    all_tags[tag].append(file.replace(f'{file_name}, ', ''))
                except KeyError:
                    all_tags[tag] = [file.replace(f'{file_name}, ', '')]

    return all_tags


def csv_to_list(data) -> list:
    """
    Converts comma seperated values to a python list
    """
    ls = []
    for item in data.split(','): # remove whitespaces and seperate by comma
        ls.append(item.strip())
    return ls


def list_to_csv(data: list):
    """
    Converts a list to a string of comma seperated values
    """
    return ', '.join(data)