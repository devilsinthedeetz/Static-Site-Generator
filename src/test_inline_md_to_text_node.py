from re import I
from typing import ItemsView
import unittest
from inline_md_to_text_node import (
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_text_node,
)
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

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_images(self):
        matches = extract_markdown_images(
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        self.assertEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            matches,
        )

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://www.google.com)"
        )
        self.assertEqual([("link", "https://www.google.com")], matches)

    def test_extract_multiple_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            matches,
        )

    def test_extract_images_links_no_matches(self):
        matches = extract_markdown_images("I should return no matches")
        matches2 = extract_markdown_links("I should call her")
        self.assertEqual([], matches)
        self.assertEqual([], matches2)

    def test_split_node_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_node_link(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )

    def test_split_node_no_image_link(self):
        node = TextNode("Just plain text", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)
        new_nodes2 = split_nodes_link([node])
        self.assertListEqual([node], new_nodes2)

    def test_split_node_image_at_beginning(self):
        node = TextNode(
            "![logo](https://example.com/logo.png) starts the text",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("logo", TextType.IMAGE, "https://example.com/logo.png"),
                TextNode(" starts the text", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_node_link_at_beginning(self):
        node = TextNode(
            "[Google](https://google.com) is a slop engine",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Google", TextType.LINK, "https://google.com"),
                TextNode(" is a slop engine", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_node_image_at_end(self):
        node = TextNode(
            "Look at this ![cat](https://example.com/cat.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("Look at this ", TextType.TEXT),
                TextNode("cat", TextType.IMAGE, "https://example.com/cat.png"),
            ],
            new_nodes,
        )

    def test_split_node_link_at_end(self):
        node = TextNode(
            "Visit [Example.com](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Visit ", TextType.TEXT),
                TextNode("Example.com", TextType.LINK, "https://example.com"),
            ],
            new_nodes,
        )

    def test_split_node_only_image(self):
        node = TextNode(
            "![cat](https://example.com/cat.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("cat", TextType.IMAGE, "https://example.com/cat.png"),
            ],
            new_nodes,
        )

    def test_split_node_only_link(self):
        node = TextNode(
            "[Google](https://google.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Google", TextType.LINK, "https://google.com"),
            ],
            new_nodes,
        )

    def test_split_multiple_nodes_images(self):
        nodes = [
            TextNode("Hello ", TextType.TEXT),
            TextNode("![cat](https://example.com/cat.png)", TextType.TEXT),
            TextNode(" Goodbye", TextType.TEXT),
        ]
        new_nodes = split_nodes_image(nodes)
        self.assertListEqual(
            [
                TextNode("Hello ", TextType.TEXT),
                TextNode("cat", TextType.IMAGE, "https://example.com/cat.png"),
                TextNode(" Goodbye", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_multiple_nodes_links(self):
        nodes = [
            TextNode("First", TextType.BOLD),
            TextNode("[Boot.dev](https://boot.dev)", TextType.TEXT),
            TextNode("Last", TextType.ITALIC),
        ]
        new_nodes = split_nodes_link(nodes)
        self.assertListEqual(
            [
                TextNode("First", TextType.BOLD),
                TextNode("Boot.dev", TextType.LINK, "https://boot.dev"),
                TextNode("Last", TextType.ITALIC),
            ],
            new_nodes,
        )

    def test_split_images_invalid_parameter(self):
        with self.assertRaises(TypeError):
            split_nodes_image("not a list")

    def test_split_links_invalid_parameter(self):
        with self.assertRaises(TypeError):
            split_nodes_link("not a list")

    def test_text_to_text_node(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        self.assertEqual(
            text_to_text_node(text),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
        )
