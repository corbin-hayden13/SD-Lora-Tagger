import requests
import json
import os
import io
import hashlib
import glob
from fake_useragent import UserAgent

from modules.shared import cmd_opts, opts
from scripts.globals import out, networks, model_dirs, splitext
from scripts.helpers.tag_manager import append_files_by_network


api_endpoints = {
    "model_hash": "https://civitai.com/api/v1/model-versions/by-hash/",
    "model_id": "https://civitai.com/api/v1/models/",
}


def get_headers():
    """
    Copied from the Civitai Browser+ extension
    https://github.com/BlafKing/sd-civitai-browser-plus
    :return:
    """
    api_key = getattr(opts, "custom_api_key", "")
    try:
        user_agent = UserAgent().chrome
    except ImportError:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    headers = {
        'User-Agent': user_agent,
        'Sec-Ch-Ua': '"Brave";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-Gpc': '1',
        'Upgrade-Insecure-Requests': '1',
    }
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'

    return headers


def request_civit_api(api_url=None):
    """
    Copied from the Civitai Browser+ extension
    https://github.com/BlafKing/sd-civitai-browser-plus
    :param api_url:
    :return:
    """
    headers = get_headers()

    timeout = {"error": "timeout"}

    try:
        response = requests.get(api_url, headers=headers, timeout=(10, 30))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        out(e)
        return timeout
    else:
        response.encoding = "utf-8"
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            out("The CivitAI servers are currently offline. Please try again later.")
            return timeout

    return data


def gen_sha256(file_path):
    """
    Copied from the Civitai Browser+ extension
    https://github.com/BlafKing/sd-civitai-browser-plus
    :param file_path: full file path for model to be hashed
    :return: sha_256 hash as str
    """
    json_file = splitext(file_path)[0] + ".json"

    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding="utf-8") as f:
                data = json.load(f)

            if 'sha256' in data and data['sha256']:
                hash_value = data['sha256']
                return hash_value
        except Exception as e:
            out(f"Failed to open {json_file}; {e}")

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
            out(f"Failed to open {json_file}: {e}")
    else:
        data = {'sha256': hash_value}
        with open(json_file, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    return hash_value


def query_model_info(file_path):
    model_hash = gen_sha256(file_path)
    model_info = request_civit_api(f"{api_endpoints['model_hash']}{model_hash}")
    try:
        model_id = model_info["modelId"]

    except KeyError:  # Failed query
        out(f"Failed to retrieve model info for {file_path}")
        return file_path, {}

    model_info = request_civit_api(f"{api_endpoints['model_id']}{model_id}")
    try:
        return file_path, model_info
    except KeyError:
        out(f"Failed to retrieve tags for {file_path}")
        return file_path, {}


def model_info_query(file_paths):
    if len(file_paths) <= 0:
        return file_paths

    paths_and_info = []
    for file in file_paths:
        paths_and_info.append(query_model_info(file))

    return paths_and_info


def add_civitai_tags():
    for network in networks:
        #path = make_network_path(network)
        path = model_dirs[network]

        if not os.path.exists(path):
            out(f"No folder for {network} found in models directory")
            continue

        files = [file for file in glob.glob(path, recursive=True)
                 if splitext(file)[1].lstrip(".") in networks[network]]
        file_paths_to_write_info = [os.path.join(path, file) for file in files if not os.path.exists(
            os.path.join(path, f"{splitext(os.path.basename(file))[0]}.civitai.info"))]
        out(f"file_paths_to_write_info={file_paths_to_write_info}")
        paths_and_info = model_info_query(file_paths_to_write_info)
        paths_and_tags = []
        for path, info in paths_and_info:
            tags = ""
            try:
                for tag in info["tags"]:
                    tags += f"{tag},"

            except KeyError:
                continue

            paths_and_tags.append((path, tags[:-1]))

        append_files_by_network(network, paths_and_tags)

