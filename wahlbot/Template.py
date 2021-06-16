from typing import List
import string
import yaml


def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


class Template:

    def __init__(self, text_modules_path: str = None, page: str = None):
        if text_modules_path:
            self.text_modules = load_yaml(text_modules_path)
        if page:
            self.page = string.Template(page)

    def get_text_module(self, name: str):
        return string.Template(self.text_modules[name]['text'])

    def get_processing(self, name: str) -> List[str]:
        if 'process' in self.text_modules[name].keys():
            return self.text_modules[name]['process']
        return []

    def load_page(self, path='./text_modules/page.txt'):
        with open(path, 'r') as f:
            return string.Template(f.read())

    def get_keys(self):
        return self.text_modules.keys()

    def get_unique_variables(self):
        text = self.page.safe_substitute({})
        variables = [elem[1] for elem in string.Formatter().parse(text) if elem[1]]
        return list(set(variables))
