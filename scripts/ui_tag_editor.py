import scripts.helpers.tag_manager as tm
import gradio as gr

def on_ui_tabs():
    file_rows = []
    tm.load_tags()
    with gr.Blocks() as sd_lora_tagger:
        with gr.Column():
            for tag in tm.tags:
                with gr.Row(elem_id=f"{tag.name}_row_container"):
                    with gr.Column(elem_id=f"{tag.name}_label_row_container", scale=2):
                        label = gr.Label(elem_id=f'{tag.name}_label', value=tag.name)
                        file_rows.append(label)
                    with gr.Column(elem_id=f"{tag.name}_description_row_container", scale=3):
                        desc_textbox = gr.Textbox(tag.description, label=f'Description ({tag.name})', elem_id=f"{tag.name}_desc_textbox")
                        file_rows.append(desc_textbox)
                    with gr.Column(elem_id=f"{tag.name}_models_row_container", scale=3):
                        models_textbox = gr.Textbox(tag.models_to_string(), label=f"Models ({tag.name})", elem_id=f"{tag.name}_models_textbox")
                        file_rows.append(models_textbox)
                    with gr.Column(scale=2):
                        save_btn = gr.Button(value="Save", elem_id=f"{tag.name}_save_btn")
                        save_btn.click(fn=tm.edit_tag, inputs=[gr.Label(value=tag.name, visible=False), desc_textbox, models_textbox])
                        file_rows.append(save_btn)
    return [(sd_lora_tagger, "SD Lora Tagger", "sd_lora_tagger")]