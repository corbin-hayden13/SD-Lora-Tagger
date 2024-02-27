import json
import os
import re

from scripts.helpers.paths import tags_path, ui_config_path, ui_config_debug
from scripts.helpers.utils import csv_to_list, list_to_csv
from scripts.globals import network_descriptions_path

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
    if not os.path.isdir(network_descriptions_path):
        os.mkdir(network_descriptions_path)
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



def add_tag(new_tag: Tag = None, index = 0):
    """
    Adds a new tag at the given index (default: 0), creates a new tag using default values if 'new_tag' is not provided.
    """
    if new_tag is not None:
        new_tag.name = avoid_duplicate(new_tag.name)
        tags.insert(index, new_tag)
        return to_dataframe()

    tag = Tag(name='new_tag', description='new description', models=[])
    tag.name = avoid_duplicate(tag.name)
    # Add the tag to the start of the list for graphical convenience
    tags.insert(index, tag)
    return to_dataframe()


def remove_tag(index = -1):
    """
    Removes a tag from the provided index. Removes the last item by default
    """
    tags.pop(index)
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
    

def avoid_duplicate(tag_name: str, exclude_current = False):
    """
    Checks tags with the same name exists, and generates a unique suffix if it does.

    Parameters:
        exclude_current - Whether or not to exclude the current entry from the dupe check (use if calling before the current tag is loaded)
    """
    count = 0
    for tag in tags:
        if tag.name == tag_name:
            count += 1
    if count > 1 or (not exclude_current and count > 0):
        return generate_suffix_recursive(tag_name)
    return tag_name


def generate_suffix_recursive(tag_name: str, i = 0) -> str: 
    """
    Recursive function to avoid duplicate tag names
    """
    if get_tag_by_name(f'{tag_name}_{i}') is not None:
        return generate_suffix_recursive(tag_name, i+1)
    
    return f'{tag_name}_{i}'