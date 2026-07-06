import unittest
from textnode import TextType, TextNode, text_node_to_html_node

no_url_nodes_cases = [
    [TextNode("plain text", TextType.TEXT), None, "plain text", "plain text"],
    [TextNode("bold text", TextType.BOLD), "b", "bold text", "<b>bold text</b>"],
    [
        TextNode("italic text", TextType.ITALIC),
        "i",
        "italic text",
        "<i>italic text</i>",
    ],
    [
        TextNode("code text", TextType.CODE),
        "code",
        "code text",
        "<code>code text</code>",
    ],
]


class TestNodeConversion(unittest.TestCase):
    def test_text(self):
        for case in no_url_nodes_cases:
            html_node = text_node_to_html_node(case[0])
            self.assertEqual(html_node.tag, case[1])
            self.assertEqual(html_node.value, case[2])
            self.assertEqual(html_node.to_html(), case[3])

    def test_image(self):
        node = TextNode(
            "This is alt-text for an image node", TextType.IMAGE, "image.png"
        )
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(
            html_node.props,
            {"src": "image.png", "alt": "This is alt-text for an image node"},
        )
        self.assertEqual(
            html_node.to_html(),
            '<img src="image.png" alt="This is alt-text for an image node">',
        )

    def test_link(self):
        node = TextNode(
            "Click here for more!", TextType.LINK, "https://www.example.com"
        )
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here for more!")
        self.assertEqual(html_node.props, {"href": "https://www.example.com"})
        self.assertEqual(
            html_node.to_html(),
            '<a href="https://www.example.com">Click here for more!</a>',
        )

    def test_invalid_text_type(self):
        node = TextNode("im an invalid", "not a TextType")
        with self.assertRaises(Exception):
            text_node_to_html_node(node)

    def test_invalid_url_image(self):
        node = TextNode("alt text", TextType.IMAGE)
        node2 = TextNode("alt text", TextType.IMAGE, "")
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node2)

    def test_invalid_url_link(self):
        node = TextNode("Click Me!", TextType.LINK)
        node2 = TextNode("Click Me!", TextType.LINK, None)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node2)
