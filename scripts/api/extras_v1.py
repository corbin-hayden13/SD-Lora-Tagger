import gradio as gr
from scripts.api.extras_api import ExtrasAPI
class ExtrasAPIv1(ExtrasAPI):

    def create(self, label='Extras') -> gr.Accordion:
        with super().create(label) as extras:
            with gr.Row():
                gr.Button("Add all models", variant="primary")
                gr.Button("Add CivitAI Tags", variant="primary")
            
        
        return extras