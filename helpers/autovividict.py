from collections import defaultdict

class CountDict(defaultdict):
    def __init__(self, *args, **kwargs):
        self.value = 0
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return str(dict(self))

    def __add__(self, x):
        return self.value + x

def autovividict():
    return defaultdict(autovividict)