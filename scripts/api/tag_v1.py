from scripts.api.tag_api import TagManagerAPI, DisplayMethod
from scripts.helpers.utils import csv_to_list, list_to_csv

class TagManagerAPIv1(TagManagerAPI):
    
    from typing import Literal

    name = "TagManagerAPI v1"
    first_call = True       
    

    def set_display_method(self, display_method: DisplayMethod):
        super().set_display_method(display_method)
        self.sort_methods = ['Alphabetically', '# Tags'] if self.display_method == 1 else ['Alphabetically', '# Models'] 


    def read_all_tags(self) -> list[list[str]]:
        if self.first_call:
            self.first_call = False
            return self.sort('Alphabetically')
        return self.format_tag_data('read')
    

    def search(self, search_term: str) -> list[list[str]]:
        return self.format_tag_data('read', self.tm.search(search_term))
    

    def add_row(self, index: int = -1) -> list[list[str]]:
        tag: self.tm.Tag = None
        if self.display_method == 1:
            tag = self.tm.Tag(name='placeholder', description='', models=['my_model'])
        return self.format_tag_data('read', self.tm.add_tag(tag))
    

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
                return self.__read_to_model_display(base_data)
            
        if operation == 'write':
            if self.display_method == 0:
                return base_data
            if self.display_method == 1:
                return self.__write_from_model_display(base_data)
        
        raise NotImplementedError()


    def get_headers(self) -> list[str]:
        if self.display_method == 0:
            return ['Tag', 'Description', 'Models']
        if self.display_method== 1:
            return ['Model', 'Tags']


    def __read_to_model_display(self, data: list[list[str]]):
        """
        Converts from tag display to model display
        """
        result = []
        models = self.tm.get_tagged_models(data)
        for model in models:
            result.append([model, list_to_csv(self.tm.get_tags_by_model(model))])
        return result
    

    def __write_from_model_display(self, data: list[list[str]]):
        """
        Converts from model display to tag display
        """
        buffer = {}
        for row in data:
            if row[0] == '' or row[0] is None:
                continue
            tags = csv_to_list(row[1])
            for tag in tags:
                obj = self.tm.get_tag_by_name(tag)
                if obj is None:
                    obj = self.tm.Tag(name=tag, models=[row[0]])
                    self.tm.add_tag(new_tag=obj)

                try:
                    buffer[obj].append(row[0])
                except KeyError:
                    buffer[obj] = [row[0]]
        
        for cached_tag in self.tm.tags:
            if cached_tag not in buffer.keys():
                buffer[cached_tag] = []

        for tag_object, models in buffer.items():
            tag_object.models = models

        return self.tm.to_dataframe()
    

    def __sort_alphabetically(self, data: list[list[str]], col = 0) -> list[list[str]]:
        return sorted(data, key=lambda x: x[col])
    

    def __sort_by_count(self, data: list[list[str]]) -> list[list[str]]:
        return sorted(data, key=lambda x: len(csv_to_list(x[1])), reverse=True)