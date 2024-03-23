import json
import os
import re
from typing import Literal

from scripts.helpers.paths import tags_path, tags_path_d, ui_config_path, ui_config_debug
from scripts.helpers.utils import csv_to_list, list_to_csv
import scripts.globals as gl

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
    """
    NOT USED: Overwrites A1111's 'ui-config.json' file to update component values
    """
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
    if not os.path.isdir(gl.network_descriptions_path):
        os.mkdir(gl.network_descriptions_path)
    if not os.path.exists(tags_path):
        print('SD-Lora-Tagger: Tags file did not exist, creating one...')
        with open(tags_path, 'w', encoding='utf-8') as f:
            try:
                js = json.dumps([Tag(name='tag', description='An example tag to get you started', models=['my_model']).toJSON()])
                f.write(js)
                return js
            except FileNotFoundError as e:
                print(f'SD-Lora-Tagger: Failed to create tag file\n{e}')

    with open(tags_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_tags():
    """
    Loads all tags from JSON
    """
    js = get_or_create_tags_file()

    count = 0
    for obj in json.loads(js):
        tag = Tag(obj)
        tag.name = avoid_duplicate(tag.name)

        tags.append(tag)
        count += 1
    
    print(f'SD-Lora-Tagger: Loaded {count} tags')


def save_tags():
    """
    Saves all tags to JSON
    """
    # This feels very wrong, probably worth replacing
    data = []
    for tag in tags:
        tag.name = avoid_duplicate(tag.name, exclude_current=True)
        data.append(tag.toJSON())
    
    js = json.dumps(data, indent=4)

    with open(tags_path, 'w', encoding='utf-8') as f:
        f.write(js)

def save_tags_debug():
    """
    Saves all tags to JSON
    """
    # This feels very wrong, probably worth replacing
    data = []
    for tag in tags:
        tag.name = avoid_duplicate(tag.name, exclude_current=True)
        data.append(tag.toJSON())
    
    js = json.dumps(data, indent=4)

    with open(tags_path_d, 'w', encoding='utf-8') as f:
        f.write(js)


def add(new_tag: Tag = None, index = 0, method: Literal['tag', 'model'] = 'tag'):
    """
    Adds a new item at the given index (default: 0), creates a new tag using default values if 'new_tag' is not provided.
    """
    if method == 'model':
        t = get_tag_by_name(new_tag.name)
        if t is None:
            tags.insert(index, new_tag)
            return to_dataframe()
        if new_tag.models[-1] not in t.models:
            t.models.append(new_tag.models[-1])
        return to_dataframe()
        
    if new_tag is not None:
        new_tag.name = avoid_duplicate(new_tag.name)
        tags.insert(index, new_tag)
        return to_dataframe()

    tag = Tag(name='new_tag', description='new description', models=[])
    tag.name = avoid_duplicate(tag.name)
    # Add the tag to the start of the list for graphical convenience
    tags.insert(index, tag)
    return to_dataframe()


def update_tag(tag_name: str, description: str = None, models: list[str] = None, models_update_method: Literal['overwrite', 'append'] = 'append'):
    """
    Updates a tag based on the given parameters.

    #### Parameters:
    models_update_method - Whether to overwrite models, or append a new list over already existing models
    """
    tag: Tag = get_tag_by_name(tag_name)
    if tag is None:
        print(f"Tag with name '{tag_name}' not found, creating a new one...")
        tag = Tag(name=tag_name, models=models)
        tags.append(tag)
        return

    if description is not None:
        tag.description = description
    
    #print(f"{tag}: {models}")

    if models is not None:
        if models_update_method == 'overwrite':
            tag.models = models
        if models_update_method == 'append':
            print(f"----{tag_name}----")
            print(models)
            print(tag.models)
            for model in models:
                if model in tag.models:
                    continue
                tag.models.append(model)
    
    return tag

def remove_tag(tag_name):
    """
    Removes a tag from the provided index. Removes the last item by default
    """
    tag = get_tag_by_name(tag_name)
    if tag is not None:
        tags.remove(tag)
    return to_dataframe()


def remove_model_from_tag(model, tag) -> list[list[str]]:
    if tag is None:
        tag = ''
    t = get_tag_by_name(tag)
    print(f"{tag}: {model}")
    if t is not None:
        if model in t.models:
            print(f"remoivng {model} from {tag}")
            t.models.remove(model)
        
    return to_dataframe()


def save_changes(data):
    """
    Modifies tags according to the provided data
    """
    for item in data:
        tag = get_tag_by_name(item[0])
        if tag is None:
            tag = Tag()
            tags.append(tag)

        tag.name = item[0]
        tag.description = item[1]
        tag.models = csv_to_list(item[2])
        #print(f"name: '{tag.name}', \ndesc: '{tag.description}', \nmodels: '{list_to_csv(tag.models)}'\n")

    save_tags()


def search(search_term: str) -> list[list]:
    """
    Searches loaded tags based on the provided search term. Returns data for a dataframe
    """
    if search_term == '' or search_term is None:
        return to_dataframe()
    
    filtered_tags = []
    for tag in tags:
        if search_term in f'{tag.name} {tag.description} {tag.models}':
            filtered_tags.append(tag)
    return to_dataframe(filtered_tags)


# ----- UTILITY -----


def to_dataframe(data: list[Tag] = None):
    """
    Converts a list of tags to values readable by the Gradio DataFrame
    """
    output = []
    if data is None:
        data = tags

    for tag in data:
        row = [tag.name, tag.description, tag.models_to_string()]
        output.append(row)
    
    return output


def get_tagged_models(data: list[list[str]] = None) -> list[str]:
    if data is None:
        data = to_dataframe()
    
    models = []
    for row in data:
        for model in csv_to_list(row[2]):
            if str(model).lstrip() == '':
                continue
            if model not in models:
                models.append(model)
    return models



def get_tag_by_name(name: str):
    """
    Returns a tag with the provided name. Returns None if no tags with the provided name exists
    """
    for tag in tags:
        if tag.name == name:
            return tag
    return None


def get_tags_by_model(model_name: str) -> list[str]:
    """
    Returns a list of tags associated with the provided model
    """
    result = []
    for tag in tags:
        if model_name in tag.models:
            result.append(tag.name) 
    return result


def get_search_terms(model_name: str) -> str:
    """
    Parses tags into a search term readable by A1111
    """
    tags = get_tags_by_model(model_name)
    if len(tags) == 0:
        return ''
    return list_to_csv(tags)
    

def avoid_duplicate(name: str, exclude_current = False, method: Literal['tag', 'model'] = 'tag', data: list[list[str]] = None):
    """
    Checks tags with the same name exists, and generates a unique suffix if it does.

    Parameters:
        exclude_current - Whether or not to exclude the current entry from the dupe check (use if calling before the current tag is loaded)
    """
    count = 0
    
    if method == 'tag':
        for tag in tags:
            if tag.name == name:
                count += 1
    if method == 'model' and name in get_tagged_models(data):
        count += 1

    if count > 1 or (not exclude_current and count > 0):
        return generate_suffix_recursive(name, method=method, data=data)
    return name


def generate_suffix_recursive(tag_name: str, i = 0, method: Literal['tag', 'model'] = 'tag', data = None) -> str: 
    """
    Recursive function to avoid duplicate tag names
    """
    if method == 'tag':
        if get_tag_by_name(f'{tag_name}_{i}') is not None:
            return generate_suffix_recursive(tag_name, i+1, method, data)
    if method == 'model':
        if f'{tag_name}_{i}' in get_tagged_models(data):
            return generate_suffix_recursive(tag_name, i+1, method, data)
    
    return f'{tag_name}_{i}'