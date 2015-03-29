import json

def makeJSONArray(collection):
    print("Making json array from %s", collection)
    array = []
    for obj in collection:
        print("Obj is %s", obj)
        array.append(obj.toJSON())
    return json.dumps(array)

def makeArray(collection):
    print("Making array from ", collection)
    array = []
    for obj in collection:
        array.append(obj.toJSON())
    return array