import modules.scripts as scripts
import os
from modules.cmd_args import parser
from modules import paths_internal

base_dir = scripts.basedir()
ui_config_path = os.path.join(paths_internal.models_path, "../ui-config.json") # this can vary, change later
description_path = os.path.join(base_dir, 'network_descriptions')
ui_config_debug = os.path.join(description_path, "debug.json")
config_path = os.path.join(base_dir, r"scripts\helpers\config.txt")
models_dir = './models'
using_sd_next = parser.description is not None and parser.description == "SD.Next"

js_overrides = ["sdNextExtraNetworks.js", "automatic1111ExtraNetworks.js"]
destination_path = os.path.join(base_dir, f"javascript/{js_overrides[0]}") if using_sd_next\
              else os.path.join(base_dir, f"javascript/{js_overrides[1]}")
source_path = os.path.join(base_dir, f"js_staging/{js_overrides[0]}") if using_sd_next\
         else os.path.join(base_dir, f"js_staging/{js_overrides[1]}")

# Paths used from modules/paths_internal.py
extension_paths = [f'{os.path.join(paths_internal.extensions_builtin_dir, "Lora")}',
                        f'{os.path.join(paths_internal.extensions_builtin_dir, "a1111-sd-webui-lycoris")}'] # Not included in A1111



model_description_dirs = {
    0: os.path.join(description_path, "Stable-diffusion/"),
    1: os.path.join(description_path, "embeddings/"),
    2: os.path.join(description_path, "hypernetworks/"),
    3: os.path.join(description_path, "Lora/"),
    4: os.path.join(description_path, "LyCORIS/")
}

tags_path = os.path.join(description_path, "tags.json")
tags_path_d = os.path.join(description_path, "tags_debug.json")