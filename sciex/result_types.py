import yaml
import pickle
from sciex.components import Result

class YamlResult(Result):
    def __init__(self, things):
        self._things = things
    def save(self, path):
        with open(path, "w") as f:
            yaml.dump(self._things, f)
    @classmethod
    def collect(cls, path):
        with open(path) as f:
            return yaml.load(f)

class PklResult(Result):
    def __init__(self, things):
        self._things = things
    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self._things, f)
    @classmethod
    def collect(cls, path):
        with open(path, "rb") as f:
            return pickle.load(f)

class PostProcessingResult(Result):
    """This kind of result does not save anything,
    but is used for collecting multiple other result
    files."""
    @classmethod
    def FILENAMES(cls):
        raise NotImplemented
    
    @classmethod
    def collect(cls, path):
        raise NotImplemented
