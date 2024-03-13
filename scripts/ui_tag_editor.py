import gradio as gr
from scripts.api.tag_api import TagManagerAPI
from scripts.api.extras_api import ExtrasAPI

class TagEditorUI():
    tag_api: TagManagerAPI
    extras_api: ExtrasAPI
    def __init__(self, api: TagManagerAPI, extras: ExtrasAPI = None):
        self.tag_api = api
        self.extras_api = extras
        self.tag_api.load_tags()


    def toggle_component(self, val):
        variant = lambda v: 'primary' if v else 'secondary'
        return gr.update(interactive=val, variant=variant(val))
    

    def save(self, *args):
        if args[0]:
            self.tag_api.save(args[1])
            return self.toggle_component(False)
        return self.toggle_component(True)
    
    def save_manual(self, *args):
        return self.toggle_component(False), self.tag_api.save(args[0])
    

    def remove_row(self, index):
        update = self.toggle_component(True)
        data = self.tag_api.del_row(int(index))
        if len(data) == 0:
            update = self.toggle_component(False)
            
        return (data, update)
    

    def add_row(self, data):
        return self.tag_api.add_row(data), self.toggle_component(True)


    def on_ui_tabs(self):
        print(f'SD_Lora_Tagger: Loading UI (using {self.tag_api.name})')
        with gr.Blocks() as sd_lora_tagger:
            with gr.Row():
                with gr.Column(scale=6):
                    with gr.Row():
                        add_btn = gr.Button(value="Add", variant='primary', scale=4)
                        rem_btn = gr.Button(value="Remove", variant='primary', scale=4)
                        index_num = gr.Number(value=-1, label="Row Index", scale=1, min_width=100)
                        search_txt = gr.Textbox(placeholder="Search...", label="Search", scale=25)
                        
        
                    with gr.Row():
                        sort_dropdown = gr.Dropdown(self.tag_api.get_sort_methods(), value='Alphabetically', label="Sort", scale=3)
                        save_btn = gr.Button(value="Save", scale=3, interactive=False)
                        save_chk = gr.Checkbox(label="Auto Save", scale=2)
                        gr.Column(scale=16)
                        save_btn.update(interactive=False)

                with gr.Column(scale=4):
                    if self.extras_api is not None:
                        gr.Row() # this, for some miraculous reason, aligns the content almost perfectly
                        with gr.Row():
                            self.extras_api.create()
                            
            with gr.Row():
                data = self.tag_api.read_all_tags()
                table = gr.Matrix(
                    data,
                    headers=self.tag_api.get_headers(),
                    datatype=['str', 'str', 'str'],
                    row_count=(len(data), 'dynamic'),
                    col_count=self.tag_api.get_col_count(),
                    height=522, # fit perfectly on my screen, might be worth introducing an option for this?
                    interactive=True
                )
                print(f'DATAFRAME ROWS: {table.row_count[0]}')
                add_btn.click(fn=self.add_row, inputs=[table], outputs=[table, rem_btn])
                rem_btn.click(fn=self.remove_row, inputs=[index_num], outputs=[table, rem_btn])
                save_btn.click(fn=self.save_manual, inputs=[table], outputs=[save_btn, table])
                save_chk.change(fn=lambda val: self.toggle_component(not val), inputs=[save_chk], outputs=[save_btn])

                # This needs some attention. Currently it will never be completely updated without passing
                # in the dataframe as an input, which results in not being able to retrieve it's value
                table.change(fn=self.save, inputs=[save_chk, table], outputs=[save_btn])

                search_txt.input(fn=self.tag_api.search, inputs=[search_txt], outputs=[table])
                sort_dropdown.input(fn=self.tag_api.sort, inputs=[sort_dropdown], outputs=[table])
                if self.extras_api is not None:
                    self.extras_api.bind_table(table)
           
        return [(sd_lora_tagger, "Tag Editor", "sd_lora_tagger")]