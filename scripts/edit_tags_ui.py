import os
import glob
import gradio as gr

import modules.scripts as scripts


def refresh_txt_files():
    pass


def on_ui_tabs():
    txt_pattern = os.path.join(scripts.basedir(), "network_descriptions/**/*.txt")
    all_txt_files = glob.glob(txt_pattern, recursive=True)

    with gr.Blocks() as sd_lora_tagger:
        search_bar = gr.Dropdown(label="Search By File Name or Tags", multiselect=True)
        with gr.Column():
            file_rows = []
            for file in all_txt_files:
                with gr.Row() as new_file_row:
                    with open(file, "r") as f:
                        textbox = gr.Textbox(value=f.read())

                    save_btn = gr.Button(value="Save")

                file_rows.append(new_file_row)

    return [(sd_lora_tagger, "SD Lora Tagger", "sd_lora_tagger")]

