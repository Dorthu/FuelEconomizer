import json

def makeJSONArray(collection):
    return json.dumps([ c.toJSON() for c in collection ])

def makeArray(collection):
    return [ c.toJSON() for c in collection ]
