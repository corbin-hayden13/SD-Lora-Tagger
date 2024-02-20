import os
import shutil
import scripts.ui_tag_editor

import modules.scripts as scripts
from modules.scripts import script_callbacks
from modules.script_callbacks import callback_map
from modules.ui_extra_networks import extra_pages

from scripts.helpers.utils import init_extra_network_tags
from scripts.helpers.registration_override import register_all
from scripts.edit_tags_ui import populate_all_tags
from scripts.ui_tag_editor import on_ui_tabs
from scripts.helpers.paths import destination_path, source_path, models_dir, using_sd_next, model_description_dirs, description_path

txt2img_extras_refresh_comp = None
override_before_ui = ["lora_script.py", "lycoris_script.py", "ui_extra_networks.py"]

try:
    # Avoiding losing the file during transit, opting to copy instead of replacing the file
    if os.path.exists(destination_path):
        os.remove(destination_path)

    shutil.copy(source_path, destination_path)
except Exception as e:
    print(f"SD Lora Tagger: using_sd_next={using_sd_next}: could not move {source_path} to {destination_path}")

init_extra_network_tags(models_dir, description_path)
populate_all_tags()


def register_pages():
    extra_pages.clear()
    description_paths = (model_description_dirs[0],
                         model_description_dirs[1],
                         model_description_dirs[2],
                         model_description_dirs[3],
                         model_description_dirs[4])

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