import json
import os
import re

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
        return output # Whitespaces should probably be trimmed when saving


tags: list[Tag] = []

def update_cache():
    text = ""
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
        tag = Tag(obj)
        tag.name = avoid_duplicate(tag.name)

        tags.append(tag)
        count += 1
    
    print(f'SD-Lora-Tagger: Loaded {count} tags')


def save_tags():
    # This feels very wrong, probably worth replacing
    data = []
    for tag in tags:
        tag.name = avoid_duplicate(tag.name)
        data.append(tag.toJSON())
    
    js = json.dumps(data, indent=4)

    with open(tags_path, 'w', encoding='utf-8') as f:
        f.write(js)
    
    update_cache()

def remove_tag(index = -1):
    tags.pop(index)
    return to_dataframe()


def save_changes(data):
    for item in data["data"]:
        tag = get_tag_by_name(item[0])
        if tag is None:
            tag = Tag()
            tags.append(tag)

        tag.name = item[0]
        tag.description = item[1]
        tag.models = csv_to_list(item[2])

    save_tags()


def search(search_term: str):
    if search_term == '' or search_term is None:
        return to_dataframe()
    
    filtered_tags = []
    for tag in tags:
        if search_term in f'{tag.name} {tag.description} {tag.models}':
            filtered_tags.append(tag)
    return to_dataframe(filtered_tags)


def add_tag():
    tag = Tag(name='new_tag', description='new description', models=[])
    tag.name = avoid_duplicate(tag.name)
    # Add the tag to the start of the list for graphical convenience
    tags.insert(0, tag)
    return to_dataframe()

# ----- UTILITY -----

def to_dataframe(data: list[Tag] = None):
    output = []
    if data is None:
        data = tags

    for tag in data:
        row = [tag.name, tag.description, tag.models_to_string()]
        output.append(row)
    
    return output


def csv_to_list(data) -> list:
    ls = []
    for item in data.replace(' ', '').split(', '): # remove whitespaces and seperate by comma
        ls.append(item)
    return ls


def get_tag_by_name(name: str):
    for tag in tags:
        if tag.name == name:
            return tag
    return None


def avoid_duplicate(tag_name: str, exclude_current = False):
    count = 0
    for tag in tags:
        if tag.name == tag_name:
            count += 1
    if count > 1 or (not exclude_current and count > 0):
        return generate_suffix_recursive(tag_name)
    return tag_name


"""
Recursive function to avoid duplicate tag names
"""
def generate_suffix_recursive(tag_name: str, i = 0) -> str: 
    if get_tag_by_name(f'{tag_name}_{i}') is not None:
        return generate_suffix_recursive(tag_name, i+1)
    
    return f'{tag_name}_{i}'