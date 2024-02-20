import os
import glob
import gradio as gr

import modules.scripts as scripts
import modules.shared as shared


global all_tags, all_txt_files


def populate_all_tags():
    global all_tags, all_txt_files

    txt_pattern = os.path.join(scripts.basedir(), "network_descriptions/**/*.txt")
    print(f"SD Lora Tagger UI: txt_pattern={txt_pattern}")
    all_txt_files = glob.glob(txt_pattern, recursive=True)
    all_tags = {}

    for file in all_txt_files:
        file_name = os.path.basename(file).split(".")[0]

        with open(file, "r") as f:
            file_data = f.read()
            for tag in file_data.split(","):
                try:
                    all_tags[tag].append(file_name)
                except KeyError:
                    all_tags[tag] = [file_name]


def save_text(*args):
    file_path = args[0]["label"]
    tags = args[1]

    with open(file_path, "w") as f:
        f.write(tags)

    populate_all_tags()

    return list(all_tags.keys())


def refresh_txt_files():
    pass


def search_extra_networks(*args):
    dropdown = args[0]
    rows = args[1:]
    # If nothing is in the dropdown / no tags are being searched
    if len(dropdown) <= 0:
        ret_list = [gr.Dropdown.update()]
        for a in range(1, len(args), 2):
            ret_list.append(gr.Textbox().update(visible=True))
            ret_list.append(gr.Button().update(visible=True))

        return ret_list

    new_rows = [gr.Dropdown().update()]
    for a in range(0, len(rows), 2):
        for tag in dropdown:
            if tag in rows[a]:
                new_rows.append(gr.Textbox().update(visible=True))
                new_rows.append(gr.Button().update(visible=True))

            else:
                new_rows.append(gr.Textbox().update(visible=False))
                new_rows.append(gr.Button().update(visible=False))

    return new_rows


def on_ui_tabs():
    with gr.Blocks() as sd_lora_tagger:
        search_bar = gr.Dropdown(label="Search By File Name or Tags", multiselect=True,
                                 choices=list(all_tags.keys()))
        with gr.Column():
            file_rows = [search_bar]
            for txt_file in all_txt_files:
                file_name = os.path.basename(txt_file).split(".")[0]

                with open(txt_file, "r") as f:
                    file_data = f.read()

                with gr.Row(elem_id=f"{file_name}_row_container") as new_file_row:
                    with gr.Column(elem_id=f"{file_name}_textbox_col", scale=7):
                        # Adds file path to info for later reference when saving
                        textbox = gr.Textbox(label=file_name, value=file_data, elem_id=f"{file_name}_textbox")

                        file_rows.append(textbox)

                    with gr.Column(scale=2):
                        save_btn = gr.Button(value="Save", elem_id=f"{file_name}_save_btn")
                        save_btn.click(fn=save_text, inputs=[gr.Label(value=txt_file, visible=False), textbox],
                                       outputs=[search_bar])

                        file_rows.append(save_btn)

        search_bar.input(fn=search_extra_networks, inputs=file_rows, outputs=file_rows)

    return [(sd_lora_tagger, "SD Lora Tagger", "sd_lora_tagger")]


def on_ui_settings():
    section = ("sd_lora_tagger", "SD Lora Tagger")
    shared.opts.add_option("sd_lora_tagger_hide_nsfw_extra_networks",
                           shared.OptionInfo(False, "Hide NSFW-tagged extra networks", section=section))

