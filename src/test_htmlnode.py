import unittest
from htmlnode import HTMLNode

test_nodes = [
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
]


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        print(
            """
----------------------------------------------------------------------
Testing HTMLNode's props_to_html()
            """
        )
        for test_node in test_nodes:
            node = test_node[0]
            comparison = test_node[1]
            print("Node:")
            print(node)
            print(f"Expecting:{comparison}")
            print(f"Actual:{node.props_to_html()}")
            self.assertTrue(comparison == node.props_to_html())
