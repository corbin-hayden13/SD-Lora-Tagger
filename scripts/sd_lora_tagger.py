import os
import shutil

import modules.scripts as scripts
from modules.scripts import script_callbacks
from modules.script_callbacks import callback_map
from modules.cmd_args import parser
from modules.ui_extra_networks import extra_pages

from scripts.helpers.utils import init_extra_network_tags
from scripts.helpers.registration_override import register_all
from scripts.edit_tags_ui import on_ui_tabs, populate_all_tags


txt2img_extras_refresh_comp = None
lora_tagger_dir = scripts.basedir()
config_path = os.path.join(lora_tagger_dir, r"scripts\helpers\config.txt")
models_dir = './models'
override_before_ui = ["lora_script.py", "lycoris_script.py", "ui_extra_networks.py"]

using_sd_next = parser.description is not None and parser.description == "SD.Next"
js_overrides = ["sdNextExtraNetworks.js", "automatic1111ExtraNetworks.js"]
destination_path = os.path.join(lora_tagger_dir, f"javascript/{js_overrides[0]}") if using_sd_next\
              else os.path.join(lora_tagger_dir, f"javascript/{js_overrides[1]}")
source_path = os.path.join(lora_tagger_dir, f"js_staging/{js_overrides[0]}") if using_sd_next\
         else os.path.join(lora_tagger_dir, f"js_staging/{js_overrides[1]}")

if not os.path.exists(destination_path):
    try:
        # Avoiding losing the file during transit, opting to copy instead of replacing the file
        shutil.copy(source_path, destination_path)
    except Exception as e:
        print(f"SD Lora Tagger: using_sd_next={using_sd_next}: could not move {source_path} to {destination_path}")

init_extra_network_tags(models_dir, os.path.join(lora_tagger_dir, "network_descriptions/"))
populate_all_tags()


def register_pages():
    extra_pages.clear()
    description_paths = (os.path.join(lora_tagger_dir, "network_descriptions/embeddings/"),
                         os.path.join(lora_tagger_dir, "network_descriptions/hypernetworks/"),
                         os.path.join(lora_tagger_dir, "network_descriptions/Stable-diffusion/"),
                         os.path.join(lora_tagger_dir, "network_descriptions/Lora/"),
                         os.path.join(lora_tagger_dir, "network_descriptions/LyCORIS/"))

    register_all(description_paths)


class LoraTagger(scripts.Script):
    def title(self):
        return "SD Lora Tagger"  # Extension for Bounty https://civitai.com/bounties/1183/extension-for-tagging-loras

    """ This EXACT function and syntax is required for self.processing to be called """
    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def after_component(self, component, **kwargs):
        global txt2img_extras_refresh_comp
        try:
            if kwargs["elem_id"] == "txt2img_extra_refresh":
                txt2img_extras_refresh_comp = component

        except KeyError:
            pass

    def before_component(self, component, **kwargs):
        global pos_prompt_comp
        try:
            if kwargs["elem_id"] == "txt2img_prompt":
                pos_prompt_comp = component

        except KeyError:
            pass


# Stops Lora, LyCORIS from rendering their own extra_network pages alongside the custom ones
#   by removing their on_before_ui() callback functions before they're called
callback_map["callbacks_before_ui"] = [item for item in callback_map["callbacks_before_ui"]
                                       if os.path.basename(item.script) not in override_before_ui]
script_callbacks.on_before_ui(register_pages)
script_callbacks.on_ui_tabs(on_ui_tabs)
