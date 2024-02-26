import gradio as gr
from scripts.api.base import TagManagerAPI

class TagEditorUI():
    api: TagManagerAPI
    def __init__(self, api: TagManagerAPI):
        self.api = api
        self.api.load_tags()

    def toggle_component(self, val):
        variant = lambda v: 'primary' if v else 'secondary'
        return gr.update(interactive=val, variant=variant(val))
    
    def save(self, *args):
        if args[0]:
            return self.toggle_component(False), self.api.save(args[1])
        return self.toggle_component(True), gr.update(value=args[1])
    
    def remove_row(self):
        update = self.toggle_component(True)
        data = self.api.del_row()
        if len(data) == 0:
            update = self.toggle_component(False)
            
        return (data, update)
    
    def add_row(self):
        return self.api.add_row(), self.toggle_component(True)

    def on_ui_tabs(self):
        print(f'SD_Lora_Tagger: Loading UI (using {self.api.name})')
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
                            data = self.api.read_all_tags()
                            frame = gr.Matrix(
                                data,
                                headers=['tag', 'description', 'models'],
                                datatype=['str', 'str', 'str'],
                                row_count=(len(data), 'dynamic'),
                                col_count=(3, 'fixed'),
                                height=650, # fit perfectly on my screen, might be worth introducing an option for this?
                                interactive=True
                            )
                            print(f'DATAFRAME ROWS: {frame.row_count[0]}')
                            add_btn.click(fn=self.add_row, outputs=[frame, rem_btn])
                            rem_btn.click(fn=lambda _: self.remove_row(), outputs=[frame, rem_btn])
                            save_btn.click(fn=self.save, inputs=[gr.Checkbox(True, visible=False), frame], outputs=[save_btn, frame])
                            save_chk.change(fn=lambda val: self.toggle_component(not val), inputs=[save_chk], outputs=[save_btn])

                            # This needs some attention. Currently it will never be completely updated without passing
                            # in the dataframe as an input, which results in not being able to retrieve it's value
                            frame.change(fn=self.save, inputs=[save_chk, frame], outputs=[save_btn, frame])

                            search_txt.input(fn=lambda text:self.api.search(text), inputs=[search_txt], outputs=[frame])
        return [(sd_lora_tagger, "Tag Editor", "sd_lora_tagger")]