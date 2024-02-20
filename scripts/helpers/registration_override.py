import os
import json
import html

from modules import ui_extra_networks, sd_hijack, shared, sd_models, extra_networks
from modules.textual_inversion.textual_inversion import Embedding

from scripts.helpers.utils import lora, lycoris, extra_networks_lora, get_or_create_tags_file
from scripts.globals import update_hide_nsfw


lora_exists = lora is not None
lycoris_exists = lycoris is not None


class EmbeddingsPage(ui_extra_networks.ExtraNetworksPage):
    def __init__(self, descriptions_path, extras=None):
        super().__init__('Textual Inversion')
        self.allow_negative_prompt = True
        self.descriptions_path = descriptions_path
        self.extras = extras

    def refresh(self):
        self.extras = update_hide_nsfw(self.extras)
        sd_hijack.model_hijack.embedding_db.load_textual_inversion_embeddings(force_reload=True)

    def list_items(self):
        self.extras = update_hide_nsfw(self.extras)
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

            search_terms = get_or_create_tags_file(self.descriptions_path, embedding.filename)

            yield_dict = {
                "name": os.path.splitext(embedding.name)[0],
                "filename": embedding.filename,
                "preview": self.find_preview(path),
                "description": f"{self.find_description(path)}|||{self.extras}",  # self.find_description(path),
                "search_term": search_terms,  # self.search_terms_from_path(embedding.filename),
                "prompt": json.dumps(os.path.splitext(embedding.name)[0]),
                "local_preview": f"{path}.preview.{shared.opts.samples_format}",
            }

            yield yield_dict

    def allowed_directories_for_previews(self):
        default = list(sd_hijack.model_hijack.embedding_db.embedding_dirs)
        default.append(self.descriptions_path)
        return default


class HypernetworksPage(ui_extra_networks.ExtraNetworksPage):
    def __init__(self, descriptions_path, extras=None):
        super().__init__('Hypernetworks')
        self.descriptions_path = descriptions_path
        self.extras = extras

    def refresh(self):
        self.extras = update_hide_nsfw(self.extras)
        shared.reload_hypernetworks()

    def list_items(self):
        self.extras = update_hide_nsfw(self.extras)
        for name, path in shared.hypernetworks.items():
            path, _ext = os.path.splitext(path)

            search_terms = get_or_create_tags_file(self.descriptions_path, path)

            yield_dict = {
                "name": name,
                "filename": path,
                "preview": self.find_preview(path),
                "description": f"{self.find_description(path)}|||{self.extras}",  # self.find_description(path),
                "search_term": search_terms,  # self.search_terms_from_path(path),
                "prompt": json.dumps(f"<hypernet:{name}:{shared.opts.extra_networks_default_multiplier}>"),
                "local_preview": f"{path}.preview.{shared.opts.samples_format}",
            }

            yield yield_dict

    def allowed_directories_for_previews(self):
        try:
            network_dir = shared.opts.hypernetwork_dir
        except AttributeError:  # For use in AUTOMATIC1111/stable-diffusion-webui
            network_dir = shared.cmd_opts.hypernetwork_dir

        return [network_dir, self.descriptions_path]


class CheckpointsPage(ui_extra_networks.ExtraNetworksPage):
    def __init__(self, descriptions_path, extras=None):
        super().__init__('Checkpoints')
        self.descriptions_path = descriptions_path
        self.extras = extras

    def refresh(self):
        self.extras = update_hide_nsfw(self.extras)
        shared.refresh_checkpoints()

    def list_items(self):
        checkpoint: sd_models.CheckpointInfo
        self.extras = update_hide_nsfw(self.extras)
        for name, checkpoint in sd_models.checkpoints_list.items():
            path, _ext = os.path.splitext(checkpoint.filename)

            search_terms = get_or_create_tags_file(self.descriptions_path, checkpoint.filename)

            yield_dict = {
                "name": checkpoint.name_for_extra,
                "filename": path,
                "fullname": checkpoint.filename,
                "hash": checkpoint.shorthash,
                "preview": self.find_preview(path),
                "description": f"{self.find_description(path)}|||{self.extras}",  # self.find_description(path),
                "search_term": search_terms,  # f'{self.search_terms_from_path(checkpoint.filename)} {(checkpoint.sha256 or "")} /{checkpoint.type}/',
                "onclick": '"' + html.escape(f"""return selectCheckpoint({json.dumps(name)})""") + '"',
                "local_preview": f"{path}.{shared.opts.samples_format}",
                "metadata": checkpoint.metadata,
            }

            yield yield_dict

    def allowed_directories_for_previews(self):
        try:
            valid_paths = [shared.opts.ckpt_dir, shared.opts.diffusers_dir, sd_models.model_path]
        except AttributeError:  # For use in AUTOMATIC1111/stable-diffusion-webui
            valid_paths = [shared.cmd_opts.ckpt_dir, sd_models.model_path]

        default = [v for v in valid_paths if v is not None]
        default.append(self.descriptions_path)
        return default


class LoraPage(ui_extra_networks.ExtraNetworksPage):
    def __init__(self, descriptions_path, extras=None):
        super().__init__('Lora')
        self.descriptions_path = descriptions_path
        self.extras = extras

    def refresh(self):
        self.extras = update_hide_nsfw(self.extras)
        lora.list_available_loras()

    def list_items(self):
        self.extras = update_hide_nsfw(self.extras)
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

            search_terms = get_or_create_tags_file(self.descriptions_path, lora_on_disk.filename)

            yield_dict = {
                "name": name,
                "filename": path,
                "fullname": lora_on_disk.filename,
                "hash": lora_on_disk.shorthash,
                "preview": self.find_preview(path),
                "description": f"{self.find_description(path)}|||{self.extras}",  # self.find_description(path),
                "search_term": search_terms,  # self.search_terms_from_path(lora_on_disk.filename),
                "prompt": prompt,
                "local_preview": f"{path}.{shared.opts.samples_format}",
                "metadata": metadata,
                "tags": tags,
            }

            yield yield_dict

    def allowed_directories_for_previews(self):
        return [shared.cmd_opts.lora_dir]


class LyCORISPage(ui_extra_networks.ExtraNetworksPage):
    def __init__(self, descriptions_path, base_name='lyco', model_dir=None, extras=None):
        super().__init__('LyCORIS')
        # If LyCORIS is not installed, cannot pre-compute shared.cmd_opts.lyco_dir so it cannot be a default arg
        if model_dir is None:
            self.model_dir = shared.cmd_opts.lyco_dir
        else:
            self.model_dir = model_dir
        self.descriptions_path = descriptions_path
        self.base_name = base_name
        self.extras = extras

    def refresh(self):
        self.extras = update_hide_nsfw(self.extras)
        lycoris.list_available_lycos(self.model_dir)

    def list_items(self):
        self.extras = update_hide_nsfw(self.extras)
        for index, (name, lyco_on_disk) in enumerate(lycoris.available_lycos.items()):
            path, ext = os.path.splitext(lyco_on_disk.filename)
            sort_keys = {} if not 'get_sort_keys' in dir(self) else self.get_sort_keys(lyco_on_disk.filename)

            search_terms = get_or_create_tags_file(self.descriptions_path, lyco_on_disk.filename)

            yield_dict = {
                "name": name,
                "filename": path,
                "preview": self.find_preview(path),
                "description": f"{self.find_description(path)}|||{self.extras}",  # self.find_description(path),
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

            yield yield_dict

    def allowed_directories_for_previews(self):
        return [self.model_dir]


def register_embeddings(descriptions_path, extras: str):
    ui_extra_networks.register_page(EmbeddingsPage(descriptions_path, extras=extras))


def register_hypernetworks(descriptions_path, extras: str):
    ui_extra_networks.register_page(HypernetworksPage(descriptions_path, extras=extras))


def register_checkpoints(descriptions_path, extras: str):
    ui_extra_networks.register_page(CheckpointsPage(descriptions_path, extras=extras))


def register_loras(descriptions_path, extras: str):
    ui_extra_networks.register_page(LoraPage(descriptions_path, extras=extras))


def register_lycos(descriptions_path, extras: str):
    ui_extra_networks.register_page(LyCORISPage(descriptions_path, extras=extras))


def register_all(description_paths, extras: str):
    embedding_path, hypernetwork_path, checkpoint_path, lora_path, lycos_path = description_paths
    register_embeddings(embedding_path, extras)
    register_hypernetworks(hypernetwork_path, extras)
    register_checkpoints(checkpoint_path, extras)
    if lora_exists:
        register_loras(lora_path, extras)
        extra_networks.register_extra_network(extra_networks_lora.ExtraNetworkLora())
    if lycoris_exists:
        register_lycos(lycos_path, extras)

