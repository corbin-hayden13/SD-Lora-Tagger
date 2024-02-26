import os
import shutil
import json

import modules.scripts as scripts
from modules.scripts import script_callbacks
from modules.script_callbacks import callback_map
from modules.ui_extra_networks import extra_pages

from scripts.helpers.utils import init_extra_network_tags, clear_js_overrides
from scripts.helpers.registration_override import register_all
from scripts.edit_tags_ui import on_ui_tabs, on_ui_settings, populate_all_tags
from scripts.globals import lora_tagger_dir, models_dir, using_sd_next, js_overrides, override_before_ui, hide_nsfw, out


destination_path = os.path.join(lora_tagger_dir, f"javascript/{js_overrides[0]}") if using_sd_next\
              else os.path.join(lora_tagger_dir, f"javascript/{js_overrides[1]}")
source_path = os.path.join(lora_tagger_dir, f"js_staging/{js_overrides[0]}") if using_sd_next\
         else os.path.join(lora_tagger_dir, f"js_staging/{js_overrides[1]}")

clear_js_overrides(os.path.join(lora_tagger_dir, "javascript"))


try:
    # Avoiding losing the file during transit, opting to copy instead of replacing the file
    if os.path.exists(destination_path):
        os.remove(destination_path)

    shutil.copy(source_path, destination_path)
except Exception as e:
    out(f"using_sd_next={using_sd_next}: could not move {source_path} to {destination_path}")

init_extra_network_tags(models_dir, os.path.join(lora_tagger_dir, "network_descriptions/"))
populate_all_tags()


def register_pages():
    extra_pages.clear()
    description_paths = (os.path.join(lora_tagger_dir, "network_descriptions/embeddings/"),
                         os.path.join(lora_tagger_dir, "network_descriptions/hypernetworks/"),
                         os.path.join(lora_tagger_dir, "network_descriptions/Stable-diffusion/"),
                         os.path.join(lora_tagger_dir, "network_descriptions/Lora/"),
                         os.path.join(lora_tagger_dir, "network_descriptions/LyCORIS/"))

    item_decorator_dict = {
        "hide_nsfw": "true" if hide_nsfw else "false",
    }

    json_data = json.dumps(item_decorator_dict)

    register_all(description_paths, json_data)


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
script_callbacks.on_ui_settings(on_ui_settings)
