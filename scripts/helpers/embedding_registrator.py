import os
import json

from modules import ui_extra_networks, sd_hijack, shared
from modules.textual_inversion.textual_inversion import Embedding


class EmbeddingsPage(ui_extra_networks.ExtraNetworksPage):
    def __init__(self, descriptions_path):
        super().__init__('Textual Inversion')
        self.allow_negative_prompt = True
        self.descriptions_path = descriptions_path

    def refresh(self):
        sd_hijack.model_hijack.embedding_db.load_textual_inversion_embeddings(force_reload=True)

    def list_items(self):
        embeddings = list(sd_hijack.model_hijack.embedding_db.word_embeddings.values())
        if len(embeddings) == 0: # maybe not loaded yet, so lets just look them up
            for root, _dirs, fns in os.walk(shared.opts.embeddings_dir, followlinks=True):
                for fn in fns:
                    if fn.lower().endswith(".pt"):
                        embedding = Embedding(0, fn)
                        embedding.filename = os.path.join(root, fn)
                        embeddings.append(embedding)
        for embedding in embeddings:
            path, _ext = os.path.splitext(embedding.filename)
            edited_filename = embedding.filename.replace("\\", "/")
            edited_filename = edited_filename.split("/")[-1]
            with open(os.path.join(self.descriptions_path, f"{edited_filename.split('.')[0]}.txt")) as f:
                search_terms = f.read()
                print(f"SD Lora Tagger: {search_terms}")

            yield {
                "name": os.path.splitext(embedding.name)[0],
                "filename": embedding.filename,
                "preview": self.find_preview(path),
                "description": self.find_description(path),
                "search_term": search_terms,  # self.search_terms_from_path(embedding.filename),
                "prompt": json.dumps(os.path.splitext(embedding.name)[0]),
                "local_preview": f"{path}.preview.{shared.opts.samples_format}",
            }

    def allowed_directories_for_previews(self):
        default = list(sd_hijack.model_hijack.embedding_db.embedding_dirs)
        default.append(self.descriptions_path)
        return default


def register_embeddings(descriptions_path):
    ui_extra_networks.register_page(EmbeddingsPage(descriptions_path))

