import os

from scripts.globals import network_descriptions_path, out, splitext


def write_tags_by_network(network, file):
    if not os.path.exists(
            os.path.join(network_descriptions_path, f"{network}/{splitext(os.path.basename(file))[0]}.txt")):
        with open(os.path.join(network_descriptions_path,
                  f"{network}/{splitext(os.path.basename(file))[0]}.txt"), "w", encoding="utf-8") as f:
            f.write(file)


def append_tags_by_network(network, file, tags):
    if not os.path.exists(
            os.path.join(network_descriptions_path, f"{network}/{splitext(os.path.basename(file))[0]}.txt")):
        out(f"No such file {file}")
        return

    with open(os.path.join(network_descriptions_path,
                           f"{network}/{splitext(os.path.basename(file))[0]}.txt"), "a", encoding="utf-8") as f:
        f.write(f",{tags}")


def write_files_by_network(network, files):
    if not os.path.exists(os.path.join(network_descriptions_path, f"{network}/")):
        os.mkdir(os.path.join(network_descriptions_path, f"{network}/"))

    for file in files:
        # Creating and writing to tag files if they don't exist
        write_tags_by_network(network, file)


def append_files_by_network(network, files_and_tags):
    if not os.path.exists(os.path.join(network_descriptions_path, f"{network}/")):
        out(f"No such directory {os.path.join(network_descriptions_path, f'{network}/')}")
        return

    for file, tags in files_and_tags:
        append_tags_by_network(network, file, tags)

