import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

test_props_to_html_nodes = [
    [
        HTMLNode(
            "a",
            "This is a Link",
            None,
            {
                "href": "https://www.google.com",
                "target": "_blank",
            },
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

# test_repr_html_nodes = [
#    HTMLNode(
#        tag="div",
#        props={"class": "myDiv"},
#        children=[
#            HTMLNode(
#                tag="p", value="I am a paragraph", props={"style": "text-align:right"}
#            ),
#            HTMLNode(
#                tag="img",
#                props={
#                    "src": "image.png",
#                    "alt": "Example image",
#                    "width": "400",
#                },
#            ),
#            HTMLNode(
#                "a",
#                "This is a Link",
#                None,
#                {
#                    "href": "https://www.google.com",
#                    "target": "_blank",
#                },
#            ),
#        ],
#    )
# ]


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        for test_node in test_props_to_html_nodes:
            node = test_node[0]
            comparison = test_node[1]
            self.assertTrue(comparison == node.props_to_html())

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

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_nested_parents(self):
        self.maxDiff = None
        img_node = LeafNode(
            "img",
            "",
            props={
                "src": "image.png",
                "alt": "Example Image",
                "width": "400",
            },
        )
        img_container_node = ParentNode("div", [img_node])
        raw_text_node = LeafNode(None, "WWF's goal is to:")
        quote_node = LeafNode(
            "q", "Build a future where people live in harmony with nature."
        )
        paragraph_node = ParentNode("p", [raw_text_node, quote_node])
        text_container_node = ParentNode(
            "span", [paragraph_node], props={"style": "text-align:right"}
        )
        top_parent_node = ParentNode("div", [text_container_node, img_container_node])
        comparison = '<div><span style="text-align:right"><p>WWF\'s goal is to:<q>Build a future where people live in harmony with nature.</q></p></span><div><img src="image.png" alt="Example Image" width="400"></div></div>'
        self.assertEqual(top_parent_node.to_html(), comparison)

    def test_to_html_no_tag(self):
        child = LeafNode("span", "child")
        parent = ParentNode(None, [child])

        with self.assertRaises(ValueError):
            parent.to_html()

    def test_to_html_no_tag_2(self):
        child = LeafNode("span", "child")
        parent = ParentNode("", [child])

        with self.assertRaises(ValueError):
            parent.to_html()

    def test_to_html_multiple_children(self):
        child1 = LeafNode("b", "Bold")
        child2 = LeafNode(None, " plain ")
        child3 = LeafNode("i", "Italic")

        parent = ParentNode("p", [child1, child2, child3])

        self.assertEqual(
            parent.to_html(),
            "<p><b>Bold</b> plain <i>Italic</i></p>",
        )

    def test_to_html_with_props(self):
        child = LeafNode("span", "Hello")

        parent = ParentNode(
            "div",
            [child],
            props={
                "class": "container",
                "id": "main",
            },
        )

        self.assertEqual(
            parent.to_html(),
            '<div class="container" id="main"><span>Hello</span></div>',
        )

    def test_to_html_nested_siblings(self):
        left = ParentNode(
            "div",
            [
                LeafNode("p", "First"),
                LeafNode("p", "Second"),
            ],
        )

        right = ParentNode(
            "div",
            [
                LeafNode("p", "Third"),
            ],
        )

        root = ParentNode("section", [left, right])

        self.assertEqual(
            root.to_html(),
            "<section><div><p>First</p><p>Second</p></div><div><p>Third</p></div></section>",
        )

    def test_to_html_text_and_elements(self):
        parent = ParentNode(
            "p",
            [
                LeafNode(None, "Hello "),
                LeafNode("strong", "world"),
                LeafNode(None, "!"),
            ],
        )

        self.assertEqual(
            parent.to_html(),
            "<p>Hello <strong>world</strong>!</p>",
        )

    def test_to_html_empty_leaf_value(self):
        child = LeafNode("span", "")
        parent = ParentNode("div", [child])

        self.assertEqual(
            parent.to_html(),
            "<div><span></span></div>",
        )

    def test_to_html_deeply_nested(self):
        node = LeafNode("span", "bottom")

        for tag in ["div", "section", "article", "main"]:
            node = ParentNode(tag, [node])

        self.assertEqual(
            node.to_html(),
            "<main><article><section><div><span>bottom</span></div></section></article></main>",
        )

    def test_to_html_invalid_child(self):
        parent = ParentNode("div", ["not a node"])

        with self.assertRaises(AttributeError):
            parent.to_html()
