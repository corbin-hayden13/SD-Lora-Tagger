import gradio as gr
from ischedule import schedule, run_loop

class ExtrasAPI():
    """
    A generic API for creating extras in a decoupled way

    Variables:
        min_max_height: Tuple[int, int] - Used in the table to determine it's height. The first default value is based on an open accordion with a single button inside, while the 2nd value is a closed accordion.

    Methods:
        create() - Creates the UI for extras
        bind_table() - Binds the table to be dynamically resized
    """
    
    table = None
    min_max_height = (522, 522) # Change if the extras tab extends beyond other UI
    __open__ = False
    __js_container__: gr.TextArea = None

    def create(self, label='Extras') -> gr.Accordion:
        """
        When overriding, use `super().create()` in inheritors to properly implement accordion update logic.

        ### Implementation Example
        ```python
        with super().create() as extras:
            # more components & logic
        
        return extras
        ```
        """
        with gr.Accordion(label, open=False, elem_id="sd_lora_tagger_extras") as accordion:
            self.__js_container__ = gr.TextArea(elem_id="sd_lora_tagger_container", visible=False)
        return accordion
    
    def bind_table(self, table: gr.Matrix):
        self.__js_container__.change(self.__update_state_internal, inputs=self.__js_container__, outputs=table)
        self.table = table
    
    def __update_state_internal(self, state):
        self.__open__ = bool(int(state)) # Convert string to bool (ex. "0" -> False)
        return gr.update(height = self.min_max_height[0] if self.__open__ else self.min_max_height[1])
