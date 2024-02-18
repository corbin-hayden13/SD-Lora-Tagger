import os
from glob import glob


def init_extra_network_tags(models_path, descriptions_path, included_networks=None):
    """
    This is used in conjunction with the refresh feature for extra networks to update tag files for each network
    :param models_path:
    :param included_networks: A dictionary of str: list as "network_folder_name": ["desired","file", "extensions"].  If not None, will extend existing known file extensions with provided ones
    :return: None
    """
    networks = {
        "Lora": ["safetensors"],
        "LyCORIS": ["safetensors"],
        "embeddings": ["pt"],
        "hypernetworks": ["pt"],
    }

    if included_networks is not None:
        for key in included_networks:
            try:
                networks[key].extend(included_networks[key])
            except KeyError:
                networks[key] = included_networks[key]

    for network in networks:
        if not os.path.exists(os.path.join(models_path, f"{network}/")):
            print(f"SD Lora Tagger: No folder for {network} found in models directory")
            continue

        path = os.path.join(models_path, network)
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
