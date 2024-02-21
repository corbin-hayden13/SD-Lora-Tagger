import scripts.helpers.tag_manager as tm
import gradio as gr
from gradio.blocks import BlockContext
from gradio import DataFrame

file_rows = []
tag_rows = []
def add_tag_ui(*args):
    block: BlockContext = args[0]
    tag = tm.Tag(name='new_tag', description='new description') 
    with gr.Row(elem_id=f"{tag.name}_row_container") as ui:
        with gr.Column(elem_id=f"{tag.name}_label_row_container", scale=2):
            label = gr.Label(elem_id=f'{tag.name}_label', value=tag.name)
            file_rows.append(label)
        with gr.Column(elem_id=f"{tag.name}_description_row_container", scale=3):
            desc_textbox = gr.Textbox(tag.description, elem_id=f"{tag.name}_desc_textbox")
            file_rows.append(desc_textbox)
        with gr.Column(elem_id=f"{tag.name}_models_row_container", scale=3):
            models_textbox = gr.Textbox(tag.models_to_string(), elem_id=f"{tag.name}_models_textbox")
            file_rows.append(models_textbox)
        with gr.Column(scale=2):
            save_btn = gr.Button(value="Save", elem_id=f"{tag.name}_save_btn")
            save_btn.click(fn=tm.edit_tag, inputs=[gr.Label(value=tag.name, visible=False), desc_textbox, models_textbox])
            file_rows.append(save_btn)
    block.add_child(ui)
        
def add_row():
    data = tm.to_dataframe()
    new_data = ['new_tag', 'new description', 0]
    data.append(new_data)
    return data

def on_ui_tabs():
    tm.load_tags()
    with gr.Blocks() as sd_lora_tagger:
        with gr.Column():
            with gr.Row():
                with gr.Column():
                    add_btn = gr.Button(value="Add", variant='primary')
                    with gr.Row():
                        frame = gr.Dataframe(
                            tm.to_dataframe(),
                            headers=['tag', 'description', 'count'],
                            datatype=['str', 'str', 'number'],
                            row_count=(5, 'dynamic'),
                            col_count=(3, 'fixed'),
                            interactive=True
                        )
                        print(f'DATAFRAME ROWS: {frame.row_count[0]}')
                        add_btn.click(fn=add_row, outputs=[frame])
                    
        #     for tag in tm.tags:
        #         with gr.Row(elem_id=f"{tag.name}_row_container") as tag_row:
        #             with gr.Column(elem_id=f"{tag.name}_label_row_container", scale=2):
        #                 name_textbox = gr.Textbox(elem_id=f'{tag.name}_label', value=tag.name)
        #                 file_rows.append(name_textbox)
        #             with gr.Column(elem_id=f"{tag.name}_description_row_container", scale=3):
        #                 desc_textbox = gr.Textbox(tag.description, elem_id=f"{tag.name}_desc_textbox")
        #                 file_rows.append(desc_textbox)
        #             with gr.Column(elem_id=f"{tag.name}_models_row_container", scale=3):
        #                 models_textbox = gr.Textbox(tag.models_to_string(), elem_id=f"{tag.name}_models_textbox")
        #                 file_rows.append(models_textbox)
        #             with gr.Column(scale=2):
        #                 save_btn = gr.Button(value="Save", variant='primary', elem_id=f"{tag.name}_save_btn")
        #                 save_btn.click(fn=tm.edit_tag, inputs=[name_textbox, desc_textbox, models_textbox])
        #                 file_rows.append(save_btn)
        # add_btn.click(fn=add_tag_ui, inputs=[sd_lora_tagger])
    return [(sd_lora_tagger, "Tag Editor", "sd_lora_tagger")]