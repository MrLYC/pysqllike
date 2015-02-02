#!/usr/bin/env python
# encoding: utf-8

from collections import namedtuple

from unittest import TestCase
from pysqllike.sqllike_filters import getval

ObjModel = namedtuple("ObjModel", ["key"])


class Test_getval(TestCase):
    model1 = {
        "int": 1, "float": 2.0, "str": "3",
        "list": [4, 5.0, "6"], "dict": {
            "int": 7, "obj": ObjModel(key=({
                "false": False}, ObjModel(key=True)))}}

    def test_useage(self):
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
