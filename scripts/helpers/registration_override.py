import os
import json
import html

from modules import ui_extra_networks, sd_hijack, shared, sd_models, extra_networks
from modules.textual_inversion.textual_inversion import Embedding

from scripts.helpers.utils import import_lora_lycoris


lora, extra_networks_lora, lycoris = import_lora_lycoris()
lora_exists = lora is not None
lycoris_exists = lycoris is not None


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
            try:
                embeddings_dir = shared.opts.embeddings_dir
            except AttributeError:
                embeddings_dir = shared.cmd_opts.embeddings_dir

            for root, _dirs, fns in os.walk(embeddings_dir, followlinks=True):
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
        try:
            network_dir = shared.opts.hypernetwork_dir
        except AttributeError:  # For use in AUTOMATIC1111/stable-diffusion-webui
            network_dir = shared.cmd_opts.hypernetwork_dir

        return [network_dir, self.descriptions_path]


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
        try:
            valid_paths = [shared.opts.ckpt_dir, shared.opts.diffusers_dir, sd_models.model_path]
        except AttributeError:  # For use in AUTOMATIC1111/stable-diffusion-webui
            valid_paths = [shared.cmd_opts.ckpt_dir, sd_models.model_path]

        default = [v for v in valid_paths if v is not None]
        default.append(self.descriptions_path)
        return default


class LoraPage(ui_extra_networks.ExtraNetworksPage):
    def __init__(self, descriptions_path):
        super().__init__('Lora')
        self.descriptions_path = descriptions_path

    def refresh(self):
        lora.list_available_loras()

    def list_items(self):
        for name, lora_on_disk in lora.available_loras.items():
            path, _ext = os.path.splitext(lora_on_disk.filename)
            alias = lora_on_disk.get_alias()
            prompt = (json.dumps(f"<lora:{alias}") + " + " + json.dumps(f':{shared.opts.extra_networks_default_multiplier}') + " + " + json.dumps(">"))
            metadata =  json.dumps(lora_on_disk.metadata, indent=4) if lora_on_disk.metadata else None
            possible_tags = lora_on_disk.metadata.get('ss_tag_frequency', {}) if lora_on_disk.metadata is not None else {}
            if isinstance(possible_tags, str):
                possible_tags = {}
                shared.log.debug(f'Lora has invalid metadata: {path}')
            tags = {}
            for tag in possible_tags.keys():
                if '_' not in tag:
                    tag = f'0_{tag}'
                words = tag.split('_', 1)
                tags[' '.join(words[1:])] = words[0]
            # shared.log.debug(f'Lora: {path}: name={name} alias={alias} tags={tags}')

            with open(os.path.join(self.descriptions_path, f"{parse_filename(lora_on_disk.filename).split('.')[0]}.txt")) as f:
                search_terms = f.read()
                print(f"SD Lora Tagger: {search_terms}")

            yield {
                "name": name,
                "filename": path,
                "fullname": lora_on_disk.filename,
                "hash": lora_on_disk.shorthash,
                "preview": self.find_preview(path),
                "description": self.find_description(path),
                "search_term": search_terms,  # self.search_terms_from_path(lora_on_disk.filename),
                "prompt": prompt,
                "local_preview": f"{path}.{shared.opts.samples_format}",
                "metadata": metadata,
                "tags": tags,
            }

    def allowed_directories_for_previews(self):
        return [shared.cmd_opts.lora_dir]


class LyCORISPage(ui_extra_networks.ExtraNetworksPage):
    def __init__(self, descriptions_path, base_name='lyco', model_dir=None):
        super().__init__('LyCORIS')
        # If LyCORIS is not installed, cannot pre-compute shared.cmd_opts.lyco_dir so it cannot be a default arg
        if model_dir is None:
            self.model_dir = shared.cmd_opts.lyco_dir
        else:
            self.model_dir = model_dir
        self.descriptions_path = descriptions_path
        self.base_name = base_name

    def refresh(self):
        lycoris.list_available_lycos(self.model_dir)

    def list_items(self):
        for index, (name, lyco_on_disk) in enumerate(lycoris.available_lycos.items()):
            path, ext = os.path.splitext(lyco_on_disk.filename)
            sort_keys = {} if not 'get_sort_keys' in dir(self) else self.get_sort_keys(lyco_on_disk.filename)

            with open(os.path.join(self.descriptions_path, f"{parse_filename(lyco_on_disk.filename).split('.')[0]}.txt")) as f:
                search_terms = f.read()
                print(f"SD Lora Tagger: {search_terms}")

            yield {
                "name": name,
                "filename": path,
                "preview": self.find_preview(path),
                "description": self.find_description(path),
                "search_term": search_terms,  # self.search_terms_from_path(lyco_on_disk.filename),
                "prompt": (
                    json.dumps(f"<{self.base_name}:{name}")
                    + " + " + json.dumps(f':{shared.opts.extra_networks_default_multiplier}')
                    + " + " + json.dumps(">")
                ),
                "local_preview": f"{path}.{shared.opts.samples_format}",
                "metadata": json.dumps(lyco_on_disk.metadata, indent=4) if lyco_on_disk.metadata else None,
                "sort_keys": {'default': index, **sort_keys},
            }

    def allowed_directories_for_previews(self):
        return [self.model_dir]


def register_embeddings(descriptions_path):
    ui_extra_networks.register_page(EmbeddingsPage(descriptions_path))


def register_hypernetworks(descriptions_path):
    ui_extra_networks.register_page(HypernetworksPage(descriptions_path))


def register_checkpoints(descriptions_path):
    ui_extra_networks.register_page(CheckpointsPage(descriptions_path))


def register_loras(descriptions_path):
    ui_extra_networks.register_page(LoraPage(descriptions_path))


def register_lycos(descriptions_path):
    ui_extra_networks.register_page(LyCORISPage(descriptions_path))


def register_all(description_paths):
    embedding_path, hypernetwork_path, checkpoint_path, lora_path, lycos_path = description_paths
    register_embeddings(embedding_path)
    register_hypernetworks(hypernetwork_path)
    register_checkpoints(checkpoint_path)
    if lora_exists:
        register_loras(lora_path)
        extra_networks.register_extra_network(extra_networks_lora.ExtraNetworkLora())
    if lycoris_exists: register_lycos(lycos_path)

