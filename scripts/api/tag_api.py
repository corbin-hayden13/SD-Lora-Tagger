from enum import Enum

class DisplayMode(Enum):
    TAG = 0
    MODEL = 1

class TagManagerAPI():
    import scripts.helpers.tag_manager as tm
    name = "Undefined"
    display_mode: DisplayMode = DisplayMode.TAG
    sort_methods: list[str] = []

    def read_all_tags(self) -> list[list[str]]:
        pass


    def search(self, search_term: str) -> list[list[str]]:
        pass


    def add_row(self, data, index: int = -1) -> list[list[str]]:
        pass


    def del_row(self, data, index: int = -1) -> list[list[str]]:
        pass


    def save(self, data: list[list[str]]) -> list[list[str]]:
        pass


    def get_headers(self) -> list[str]:
        pass


    def get_col_count(self) -> tuple[int, str]:
        if self.display_mode is DisplayMode.TAG:
            return (4, 'fixed')
        else:
            return (3, 'fixed')


    def sort(self, sort_method: str) -> list[list[str]]:
        pass


    def load_tags(self):
        self.tm.load_tags()


    def set_display_mode(self, display_mode: DisplayMode):
        self.display_mode = display_mode


    def get_sort_methods(self) -> list[str]:
        return self.sort_methods