import os
import shutil

import modules.scripts as scripts
from modules.scripts import script_callbacks
from modules import extra_networks
from modules.script_callbacks import callback_map

from modules.ui_extra_networks import extra_pages
import gradio as gr

from scripts.helpers.utils import init_extra_network_tags, decorate_as_listlike
from scripts.helpers.registration_override import register_all

"""
TODO: Setting to switch between AUTOMATIC1111/stable-diffusion-webui and vladmandic/automatic (SD.Next)
TODO: Can search by something called "search_terms"; Defined as the absolute file path of all extra networks currently
  - Register extra network pages to add custom search_terms
"""


txt2img_extras_refresh_comp = None
lora_tagger_dir = scripts.basedir()
config_path = os.path.join(lora_tagger_dir, r"scripts\helpers\config.txt")
models_dir = './models'

init_extra_network_tags(models_dir, os.path.join(lora_tagger_dir, "network_descriptions/"))
# This prevents the on_before_ui() callback call for the Lora script
decorate_as_listlike(callback_map, key="callbacks_before_ui", exclude_scripts=["lora_script.py"])


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
                txt2img_extras_refresh_comp.click(lambda: print(f"SD Lora Tagger: Hello from the script!"
                                                                f"\n{os.listdir(f'./models/Lora/')}"))

        except KeyError:
            pass

    def before_component(self, component, **kwargs):
        global pos_prompt_comp
        try:
            if kwargs["elem_id"] == "txt2img_prompt":
                pos_prompt_comp = component

        except KeyError:
            pass


script_callbacks.on_before_ui(register_pages)
