import requests
import json
from fake_useragent import UserAgent

from scripts.helpers.utils import gen_sha256

from modules.shared import cmd_opts, opts


api_urls = {
    "model_hash": "https://civitai.com/api/v1/model-versions/by-hash/",
    "model_id": "https://civitai.com/api/v1/models/",
}


def query_model_tags(file_path):
    model_hash = gen_sha256(file_path)
    model_info = request_civit_api(f"{api_urls['model_hash']}{model_hash}")
    try:
        model_id = model_info["modelId"]

    except KeyError:  # Failed query
        print(f"SD Lora Tagger: Failed to retrieve model info for {file_path}")
        return []

    model_info = request_civit_api(f"{api_urls['model_id']}{model_id}")
    try:
        return model_info["tags"]
    except KeyError:
        print(f"SD Lora Tagger: Failed to retrieve tags for {file_path}")


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

