import unittest
from textnode import TextNode, TextType

equal_cases: list[list[TextNode]] = [
    [
        TextNode("'This is a text node'", TextType.CODE, None),
        TextNode("'This is a text node'", TextType.CODE),
    ],
    [
        TextNode(
            "This is a link text node",
            TextType.LINK,
            "https://blog.devilsinthedeetz.com",
        ),
        TextNode(
            "This is a link text node",
            TextType.LINK,
            "https://blog.devilsinthedeetz.com",
        ),
    ],
    [
        TextNode(
            "Oh look, another text node. This one is italic",
            TextType.ITALIC,
        ),
        TextNode(
            "Oh look, another text node. This one is italic", TextType.ITALIC, None
        ),
    ],
]

not_equal_cases: list[list[TextNode]] = [
    [
        TextNode("'This is a text node'", TextType.CODE),
        TextNode("'This is a spicy text node'", TextType.CODE),
    ],
    [
        TextNode("String Cheese", TextType.IMAGE, "https://stringcheese.jpg"),
        TextNode("String Cheese", TextType.IMAGE, None),
    ],
    [
        TextNode("String Cheese", TextType.IMAGE, "https://stringcheese.jpg"),
        TextNode("String Cheese", TextType.IMAGE),
    ],
    [
        TextNode(
            "This is some text", TextType.LINK, "https://www.gigchad.com/trollface.png"
        ),
        TextNode(
            "This is some text", TextType.IMAGE, "https://www.gigchad.com/trollface.png"
        ),
    ],
]


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        for case in equal_cases:
            self.assertEqual(case[0], case[1])

    def test_not_eq(self):
        for case in not_equal_cases:
            self.assertNotEqual(case[0], case[1])


if __name__ == "__main__":
    unittest.main()
