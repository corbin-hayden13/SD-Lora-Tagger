import os
import io
from glob import glob
import sys
from importlib import import_module
from pathlib import Path
import json
import hashlib

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


def gen_sha256(file_path):
    """
    Copied from the Civitai Browser+ extension
    https://github.com/BlafKing/sd-civitai-browser-plus
    :param file_path: full file path for model to be hashed
    :return: sha_256 hash as str
    """
    json_file = os.path.splitext(file_path)[0] + ".json"

    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding="utf-8") as f:
                data = json.load(f)

            if 'sha256' in data and data['sha256']:
                hash_value = data['sha256']
                return hash_value
        except Exception as e:
            print(f"SD Lora Tagger: Failed to open {json_file}; {e}")

    def read_chunks(file, size=io.DEFAULT_BUFFER_SIZE):
        while True:
            chunk = file.read(size)
            if not chunk:
                break
            yield chunk

    blocksize = 1 << 20
    h = hashlib.sha256()
    length = 0
    with open(os.path.realpath(file_path), 'rb') as f:
        for block in read_chunks(f, size=blocksize):
            length += len(block)
            h.update(block)

    hash_value = h.hexdigest()

    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding="utf-8") as f:
                data = json.load(f)

            if 'sha256' in data and data['sha256']:
                data['sha256'] = hash_value

            with open(json_file, 'w', encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to open {json_file}: {e}")
    else:
        data = {'sha256': hash_value}
        with open(json_file, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    return hash_value


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
