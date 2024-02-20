import json
import os

from scripts.helpers.paths import tags_path

class Tag(object):
    name: str
    description: str
    models: list[str]

    def __init__(self, js: dict):
        self.name = None if 'name' not in js else js['name']
        self.description = None if 'description' not in js else js['description']
        self.models = None if 'models' not in js else js['models']
    
    def toJSON(self):
        return self.__dict__
    
    def models_to_string(self):
        output = ', '.join(self.models)
        print(output)
        return output # Whitespaces should probably be trimmed when saving

tags: list[Tag] = []

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

    
def save_tags():
    # This feels very wrong, probably worth replacing
    data = []
    for tag in tags:
        data.append(tag.toJSON())
    
    js = json.dumps(data)

    with open(tags_path, 'w', encoding='utf-8') as f:
        f.write(js)

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