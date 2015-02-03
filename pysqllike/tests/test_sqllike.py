#!/usr/bin/env python
# encoding: utf-8

from collections import namedtuple

from unittest import TestCase
from pysqllike.sqllike_filters import getval, select, groupby, calc, where

ObjModel = namedtuple("ObjModel", ["key"])


class Test_getval(TestCase):
    model1 = {
        "int": 1, "float": 2.0, "str": "3",
        "list": [4, 5.0, "6"], "dict": {
            "int": 7, "obj": ObjModel(key=({
                "false": False}, ObjModel(key=True)))}}

    def test_usage(self):
        self.assertEqual(getval(self.model1, "int"), 1)
        self.assertEqual(getval(self.model1, "float"), 2.0)
        self.assertEqual(getval(self.model1, "str"), "3")
        self.assertListEqual(getval(self.model1, "list"), [4, 5.0, "6"])

        self.assertListEqual(getval(self.model1, "list.*"), [4, 5.0, "6"])
        self.assertEqual(getval(self.model1, "list.0"), 4)
        self.assertEqual(getval(self.model1, "list.1"), 5.0)
        self.assertEqual(getval(self.model1, "list.2"), "6")

        self.assertEqual(getval(self.model1, "dict.int"), 7)

        self.assertIsInstance(getval(self.model1, "dict.obj"), ObjModel)
        self.assertIsInstance(getval(self.model1, "dict.obj.key"), tuple)
        self.assertIsInstance(getval(self.model1, "dict.obj.0"), tuple)
        self.assertEqual(getval(self.model1, "dict.obj.key.0.false"), False)
        self.assertEqual(getval(self.model1, "dict.obj.0.0.false"), False)
        self.assertIsInstance(getval(self.model1, "dict.obj.0.1"), ObjModel)
        self.assertEqual(getval(self.model1, "dict.obj.0.1.key"), True)

        self.assertEqual(getval(self.model1, "dict.noexist", False), False)


class Test_select(TestCase):
    model1 = [
        {"name": "1", "age": 23},
        {"name": "4", "age": 56},
        {"name": "7", "age": 89}]

    model2 = [
        {"name": "1", "obj": ObjModel(key="a")},
        {"name": "2", "obj": ObjModel(key="b")},
        {"name": "3", "obj": ObjModel(key="c")},
        {"name": "4", "obj": ObjModel(key="d")}]

    model3 = [
        ObjModel(key={"name": "1", "value": 2, "attrs": {"w": 3, "h": 4}}),
        ObjModel(key={"name": "5", "value": 6, "attrs": {"w": 7, "h": 8}})]

    def test_usage(self):
        self.assertListEqual(select(self.model1, "name"), [
            {"name": "1"}, {"name": "4"}, {"name": "7"}])

        self.assertListEqual(select(self.model1, "age"), [
            {"age": 23}, {"age": 56}, {"age": 89}])

        self.assertListEqual(select(self.model1, "n=name", "a=age"), [
            {"n": "1", "a": 23}, {"n": "4", "a": 56}, {"n": "7", "a": 89}])

        self.assertListEqual(select(self.model1, "*"), self.model1)

        self.assertListEqual(select(self.model1, "person=*"), [
            {"person": {
                "name": "1", "age": 23}},
            {"person": {
                "name": "4", "age": 56}},
            {"person": {
                "name": "7", "age": 89}}])

        self.assertListEqual(select(self.model2, "name", "obj.key"), [
            {"name": "1", "obj_key": "a"},
            {"name": "2", "obj_key": "b"},
            {"name": "3", "obj_key": "c"},
            {"name": "4", "obj_key": "d"}])

        self.assertListEqual(select(self.model2, "name", "key=obj.key"), [
            {"name": "1", "key": "a"},
            {"name": "2", "key": "b"},
            {"name": "3", "key": "c"},
            {"name": "4", "key": "d"}])

        self.assertListEqual(select(self.model3, "key.attrs.*"), [
            {"w": 3, "h": 4},
            {"w": 7, "h": 8}])

        self.assertListEqual(select(self.model3, "name=key.name", "key.value", "key.attrs.*"), [
            {"name": "1", "key_value": 2, "w": 3, "h": 4},
            {"name": "5", "key_value": 6, "w": 7, "h": 8}])


class Test_groupby(TestCase):
    model1 = [
        {"name": "a", "val": 1, "attrs": {"cached": False}},
        {"name": "b", "val": 1, "attrs": {"cached": False}},
        {"name": "a", "val": 2, "attrs": {"cached": True}},
        {"name": "c", "val": 2, "attrs": {"cached": False}},
        {"name": "b", "val": 3, "attrs": {"cached": True}}]

    def test_usage(self):
        self.assertDictEqual(groupby(self.model1, "name"), {
            "a": [
                {"name": "a", "val": 1, "attrs": {"cached": False}},
                {"name": "a", "val": 2, "attrs": {"cached": True}}],
            "b": [
                {"name": "b", "val": 1, "attrs": {"cached": False}},
                {"name": "b", "val": 3, "attrs": {"cached": True}}],
            "c": [
                {"name": "c", "val": 2, "attrs": {"cached": False}}]})

        self.assertDictEqual(groupby(self.model1, "attrs.cached"), {
            False: [
                {"name": "a", "val": 1, "attrs": {"cached": False}},
                {"name": "b", "val": 1, "attrs": {"cached": False}},
                {"name": "c", "val": 2, "attrs": {"cached": False}}],
            True: [
                {"name": "a", "val": 2, "attrs": {"cached": True}},
                {"name": "b", "val": 3, "attrs": {"cached": True}}]})


class Test_exp_eval(TestCase):
    model1 = {
        "int": 1, "float": 2.3, "str": "456", "list": [7, 8.9, "10"],
        "dict": {"key1": 11, "key2": ObjModel(key=12.13)}}

    def test_usage(self):
        self.assertEqual(calc(self.model1, "`int`+1"), 2)
        self.assertEqual(calc(self.model1, "0.09 < `float`/23 < 0.1"), True)
        self.assertEqual(calc(self.model1, "`str` == '456'"), True)
        self.assertEqual(calc(self.model1, "7 in `list`"), True)
        self.assertEqual(calc(self.model1, "'key3' not in `dict.keys`"), True)
        self.assertEqual(calc(self.model1, "`dict.key1`/10 == `int`"), True)
        self.assertEqual(calc(self.model1, "'`dict.key2`'"), "ObjModel(key=12.13)")
        self.assertEqual(calc(self.model1, "12 and 34 or 56"), 34)

    def test_evil(self):
        forbidden_exps = (
            "import os", "raw_input()", "dir()", "x=1", "lambda x:1",
            "__import__('os').system('rm -rf ./')", "`__class__`.__name__")

        for exp in forbidden_exps:
            with self.assertRaises(ValueError):
                calc(None, exp)


class Test_wehre(TestCase):
    model1 = [
        {"key": "a", "val": 1},
        {"key": "a", "val": 2},
        {"key": "b", "val": 3},
        {"key": "a", "val": 4},
        {"key": "b", "val": 5},
        {"key": "a", "val": 6}]

    def test_usage(self):
        self.assertListEqual(where(self.model1, "`key` == 'a'"), [
            {"key": "a", "val": 1},
            {"key": "a", "val": 2},
            {"key": "a", "val": 4},
            {"key": "a", "val": 6}])

        self.assertListEqual(where(self.model1, "`val` % 2 == 1"), [
            {"key": "a", "val": 1},
            {"key": "b", "val": 3},
            {"key": "b", "val": 5}])

        self.assertListEqual(where(
            self.model1, "`key` == 'b' and `val` in [5, 6]"),
            [{"key": "b", "val": 5}])
