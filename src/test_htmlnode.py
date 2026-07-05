import unittest
from htmlnode import HTMLNode, LeafNode

test_props_to_html_nodes = [
    [
        HTMLNode(
            "a",
            "This is a Link",
            {
                "href": "https://www.google.com",
                "target": "_blank",
            },
            None,
        ),
        ' href="https://www.google.com" target="_blank"',
    ],
    [
        HTMLNode(
            tag="img",
            props={
                "src": "image.png",
                "alt": "Example image",
                "width": "400",
            },
        ),
        ' src="image.png" alt="Example image" width="400"',
    ],
    [
        HTMLNode(
            tag="p", value="I am a paragraph", props={"style": "text-align:right"}
        ),
        ' style="text-align:right"',
    ],
]

test_repr_html_nodes = [
    HTMLNode(
        tag="div",
        props={"class": "myDiv"},
        children=[
            HTMLNode(
                tag="p", value="I am a paragraph", props={"style": "text-align:right"}
            ),
            HTMLNode(
                tag="img",
                props={
                    "src": "image.png",
                    "alt": "Example image",
                    "width": "400",
                },
            ),
            HTMLNode(
                "a",
                "This is a Link",
                {
                    "href": "https://www.google.com",
                    "target": "_blank",
                },
                None,
            ),
        ],
    )
]


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        for test_node in test_props_to_html_nodes:
            node = test_node[0]
            comparison = test_node[1]
            self.assertTrue(comparison == node.props_to_html())


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_h1(self):
        node = LeafNode("h1", "My Title")
        self.assertEqual(node.to_html(), "<h1>My Title</h1>")

    def test_leaf_no_tag_returns_raw_text(self):
        node = LeafNode(None, "Hello, world!")
        self.assertEqual(node.to_html(), "Hello, world!")

    def test_leaf_with_props(self):
        node = LeafNode("a", "Boot.dev", {"href": "https://boot.dev"})
        self.assertEqual(node.to_html(), '<a href="https://boot.dev">Boot.dev</a>')

    def test_leaf_with_multiple_props(self):
        node = LeafNode(
            "a",
            "Google",
            {
                "href": "https://google.com",
                "target": "_blank",
            },
        )
        self.assertEqual(
            node.to_html(), '<a href="https://google.com" target="_blank">Google</a>'
        )

    def test_leaf_missing_value_raises_error(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None).to_html()

    def test_leaf_empty_str_value(self):
        self.assertEqual(LeafNode("p", "").to_html(), "<p></p>")

    def test_leaf_children_is_none(self):
        node = LeafNode("p", "Hello")
        self.assertIsNone(node.children)

    def test_leaf_repr(self):
        node = LeafNode("p", "Hello")
        self.assertEqual(repr(node), "LeafNode(tag=p, value=Hello, props=None)")
