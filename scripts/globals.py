import json
import os

import modules.scripts as scripts
from modules.shared import opts, models_path, cmd_opts
from modules.cmd_args import parser


global hide_nsfw


def out(msg):
    print(f"SD Lora Tagger: {msg}")


def splitext(path):
    return path[:path.rfind(".")]


""" Paths """
lora_tagger_dir = scripts.basedir()
models_dir = models_path
network_descriptions_path = os.path.join(lora_tagger_dir, "network_descriptions")

# Used in accordance to https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/master/modules/cmd_args.py
model_dirs = {
    "Lora": cmd_opts.lora_dir,
    "LyCORIS": cmd_opts.lyco_dir if hasattr(cmd_opts, "lyco_dir") else None,
    "embeddings": cmd_opts.embeddings_dir,
    "hypernetworks": cmd_opts.hypernetwork_dir,
    "Stable-diffusion": cmd_opts.ckpt_dir
}

""" Options and Flags """
js_overrides = ["sdNextExtraNetworks.js", "automatic1111ExtraNetworks.js"]
override_before_ui = ["lora_script.py", "lycoris_script.py", "ui_extra_networks.py"]
using_sd_next = parser.description is not None and parser.description == "SD.Next"

""" Other """
hide_nsfw_networks_key = "sd_lora_tagger_hide_nsfw_extra_networks"
networks = {
    "Lora": ["safetensors"],
    "LyCORIS": ["safetensors"] if model_dirs["LyCORIS"] is not None else [],
    "embeddings": ["pt", "safetensors"],
    "hypernetworks": ["pt"],
    "Stable-diffusion": ["safetensors", "ckpt"],
}


def update_hide_nsfw(extras=None):
    global hide_nsfw_networks_key, hide_nsfw

    hide_nsfw = getattr(opts, hide_nsfw_networks_key, None)
    if hide_nsfw is None:
        hide_nsfw = False
        out(f"KeyError on shared.opts.data, defaulting to hide_nsfw={hide_nsfw}")

    if extras is not None:
        extras_dict = json.loads(extras)
        extras_dict["hide_nsfw"] = "true" if hide_nsfw else "false"
        return json.dumps(extras_dict)

    else: return extras


update_hide_nsfw()

