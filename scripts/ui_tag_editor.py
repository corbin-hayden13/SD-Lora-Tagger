import scripts.helpers.tag_manager as tm
import gradio as gr
from gradio.blocks import BlockContext

def add_row():
    return tm.add_tag(), toggle_component(True)


def remove_row():
    update = toggle_component(True)
    data = tm.remove_tag()
    if len(data) == 0:
        update = toggle_component(False)
        
    return (data, update)


def save(*args, data=None):
    if args[0]:
        tm.save_changes(args[1] if data is None else data)
        return toggle_component(False)
    return toggle_component(True)


def toggle_component(val):
    variant = lambda v: 'primary' if v else 'secondary'
    return gr.update(interactive=val, variant=variant(val))


def on_ui_tabs():
    tm.load_tags()
    with gr.Blocks() as sd_lora_tagger:
        with gr.Column():
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        add_btn = gr.Button(value="Add", variant='primary', scale=3)
                        rem_btn = gr.Button(value="Remove", variant='primary', scale=3)
                        search_txt = gr.Textbox(placeholder="Search...", scale=20, show_label=False)
                        
                    with gr.Row():
                        save_btn = gr.Button(value="Save", scale=2, interactive=False)
                        save_chk = gr.Checkbox(label="Auto Save", scale=20)
                        save_btn.update(interactive=False)
                            
                        
                    with gr.Row():
                        data = tm.to_dataframe()
                        frame = gr.Dataframe(
                            data,
                            headers=['tag', 'description', 'models'],
                            datatype=['str', 'str', 'str'],
                            row_count=(len(data), 'dynamic'),
                            col_count=(3, 'fixed'),
                            height=650, # fit perfectly on my screen, might be worth introducing an option for this?
                            interactive=True
                        )
                        print(f'DATAFRAME ROWS: {frame.row_count[0]}')
                        add_btn.click(fn=add_row, outputs=[frame, rem_btn])
                        rem_btn.click(fn=lambda _: remove_row(), outputs=[frame, rem_btn])
                        save_btn.click(fn=lambda _: save(True, data=frame.value), outputs=[save_btn])
                        save_chk.change(fn=lambda val: toggle_component(not val), inputs=[save_chk], outputs=[save_btn])
                        frame.change(fn=lambda val: save(val, data=frame.value), inputs=[save_chk], outputs=[save_btn])

                        search_txt.input(fn=lambda text:tm.search(text), inputs=[search_txt], outputs=[frame])
    return [(sd_lora_tagger, "Tag Editor", "sd_lora_tagger")]