import gradio as gr
from scripts.api.extras_api import ExtrasAPI
class ExtrasAPIv1(ExtrasAPI):

    def create(self) -> gr.Accordion:
        with super().create() as extras:
            gr.Button("Add all models", variant="primary")
            
        
        return extras