import json
import os

import modules.ui
from scripts.helpers.paths import tags_path, ui_config_path, ui_config_debug

class Tag(object):
    name: str
    description: str
    models: list[str]

    def __init__(self, js: dict = None, name = '', description = '', models = []):
        if js is not None:
            self.name = None if 'name' not in js else js['name']
            self.description = None if 'description' not in js else js['description']
            self.models = None if 'models' not in js else js['models']
        else:
            self.name = name
            self.description = description
            self.models = models
    
    def toJSON(self):
        return self.__dict__
    
    def models_to_string(self):
        output = ', '.join(self.models)
        print(output)
        return output # Whitespaces should probably be trimmed when saving

tags: list[Tag] = []

def update_cache():
    text = ""
    print(ui_config_path)
    with open(ui_config_path, 'r', encoding='utf8') as f:
        text = f.read()

    # with open(ui_config_debug, 'w', encoding='utf8') as fd:
    #     fd.write(text)  
    
    js = json.loads(text)

    for tag in tags:
        js[f'sd_lora_tagger/Models ({tag.name})/value'] = tag.models_to_string()
        js[f'sd_lora_tagger/Description ({tag.name})/value'] = tag.description

    with open(ui_config_path, 'w', encoding='utf8') as fw:
        text = fw.write(json.dumps(js, indent=4))

def get_or_create_tags_file() -> str:
    if os.path.exists(tags_path):
        with open(tags_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print('SD-Lora-Tagger: Tags file did not exist, creating one...')
        with open(tags_path, 'w', encoding='utf-8') as f:
            try:
                return f.write('')
            except FileNotFoundError as e:
                print(f'SD-Lora-Tagger: Failed to create tag file\n{e}')


def load_tags():
    js = get_or_create_tags_file()

    count = 0
    for obj in json.loads(js):
        tags.append(Tag(obj))
        count += 1
    
    print(f'SD-Lora-Tagger: Loaded {count} tags')

    
def to_dataframe():
    output = []

    for tag in tags:
        row = []
        row.append(tag.name)
        row.append(tag.description)
        row.append(len(tag.models))
        output.append(row)
    
    return output

def save_tags():
    # This feels very wrong, probably worth replacing
    data = []
    for tag in tags:
        data.append(tag.toJSON())
    
    js = json.dumps(data)

    with open(tags_path, 'w', encoding='utf-8') as f:
        f.write(js)
    
    update_cache()

def edit_tag(*args):
    tag_name = args[0]["label"]
    description = args[1]
    models = []
    for model in args[2].split(', '):
        models.append(model)
    
    tag = get_tag_by_name(tag_name)
    tag.description = description
    tag.models = models
    save_tags() # temporary

def get_tag_by_name(name: str):
    for tag in tags:
        if tag.name == name:
            return tag
    return None