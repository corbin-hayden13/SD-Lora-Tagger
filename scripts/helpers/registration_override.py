import os
import json
import html

from modules import ui_extra_networks, sd_hijack, shared, sd_models
from modules.textual_inversion.textual_inversion import Embedding


def parse_filename(path):
    edited_filename = path.replace("\\", "/")
    return edited_filename.split("/")[-1]


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
            with open(os.path.join(self.descriptions_path, f"{parse_filename(embedding.filename).split('.')[0]}.txt")) as f:
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


class HypernetworksPage(ui_extra_networks.ExtraNetworksPage):
    def __init__(self, descriptions_path):
        super().__init__('Hypernetworks')
        self.descriptions_path = descriptions_path

    def refresh(self):
        shared.reload_hypernetworks()

    def list_items(self):
        for name, path in shared.hypernetworks.items():
            path, _ext = os.path.splitext(path)

            with open(os.path.join(self.descriptions_path, f"{parse_filename(path).split('.')[0]}.txt")) as f:
                search_terms = f.read()
                print(f"SD Lora Tagger: {search_terms}")

            yield {
                "name": name,
                "filename": path,
                "preview": self.find_preview(path),
                "description": self.find_description(path),
                "search_term": search_terms,  # self.search_terms_from_path(path),
                "prompt": json.dumps(f"<hypernet:{name}:{shared.opts.extra_networks_default_multiplier}>"),
                "local_preview": f"{path}.preview.{shared.opts.samples_format}",
            }

    def allowed_directories_for_previews(self):
        return [shared.opts.hypernetwork_dir, self.descriptions_path]


class CheckpointsPage(ui_extra_networks.ExtraNetworksPage):
    def __init__(self, descriptions_path):
        super().__init__('Checkpoints')
        self.descriptions_path = descriptions_path

    def refresh(self):
        shared.refresh_checkpoints()

    def list_items(self):
        checkpoint: sd_models.CheckpointInfo
        for name, checkpoint in sd_models.checkpoints_list.items():
            path, _ext = os.path.splitext(checkpoint.filename)

            with open(os.path.join(self.descriptions_path, f"{parse_filename(checkpoint.filename).split('.')[0]}.txt")) as f:
                search_terms = f.read()
                print(f"SD Lora Tagger: {search_terms}")

            yield {
                "name": checkpoint.name_for_extra,
                "filename": path,
                "fullname": checkpoint.filename,
                "hash": checkpoint.shorthash,
                "preview": self.find_preview(path),
                "description": self.find_description(path),
                "search_term": search_terms,  # f'{self.search_terms_from_path(checkpoint.filename)} {(checkpoint.sha256 or "")} /{checkpoint.type}/',
                "onclick": '"' + html.escape(f"""return selectCheckpoint({json.dumps(name)})""") + '"',
                "local_preview": f"{path}.{shared.opts.samples_format}",
                "metadata": checkpoint.metadata,
            }

    def allowed_directories_for_previews(self):
        default = [v for v in [shared.opts.ckpt_dir, shared.opts.diffusers_dir, sd_models.model_path] if v is not None]
        default.append(self.descriptions_path)
        return default


def register_embeddings(descriptions_path):
    ui_extra_networks.register_page(EmbeddingsPage(descriptions_path))


def register_hypernetworks(descriptions_path):
    ui_extra_networks.register_page(HypernetworksPage(descriptions_path))


def register_checkpoints(descriptions_path):
    ui_extra_networks.register_page(CheckpointsPage(descriptions_path))


def register_loras():
    pass
