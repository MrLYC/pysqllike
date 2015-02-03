#!/usr/bin/env python
# encoding: utf-8

import re
import tokenize
import token
import StringIO

__all__ = ["getval", "select", "groupby", "calc"]


def getval(obj, keys, default=None, call_func=False):
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
            if call_func and callable(obj):
                obj = obj()
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


_EXP_VAR_PATTENT = re.compile(r"`([\.\w]+?)`")
_EXP_KEY_WORDS = ("and", "or", "not", "in", "is", "False", "True", "None")
_EXP_BASE_TYPE = (
    int, long, float, str, unicode, complex, list, tuple, dict, bool, type(None))
_EXP_TYPE_HANDLER = {}


def _const_eval(exp):
    """Only const can be evaluate
    """
    stream = StringIO.StringIO(exp)
    parts = []

    for tk_t, tk_v, _, _, _ in tokenize.generate_tokens(stream.readline):
        if tk_t == token.NAME and tk_v not in _EXP_KEY_WORDS:
            raise ValueError("Unknown name: %s" % tk_v)
        parts.append(tk_v)

    return eval(exp, {
        "__builtin__": None,
        "__file__": None,
        "__name__": None,
        "globals": None,
        "locals": None})


def calc(model, exp):
    """Safety eval for where function
    """
    parts = []
    isvar = True
    exp_parts = _EXP_VAR_PATTENT.split(exp)
    for part in exp_parts:
        isvar = not isvar
        if isvar:
            val = getval(model, part, call_func=True)
            val_t = type(val)
            if isinstance(val, _EXP_BASE_TYPE):
                part = repr(val)
            elif val_t in _EXP_TYPE_HANDLER:
                part = _EXP_TYPE_HANDLER[val_t](val)
            else:
                part = "'%s'" % str(val)
        parts.append(part)

    return _const_eval("".join(parts))
