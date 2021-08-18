import yaml
import pickle
import csv
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
            return yaml.load(f, Loader=yaml.Loader)

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

class CsvResult(Result):
    def __init__(self, rows, **fmtparams):
        self.rows = rows
        self.fmt_params = fmt_params
    def save(self, path):
        with open(path, "w") as f:
            writer = csv.writer(f, **fmtparams)
            for row in self.rows:
                writer.writerow(row)
    @classmethod
    def collect(cls, path):
        """Loads the rows from the csv file.
        Note that it is possible to directly create
        a pandas.DataFrame object using these rows as input."""
        rows = []
        with open(path) as f:
            reader = csv.reader(f, **fmtparams)
            for row in reader:
                rows.append(row)
        return rows

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
