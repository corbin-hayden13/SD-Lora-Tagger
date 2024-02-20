import os
from glob import glob
import sys
from importlib import import_module
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

                with open(os.path.join(descriptions_path, f"{network}/{file}.txt"), "w") as f:
                    f.write(file)


def load_tags(descriptions_path):
    files = [file for file in glob(os.path.join(descriptions_path, "**/*.txt"), recursive=True) if file.split(".")[-1] == "txt"]
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
