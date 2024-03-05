from enum import Enum

class DisplayMethod(Enum):
    TAG = 0
    MODEL = 1

class TagManagerAPI():
    import scripts.helpers.tag_manager as tm
    name = "Undefined"
    display_method: DisplayMethod = 0
    sort_methods: list[str] = []

    def read_all_tags(self) -> list[list[str]]:
        pass


    def search(self, search_term: str) -> list[list[str]]:
        pass


    def add_row(self, index: int = -1) -> list[list[str]]:
        pass


    def del_row(self, index: int = -1) -> list[list[str]]:
        pass


    def save(self, data: list[list[str]]) -> list[list[str]]:
        pass


    def get_headers(self) -> list[str]:
        pass


    def sort(self, sort_method: str) -> list[list[str]]:
        pass


    def load_tags(self):
        self.tm.load_tags()


    def set_display_method(self, display_method: DisplayMethod):
        self.display_method = display_method


    def get_sort_methods(self) -> list[str]:
        return self.sort_methods