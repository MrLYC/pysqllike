#!/usr/bin/env python
# encoding: utf-8


def getval(obj, keys, default=None):
    """Try to get value from obj by keys chains
    """
    for key in keys.split("."):
        try:
            if key == "*":
                break
            elif (isinstance(obj, dict) or hasattr(obj, "get")) and key in obj:
                obj = obj.get(key)
            elif hasattr(obj, key):
                obj = getattr(obj, key)
            elif isinstance(obj, (tuple, list)):
                obj = obj[int(key)]
            elif hasattr(obj, "__getitem__"):
                obj = obj[key]
            continue
        except:
            pass
        obj = default
        break
    return obj
