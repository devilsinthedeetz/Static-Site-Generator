from re import I
from typing import ItemsView
import unittest
from inline_md_to_text_node import split_nodes_delimiter
from textnode import TextNode, TextType


class TestMDConversion(unittest.TestCase):
    def test_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "`", TextType.CODE),
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_code_2(self):
        node = TextNode("This is text with `a **code** block` word", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "`", TextType.CODE),
            [
                TextNode("This is text with ", TextType.TEXT),
                TextNode("a **code** block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_code_bold(self):
        node = TextNode("This is **text** with `a **code** block` word", TextType.TEXT)
        first_split = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            split_nodes_delimiter(first_split, "**", TextType.BOLD),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with ", TextType.TEXT),
                TextNode("a **code** block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_code_italic(self):
        node = TextNode(
            "This is _spicy text_ with `a _code_ block` word", TextType.TEXT
        )
        first_split = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            split_nodes_delimiter(first_split, "_", TextType.ITALIC),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("spicy text", TextType.ITALIC),
                TextNode(" with ", TextType.TEXT),
                TextNode("a _code_ block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_bold(self):
        node = TextNode("This is text with a **bold** word", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "**", TextType.BOLD),
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_italic(self):
        node = TextNode("This is text with a _spicy_ word", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "_", TextType.ITALIC),
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("spicy", TextType.ITALIC),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_code_bold_italic(self):
        node = TextNode(
            "This is _spicy_ **bold** text with a `_**code**_` word", TextType.TEXT
        )
        first_split = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            first_split,
            [
                TextNode("This is _spicy_ **bold** text with a ", TextType.TEXT),
                TextNode("_**code**_", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )
        second_split = split_nodes_delimiter(first_split, "**", TextType.BOLD)
        self.assertEqual(
            second_split,
            [
                TextNode("This is _spicy_ ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text with a ", TextType.TEXT),
                TextNode("_**code**_", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )
        third_split = split_nodes_delimiter(second_split, "_", TextType.ITALIC)
        self.assertEqual(
            third_split,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("spicy", TextType.ITALIC),
                TextNode(" ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text with a ", TextType.TEXT),
                TextNode("_**code**_", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_node_list_err(self):
        node = TextNode("I am a _zesty_ boy", TextType.TEXT)
        with self.assertRaises(TypeError):
            split_nodes_delimiter(node, "_", TextType.ITALIC)

    def test_deliminator_support_err(self):
        node = TextNode("I am a *zesty* boy", TextType.TEXT)
        with self.assertRaises(NotImplementedError):
            split_nodes_delimiter([node], "*", TextType.ITALIC)

    def test_deliminator_mismatch_err(self):
        node = TextNode("I should raise some sorta exception", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.ITALIC)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.BOLD)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.CODE)

    def test_closing_deliminator_err(self):
        node = TextNode("I really should close my **bold delimiter", TextType.TEXT)
        node2 = TextNode("I really should close my _zesty delimiter", TextType.TEXT)
        node3 = TextNode("I really should close my `code delimiter", TextType.TEXT)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "**", TextType.BOLD)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node2], "_", TextType.ITALIC)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node3], "`", TextType.CODE)
