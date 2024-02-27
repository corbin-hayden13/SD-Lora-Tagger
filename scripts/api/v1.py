from scripts.api.base import TagManagerAPI
from scripts.helpers.utils import csv_to_list, list_to_csv

class TagManagerAPIv1(TagManagerAPI):
    
    from typing import Literal

    name = "TagManagerAPI v1"
    first_call = True

    def __init__(self) -> None:
        super().__init__()
        self.sort_methods = ['Alphabetically', '# Tags'] if self.display_method == 1 else ['Alphabetically', '# Models'] 
    
    def read_all_tags(self) -> list[list[str]]:
        if self.first_call:
            self.first_call = False
            return self.sort('Alphabetically')
        return self.format_tag_data('read')
    
    def search(self, search_term: str) -> list[list[str]]:
        return self.format_tag_data('read', self.tm.search(search_term))
    
    def add_row(self, index: int = -1) -> list[list[str]]:
        return self.format_tag_data('read', self.tm.add_tag())
    
    def del_row(self, index: int = -1) -> list[list[str]]:
        return self.format_tag_data('read', self.tm.remove_tag(index))
    
    def save(self, data: list[list[str]]) -> list[list[str]]:
        self.tm.save_changes(self.format_tag_data('write', data))
        return self.read_all_tags()

    def sort(self, sort_method: str) -> list[list[str]]:
        data = self.format_tag_data('read')

        if sort_method == 'Alphabetically':
            return self.__sort_alphabetically(data)
        if sort_method == '# Tags' or sort_method == '# Models':
            return self.__sort_by_count(data)
    
    def format_tag_data(self, operation: Literal['read', 'write'], data: list[list[str]] = None) -> list[list[str]]:
        base_data = data if not data is None else self.tm.to_dataframe()
        if operation == 'read':
            if self.display_method == 0:
                return base_data
            if self.display_method == 1:
                return self.__read_to_model_display()
            print('you should not be here')
        if operation == 'write':
            if self.display_method == 0:
                return base_data
            if self.display_method == 1:
                return self.__write_from_model_display(base_data)

    def get_headers(self) -> list[str]:
        if self.display_method == 0:
            return ['Tag', 'Description', 'Models']
        if self.display_method== 1:
            return ['Model', ' ', 'Tags']

    def __read_to_model_display(self):
        """
        Converts from tag display to model display
        """
        result = []
        models = self.tm.get_tagged_models()
        for model in models:
            result.append([model, '', list_to_csv(self.tm.get_tags_by_model(model))])
        return result
    
    def __write_from_model_display(self, data: list[list[str]]):
        """
        Converts from model display to tag display
        """
        for item in data:
            if item == '':
                continue
            tags = csv_to_list(item[2])
            for tag in tags:
                obj = self.tm.get_tag_by_name(tag)
                if obj is None:
                    obj = self.tm.Tag(name=tag, models=[item[0]])
                    self.tm.add_tag(new_tag=obj)
                    continue
                if item[0] not in obj.models:
                    obj.models.append(item[0])
        return self.tm.to_dataframe()
    
    def __sort_alphabetically(self, data: list[list[str]], col = 0) -> list[list[str]]:
        return sorted(data, key=lambda x: x[col])
    
    def __sort_by_count(self, data: list[list[str]]) -> list[list[str]]:
        return sorted(data, key=lambda x: len(csv_to_list(x[2])))