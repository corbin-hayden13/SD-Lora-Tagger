import os
import shutil

import modules.scripts as scripts
from modules.scripts import script_callbacks
from modules.ui_extra_networks import extra_pages
import gradio as gr

from scripts.helpers.utils import init_extra_network_tags, load_tags
from scripts.helpers.registration_override import register_embeddings, register_hypernetworks, register_checkpoints,\
    register_loras

"""
TODO: Setting to switch between AUTOMATIC1111/stable-diffusion-webui and vladmandic/automatic (SD.Next)
TODO: Can search by something called "search_terms"; Defined as the absolute file path of all extra networks currently
  - Register extra network pages to add custom search_terms
"""


txt2img_extras_refresh_comp = None
lora_tagger_dir = scripts.basedir()
config_path = os.path.join(lora_tagger_dir, r"scripts\helpers\config.txt")
folder_names = ["Lora", "LyCORIS", "embeddings"]
models_dir = f'./{lora_tagger_dir}/../../models/'
is_sd_next = None

with open(config_path, "r") as f:
    is_sd_next = True if f.read().split("=")[1] == "True" else False

override_file = 'sdNextExtraNetworksOverride.js' if is_sd_next else 'webuiExtraNetworksOverride.js'
undo_file = 'sdNextExtraNetworksOverride.js' if not is_sd_next else 'webuiExtraNetworksOverride.js'

source_path_override = os.path.join(lora_tagger_dir, f"staging\\{override_file}")
source_path_undo = os.path.join(lora_tagger_dir, f"javascript\\{undo_file}")
destination_path_override = os.path.join(lora_tagger_dir, f"javascript\\{override_file}")

try:
    shutil.copy(source_path_override, destination_path_override)
    print(f"SD Lora Tagger: Successfully copied js file = {os.path.exists(destination_path_override)}")
except Exception as e:
    print(f"Could not copy {override_file} from {os.path.join(lora_tagger_dir, 'staging')} directory")

if os.path.exists(source_path_undo):
    try:
        os.remove(source_path_undo)
        print(f"SD Lora Tagger: Successfully deleted js file = {not os.path.exists(source_path_undo)}")
    except Exception as e:
        print(f"Could not delete {undo_file} from {os.path.join(lora_tagger_dir), 'javascript'} directory")

init_extra_network_tags(models_dir, os.path.join(lora_tagger_dir, "network_descriptions/"))


def set_is_sd_next(cond):
    with open(config_path, "w") as f:
        f.write(f"sd.next={cond}")


def input_changed(*args):
    print(f"SD Lora Tagger: {args}")


def register_pages():
    extra_pages.clear()
    register_embeddings(os.path.join(lora_tagger_dir, "network_descriptions/embeddings/"))
    register_hypernetworks(os.path.join(lora_tagger_dir, "network_descriptions/hypernetworks/"))
    register_checkpoints(os.path.join(lora_tagger_dir, "network_descriptions/Stable-diffusion/"))
    register_loras(os.path.join(lora_tagger_dir, "network_descriptions/Lora/"))


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
                                                                f"\n{os.listdir(f'./{lora_tagger_dir}/../../models/Lora/')}"))

        except KeyError:
            pass

    def before_component(self, component, **kwargs):
        global pos_prompt_comp
        try:
            if kwargs["elem_id"] == "txt2img_prompt":
                pos_prompt_comp = component

            """ if kwargs["elem_id"] == "txt2img_extra_search":
                with gr.Row() as new_layout:
                    tag_search_dropdown = gr.Dropdown(info="Search by tags...", multiselect=True,
                                                      show_label=False, choices=list(load_tags(os.path.join(lora_tagger_dir, "network_descriptions/")).keys()))
                    tag_search_dropdown.input(fn=input_changed, inputs=tag_search_dropdown)
                    name_search = component
                return new_layout """

        except KeyError:
            pass


script_callbacks.on_before_ui(register_pages)
