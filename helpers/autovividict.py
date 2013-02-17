from collections import defaultdict

# counting dictionary that serves as 0 for addition
# this allows incrementing unknown keys: d['k'] += 1
class countdict(defaultdict):
    def __init__(self, *args, **kwargs):
        self.value = 0
        super(countdict, self).__init__(*args, **kwargs)
    def __repr__(self):
        return str(dict(self))
    def __add__(self, x):
        return self.value + x

# autovivicatious counting dictionary, allowing dynamic creation of keys
# explained at <http://en.wikipedia.org/wiki/Autovivification#Python>
def autovividict():
    return countdict(autovividict)
