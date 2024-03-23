import scripts.helpers.tag_manager as tm
import os
from glob import glob
from pathlib import Path
from scripts.helpers.utils import csv_to_list
from scripts.globals import network_descriptions_path

DEPRECATED_SUFFIX = "_OLD"

def rename_directory(network_name):
    old_name = get_network_directory(network_name)
    new_name = old_name + DEPRECATED_SUFFIX

    os.rename(old_name, new_name)

def read_tags_file(path, model_name):
    with open(path, 'r', encoding='utf-8') as f:
        tags = csv_to_list(f.read())
        clean_tags = []
        for tag in tags:
            if tag != '' and tag != model_name and tag.lstrip() != '' and model_name.replace(' ', '') != tag:
                clean_tags.append(tag)
        return clean_tags

def get_network_directory(network_name):
    return os.path.join(network_descriptions_path, network_name)

def get_existing_network_folders(network_names):
    exists = []
    for network_name in network_names:
        if os.path.exists(get_network_directory(network_name)) and not os.path.exists(get_network_directory(f"{network_name + DEPRECATED_SUFFIX}")):
            exists.append(network_name)
    return exists

def update_network(network_name):
    print(f"SD Lora Tagger: Updating {network_name} networks...")
    paths = glob(os.path.join(get_network_directory(network_name), f"**[!{DEPRECATED_SUFFIX}]\\*.txt"), recursive=True)

    for tag_path in paths:
        model = tag_path.split('\\')[-1].split('.')[0]
        tags = read_tags_file(tag_path, model)
        print(f"{model}, {tags}")
        if len(tags) == 0:
            continue
        for tag in tags:
            tm.update_tag(tag, models=[model])

    try:
        rename_directory(network_name)
    except FileExistsError:
        print(f"SD Lora Tagger: Failed to rename '{network_name}' directory. Tags were still updated.")



def update():
    # replace with globals.networks when PR #32 is merged
    networks = ["embeddings", "hypernetworks", "Lora", "LyCORIS", "Stable-diffusion"]
    networks_to_update = get_existing_network_folders(networks)

    if len(networks_to_update) == 0:
        return
    
    print("SD Lora Tagger: Outdated tags detected. Your tags will now be updated to support the latest version of the extension.\nSD Lora Tagger: A copy of your outdated tags will be saved, but they will no longer be usable.\nSD Lora Tagger: If you experience any issues during the process, please report it to https://github.com/corbin-hayden13/SD-Lora-Tagger")
    for network in networks_to_update:
        update_network(network)
    print("SD Lora Tagger: Tags updated successfully!")
    # tm.save_tags_debug()
    tm.save_tags()
