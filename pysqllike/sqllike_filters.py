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


def select(lst, *fields):
    """Select("a", "v=b") from [{"a": 1, "b": 2, "c": 3}, ...]
        => [{"a": 1, "v": 2}, ...]
    """
    fields = [f for f in fields if f]
    result_lst = []

    for i in lst:
        item = {}
        for f in fields:
            if f.find("=") != -1:
                k, f = f.split("=")
            else:
                k = f.replace(".", "_")

            val = getval(i, f)
            if k.find("*") != -1:
                item.update(val)
            else:
                item[k] = val
        result_lst.append(item)
    return result_lst


def groupby(lst, field):
    """[{"key": "a", "val": 1}, {"key": "b", "val": 2}, {"key": "a", "val": 3}]
    groupby key => {
        "a": [{"key": "a", "val": 1}, {"key": "a", ""}],
        "b": [{"key": "b", "val": 2}]
    }
    """
    result = {}
    for i in lst:
        key = getval(i, field)
        if key not in result:
            result[key] = []
        result[key].append(i)
    return result
