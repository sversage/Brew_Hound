import unidecode
import pandas as pd
import re
from read_write_to_sql import BrewHoundDatabase

class MyCompleter:

    def __init__(self):
        self.db = BrewHoundDatabase()
        self.options = sorted(set(self.db.query_sql("SELECT * FROM beer_names;").name.tolist()))
        self.options = [(re.sub('[^a-z0-9]+', '', x.lower()),x) for x in self.options]

    def complete(self, text):
        if text:
            text = re.sub('[^a-z0-9]+', '', text.lower())
            self.matches = [unidecode.unidecode(s[1]) for s in self.options
                               if text in s[0]]
        else:
            self.matches = self.options[:]

        return {'response':self.matches}

if __name__ == '__main__':
    comp_test = MyCompleter()
    print comp_test.complete("Amber")
