# Get values in dictionary using nested keys. E.g. for keys ["a", "b", "c"], you get dict["a"]["b"]["c"]
def get_nested(dict={}, keys=[]):
    val = dict
    for key in keys:
        if key not in val:
            return None
        val = val[key]
    return val

class OpCond:
    def satisfy():
        return True

class OpCondSet(OpCond):
    def __init__(self, taxonomies=[], boundset=[], json=None):
        if json is not None:
            self._taxonomies = [tax for tax in json["taxonomies"]]
            self._boundset = [bound for bound in json["boundset"]]
            return
        self._taxonomies = taxonomies
        self._boundset = boundset

    def satisfy(self, data = {}):
        val = get_nested(data, self._taxonomies)
        if val is None:
            return False
        return val in self._boundset
    
    def __str__(self):
        return f"OpCondSet(taxonomies={self._taxonomies}, boundset={self._boundset})"
    
    
class OpCondRange(OpCond):
    def __init__(self, taxonomies=[], min=0, max=100, json=None):
        if json is not None:
            self._taxonomies = [tax for tax in json["taxonomies"]]
            self._min = json["min"]
            self._max = json["max"]
            return
        self._taxonomies = taxonomies
        self._min = min
        self._max = max

    def satisfy(self, data = {}):
        val = get_nested(data, self._taxonomies)
        if val is None:
            return False
        return val >= self._min and val <= self._max
    
    def __str__(self):
        return f"OpCondRange(taxonomies={self._taxonomies}, min={self._min}, max={self._max})"


class OpCondImply(OpCond):
    def __init__(self, opcond_if=None, opcond_then=None, json=None):
        if json is not None:
            self._opcond_if = init_opcond_from_json(json["opcond_if"])
            self._opcond_then = init_opcond_from_json(json["opcond_then"])    
            return
        self._opcond_if = opcond_if
        self._opcond_then = opcond_then

    def satisfy(self, data = {}):
        if self._opcond_if.satisfy(data):
            return self._opcond_then.satisfy(data)
        return True

    def __str__(self):
        return f"OpCondImply(opcond_if={self._opcond_if}, opcond_then={self._opcond_then})"


class OpCondAnd(OpCond):
    def __init__(self, opconds=[], json=None):
        if json is not None:
            self._opconds = [init_opcond_from_json(opc_json) for opc_json in json["opconds"]]
            return
        self._opconds = opconds

    def satisfy(self, data = {}):
        return all([oc.satisfy(data) for oc in self._opconds])
    
    def __str__(self):
        return f"OpCondAnd(opconds={self._opconds})"

class OpCondOr(OpCond):
    def __init__(self, opconds=[], json=None):
        if json is not None:
            self._opconds = [init_opcond_from_json(opc_json) for opc_json in json["opconds"]]
            return
        self._opconds = opconds

    def satisfy(self, data = {}):
        return any([oc.satisfy(data) for oc in self._opconds])
    
    def __str__(self):
        return f"OpCondAnd(opconds={self._opconds})"

def init_opcond_from_json(opcond_json):
    if "OpCondRange" in opcond_json:
        return OpCondRange(json=opcond_json["OpCondRange"])
    elif "OpCondSet" in opcond_json:
        return OpCondSet(json=opcond_json["OpCondSet"])
    elif "OpCondAnd" in opcond_json:
        return OpCondAnd(json=opcond_json["OpCondAnd"])
    elif "OpCondOr" in opcond_json:
        return OpCondAnd(json=opcond_json["OpCondOr"])
    elif "OpCondImply" in opcond_json:
        return OpCondImply(json=opcond_json["OpCondImply"])