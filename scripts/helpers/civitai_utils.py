import requests
import json
import os
import io
import hashlib
import time
from fake_useragent import UserAgent
from multiprocessing import cpu_count, Process, ProcessError, Queue

from modules.shared import cmd_opts, opts


api_urls = {
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
        print(f"SD Lora Tagger: {e}")
        return timeout
    else:
        response.encoding = "utf-8"
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            print("SD Lora Tagger: The CivitAI servers are currently offline. Please try again later.")
            return timeout

    return data


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


def query_model_info(file_path):
    model_hash = gen_sha256(file_path)
    model_info = request_civit_api(f"{api_urls['model_hash']}{model_hash}")
    try:
        model_id = model_info["modelId"]

    except KeyError:  # Failed query
        print(f"SD Lora Tagger: Failed to retrieve model info for {file_path}")
        return file_path, []

    model_info = request_civit_api(f"{api_urls['model_id']}{model_id}")
    try:
        return file_path, model_info
    except KeyError:
        print(f"SD Lora Tagger: Failed to retrieve tags for {file_path}")
        return file_path, []


def get_civitai_tags(file_paths, ret_queue):
    path_and_info = []
    for file in file_paths:
        path_and_info.append(query_model_info(file))
        time.sleep(0.5)

    ret_queue.put(path_and_info)


def model_info_query(file_paths):
    if len(file_paths) <= 0:
        return file_paths

    cpus = cpu_count() - 1
    files_per_process = len(file_paths) // cpus

    path_folds = []
    for a in range(cpus - 1):
        path_folds.append(file_paths[a * files_per_process:(a * files_per_process) + files_per_process])

    path_folds.append(file_paths[(cpus - 1) * files_per_process:])

    processes_and_queues = []
    for path_fold in path_folds:
        ret_queue = Queue()
        processes_and_queues.append((
            Process(target=get_civitai_tags, args=(path_fold, ret_queue)),
            ret_queue
        ))

    for process, _ in processes_and_queues:
        process.start()

    for process, _ in processes_and_queues:
        process.join()

    paths_and_info = []
    for _, queue in processes_and_queues:
        while not queue.empty():
            paths_and_info.extend(queue.get())

    print(f"SD Lora Tagger: paths_and_info =>\n{paths_and_info}")
    return paths_and_info


