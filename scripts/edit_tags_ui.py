import os
import glob
import gradio as gr

import modules.shared as shared

from scripts.globals import update_hide_nsfw, hide_nsfw, network_descriptions_path

from scripts.helpers.paths import base_dir

global all_tags, all_txt_files


def populate_all_tags():
    global all_tags, all_txt_files

    txt_pattern = os.path.join(f"{network_descriptions_path}/**/*.txt")
    print(f"SD Lora Tagger UI: txt_pattern={txt_pattern}")
    all_txt_files = glob.glob(txt_pattern, recursive=True)
    all_tags = {}

    for file in all_txt_files:
        file_name = os.path.basename(file).split(".")[0]

        with open(file, "r", encoding='utf-8') as f:
            file_data = f.read()
            for tag in file_data.split(","):
                try:
                    all_tags[tag].append(file_name)
                except KeyError:
                    all_tags[tag] = [file_name]


def save_text(*args):
    global all_tags

    file_path = args[0]["label"]
    tags = args[1]
    file_name = os.path.basename(file_path).split(".")[0]

    with open(file_path, "w", encoding='utf-8') as f:
        if tags.startswith(file_name):
            f.write(tags)
        else:
            f.write(f'{file_name}, {tags}')

    populate_all_tags()

    return [gr.Dropdown.update(choices=list(all_tags.keys())),
            gr.Textbox.update(value=tags)]


def refresh_txt_files():
    pass


def search_extra_networks(*args):
    update_hide_nsfw()

    dropdown = args[0]
    rows = args[1:]
    # If nothing is in the dropdown / no tags are being searched
    if len(dropdown) <= 0:
        ret_list = [gr.Dropdown.update()]
        for a in range(1, len(args), 2):
            if "nsfw" in rows[a] and hide_nsfw:
                ret_list.append(gr.Textbox().update(visible=False, container=False))
                ret_list.append(gr.Button().update(visible=False))

            else:
                ret_list.append(gr.Textbox().update(visible=True, container=True))
                ret_list.append(gr.Button().update(visible=True))

        return ret_list

    new_rows = [gr.Dropdown().update()]
    for a in range(0, len(rows), 2):
        if "nsfw" in rows[a] and hide_nsfw:
            new_rows.append(gr.Textbox().update(visible=False, container=False))
            new_rows.append(gr.Button().update(visible=False))
            continue

        for tag in dropdown:
            if tag in rows[a]:
                new_rows.append(gr.Textbox().update(visible=True, container=True))
                new_rows.append(gr.Button().update(visible=True))

            else:
                new_rows.append(gr.Textbox().update(visible=False, container=False))
                new_rows.append(gr.Button().update(visible=False))

    return new_rows


def on_ui_tabs():
    update_hide_nsfw()
    print(f"SD Lora Tagger: hide_nsfw={hide_nsfw}")

    with gr.Blocks() as sd_lora_tagger:
        search_bar = gr.Dropdown(label="Search By File Name or Tags", multiselect=True,
                                 choices=list(all_tags.keys()))
        with gr.Column():
            file_rows = [search_bar]
            for txt_file in all_txt_files:
                file_name = os.path.basename(txt_file).split(".")[0]
                file_data = ''

                with open(txt_file, "r", encoding='utf8') as f:
                    data = f.read()
                    file_data = data.replace(f"{file_name}, ", "") # Exclude file name as it is not a tag (will still be added on save)
                    #print(f'{file_name}: "{file_data}"') 

                set_visible = not ("nsfw" in file_data.lower().split(",") and hide_nsfw)

                with gr.Row(elem_id=f"{file_name}_row_container", equal_height=True) as new_file_row:
                    with gr.Column(elem_id=f"{file_name}_textbox_col", scale=7):
                        
                        # Adds file path to info for later reference when saving
                        textbox = gr.Textbox(label=file_name, value=file_data, elem_id=f"{file_name}_textbox",
                                             visible=set_visible)

                        file_rows.append(textbox)

                    with gr.Column(scale=2):
                        save_btn = gr.Button(value="Save", elem_id=f"{file_name}_save_btn",  visible=set_visible)
                        save_btn.click(fn=save_text, inputs=[gr.Label(value=txt_file, visible=False), textbox],
                                       outputs=[search_bar, textbox])

                        file_rows.append(save_btn)

        search_bar.input(fn=search_extra_networks, inputs=file_rows, outputs=file_rows)
        # for entry in file_rows:
        #     if isinstance(entry, gr.Textbox):
        #         print(f'{entry.label}: "{entry.value}"')

    return [(sd_lora_tagger, "SD Lora Tagger", "sd_lora_tagger")]


def on_ui_settings():
    section = ("sd_lora_tagger", "SD Lora Tagger")
    shared.opts.add_option("sd_lora_tagger_hide_nsfw_extra_networks",
                           shared.OptionInfo(False, "Hide NSFW-tagged extra networks", section=section))
    update_hide_nsfw()

