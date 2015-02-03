#!/usr/bin/env python
# encoding: utf-8

from ast import literal_eval
import tokenize
import token
import StringIO

__all__ = [
    "getval", "select", "groupby", "calc", "where", "each", "limit", "reverse"]


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
            if k.rfind("*") != -1:
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


_EXP_KEY_WORDS = {"and", "or", "not", "in", "is", "False", "True", "None"}
_EXP_BASE_TYPE = (
    int, long, float, str, unicode, complex, list, tuple, dict, bool, type(None))
_EXP_TYPE_HANDLER = {}
_EXP_FUNC = {
    "len": len, "sum": sum, "abs": abs}


def calc(model, exp):
    """Safety eval for where function
    """
    stream = StringIO.StringIO(exp)
    parts = []
    invar = False
    var_path = []

    for tk_t, tk_v, _, _, _ in tokenize.generate_tokens(stream.readline):
        part = ""
        if tk_v == "`":
            if invar:
                val = getval(model, ".".join(var_path))
                val_type = type(val)
                var_path = []
                if val_type in _EXP_TYPE_HANDLER:
                    val = _EXP_TYPE_HANDLER[val_type](val)
                try:
                    if isinstance(val, _EXP_BASE_TYPE):
                        part = repr(literal_eval(repr(val)))
                    else:
                        part = "'%s'" % str(val)
                except ValueError:
                    part = "'%s'" % str(val)
            invar = not invar
        elif invar:
            if tk_t in (token.NAME, token.NUMBER) or tk_v == "*":
                var_path.append(tk_v)
            elif tk_v != ".":
                raise ValueError("Unknown var: %s.%s" % (".".join(var_path), tk_v))
        elif tk_v not in (".", "=") and \
                tk_t != token.NAME or tk_v in _EXP_KEY_WORDS or tk_v in _EXP_FUNC:
            part = tk_v
        else:
            raise ValueError("Forbidden expression")
        if part:
            parts.append(part)

    env = {
        "__builtin__": None,
        "__file__": None,
        "__name__": None,
        "globals": None,
        "locals": None}

    return eval(" ".join(parts), _EXP_FUNC, env)


def where(lst, exp):
    """Filter items where match the exp
    """
    result = []
    for i in lst:
        if calc(i, exp):
            result.append(i)
    return result


def each(lst, exp):
    """Calculate each item with exp
    """
    return map(lambda i: calc(i, exp), lst)


def limit(lst, index, offset=None, step=1):
    """Constrain the number of items.
    """
    if offset is None:
        offset = len(lst)
    else:
        offset = offset + index
    return lst[index:offset:step]


def reverse(lst):
    """Reverse a list
    """
    return lst[::-1]
