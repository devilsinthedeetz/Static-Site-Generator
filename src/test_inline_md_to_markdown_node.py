import unittest

from inline_md_to_markdown_node import (
    inline_md_to_markdown_node,
    MarkdownSyntaxError,
)
from markdown_node import Text, Italic, Bold, Code, Link, Image


class TestInlineMarkdownParser(unittest.TestCase):
    def test_simple_link(self):
        self.assertEqual(
            inline_md_to_markdown_node("Visit [example](https://example.com)."),
            [
                Text("Visit "),
                Link(
                    url="https://example.com",
                    children=[Text("example")],
                ),
                Text("."),
            ],
        )

    def test_styled_link(self):
        self.assertEqual(
            inline_md_to_markdown_node("[I am a _spicy_ link](www.spicy.com)"),
            [
                Link(
                    url="www.spicy.com",
                    children=[
                        Text("I am a "),
                        Italic([Text("spicy")]),
                        Text(" link"),
                    ],
                )
            ],
        )

    def test_link_with_bold_and_code(self):
        self.assertEqual(
            inline_md_to_markdown_node(
                "[Use **bold** and `code`](https://example.com)"
            ),
            [
                Link(
                    url="https://example.com",
                    children=[
                        Text("Use "),
                        Bold([Text("bold")]),
                        Text(" and "),
                        Code("code"),
                    ],
                )
            ],
        )

    def test_image(self):
        self.assertEqual(
            inline_md_to_markdown_node("Logo: ![project logo](/images/logo.png)"),
            [
                Text("Logo: "),
                Image(
                    url="/images/logo.png",
                    alt="project logo",
                ),
            ],
        )

    def test_image_before_link_detection(self):
        self.assertEqual(
            inline_md_to_markdown_node("![alt text](image.png)"),
            [
                Image(
                    url="image.png",
                    alt="alt text",
                )
            ],
        )

    def test_parentheses_in_url(self):
        self.assertEqual(
            inline_md_to_markdown_node(
                "[functions](https://example.com/function_(math))"
            ),
            [
                Link(
                    url="https://example.com/function_(math)",
                    children=[Text("functions")],
                )
            ],
        )

    def test_italic_inside_bold(self):
        result = inline_md_to_markdown_node("**such as _this_ kinda stuff**")

        expected = [
            Bold(
                children=[
                    Text("such as "),
                    Italic(
                        children=[
                            Text("this"),
                        ]
                    ),
                    Text(" kinda stuff"),
                ]
            )
        ]

        self.assertEqual(result, expected)

    def test_bold_inside_italic(self):
        result = inline_md_to_markdown_node("_such as **this** kinda stuff_")

        expected = [
            Italic(
                children=[
                    Text("such as "),
                    Bold(
                        children=[
                            Text("this"),
                        ]
                    ),
                    Text(" kinda stuff"),
                ]
            )
        ]

        self.assertEqual(result, expected)

    def test_multiple_italic_nodes_inside_bold(self):
        result = inline_md_to_markdown_node(
            "**one _italic_ and another _italic_ section**"
        )

        expected = [
            Bold(
                children=[
                    Text("one "),
                    Italic([Text("italic")]),
                    Text(" and another "),
                    Italic([Text("italic")]),
                    Text(" section"),
                ]
            )
        ]

        self.assertEqual(result, expected)

    def test_multiple_bold_nodes_inside_italic(self):
        result = inline_md_to_markdown_node(
            "_one **bold** and another **bold** section_"
        )

        expected = [
            Italic(
                children=[
                    Text("one "),
                    Bold([Text("bold")]),
                    Text(" and another "),
                    Bold([Text("bold")]),
                    Text(" section"),
                ]
            )
        ]

        self.assertEqual(result, expected)

    def test_bold_and_italic_with_surrounding_text(self):
        result = inline_md_to_markdown_node("before **bold with _italic_ text** after")

        expected = [
            Text("before "),
            Bold(
                children=[
                    Text("bold with "),
                    Italic([Text("italic")]),
                    Text(" text"),
                ]
            ),
            Text(" after"),
        ]

        self.assertEqual(result, expected)

    def test_deeply_nested_bold_italic_bold(self):
        result = inline_md_to_markdown_node("**outer _middle **inner** middle_ outer**")

        expected = [
            Bold(
                children=[
                    Text("outer "),
                    Italic(
                        children=[
                            Text("middle "),
                            Bold([Text("inner")]),
                            Text(" middle"),
                        ]
                    ),
                    Text(" outer"),
                ]
            )
        ]

        self.assertEqual(result, expected)

    def test_deeply_nested_italic_bold_italic(self):
        result = inline_md_to_markdown_node("_outer **middle _inner_ middle** outer_")

        expected = [
            Italic(
                children=[
                    Text("outer "),
                    Bold(
                        children=[
                            Text("middle "),
                            Italic([Text("inner")]),
                            Text(" middle"),
                        ]
                    ),
                    Text(" outer"),
                ]
            )
        ]

        self.assertEqual(result, expected)

    def test_code_inside_bold(self):
        result = inline_md_to_markdown_node("**run `python main.py` now**")

        expected = [
            Bold(
                children=[
                    Text("run "),
                    Code("python main.py"),
                    Text(" now"),
                ]
            )
        ]

        self.assertEqual(result, expected)

    def test_code_inside_italic(self):
        result = inline_md_to_markdown_node("_run `python main.py` now_")

        expected = [
            Italic(
                children=[
                    Text("run "),
                    Code("python main.py"),
                    Text(" now"),
                ]
            )
        ]

        self.assertEqual(result, expected)

    def test_markdown_inside_code_is_not_parsed(self):
        result = inline_md_to_markdown_node("`**not bold** and _not italic_`")

        expected = [
            Code("**not bold** and _not italic_"),
        ]

        self.assertEqual(result, expected)

    def test_code_delimiters_inside_bold(self):
        result = inline_md_to_markdown_node("**before `**literal stars**` after**")

        expected = [
            Bold(
                children=[
                    Text("before "),
                    Code("**literal stars**"),
                    Text(" after"),
                ]
            )
        ]

        self.assertEqual(result, expected)

    def test_italic_inside_link(self):
        result = inline_md_to_markdown_node("[I am a _spicy_ link](www.spicy.com)")

        expected = [
            Link(
                url="www.spicy.com",
                children=[
                    Text("I am a "),
                    Italic([Text("spicy")]),
                    Text(" link"),
                ],
            )
        ]

        self.assertEqual(result, expected)

    def test_bold_inside_link(self):
        result = inline_md_to_markdown_node(
            "[Read the **important** section](https://example.com)"
        )

        expected = [
            Link(
                url="https://example.com",
                children=[
                    Text("Read the "),
                    Bold([Text("important")]),
                    Text(" section"),
                ],
            )
        ]

        self.assertEqual(result, expected)

    def test_bold_and_italic_inside_link(self):
        result = inline_md_to_markdown_node(
            "[A **bold and _spicy_** link](https://example.com)"
        )

        expected = [
            Link(
                url="https://example.com",
                children=[
                    Text("A "),
                    Bold(
                        children=[
                            Text("bold and "),
                            Italic([Text("spicy")]),
                        ]
                    ),
                    Text(" link"),
                ],
            )
        ]

        self.assertEqual(result, expected)

    def test_code_inside_link(self):
        result = inline_md_to_markdown_node(
            "[Read about `parse_inline`](https://example.com/parser)"
        )

        expected = [
            Link(
                url="https://example.com/parser",
                children=[
                    Text("Read about "),
                    Code("parse_inline"),
                ],
            )
        ]

        self.assertEqual(result, expected)

    def test_link_inside_bold(self):
        result = inline_md_to_markdown_node(
            "**Visit [this _spicy_ page](https://spicy.com) now**"
        )

        expected = [
            Bold(
                children=[
                    Text("Visit "),
                    Link(
                        url="https://spicy.com",
                        children=[
                            Text("this "),
                            Italic([Text("spicy")]),
                            Text(" page"),
                        ],
                    ),
                    Text(" now"),
                ]
            )
        ]

        self.assertEqual(result, expected)

    def test_link_inside_italic(self):
        result = inline_md_to_markdown_node(
            "_Visit [this **important** page](https://example.com) now_"
        )

        expected = [
            Italic(
                children=[
                    Text("Visit "),
                    Link(
                        url="https://example.com",
                        children=[
                            Text("this "),
                            Bold([Text("important")]),
                            Text(" page"),
                        ],
                    ),
                    Text(" now"),
                ]
            )
        ]

        self.assertEqual(result, expected)

    def test_adjacent_bold_and_italic(self):
        result = inline_md_to_markdown_node("**bold**_italic_")

        expected = [
            Bold([Text("bold")]),
            Italic([Text("italic")]),
        ]

        self.assertEqual(result, expected)

    def test_adjacent_nested_elements_inside_bold(self):
        result = inline_md_to_markdown_node("**_one__two_**")

        expected = [
            Bold(
                children=[
                    Italic([Text("one")]),
                    Italic([Text("two")]),
                ]
            )
        ]

        self.assertEqual(result, expected)

    def test_text_between_nested_elements(self):
        result = inline_md_to_markdown_node("**_one_ middle _two_**")

        expected = [
            Bold(
                children=[
                    Italic([Text("one")]),
                    Text(" middle "),
                    Italic([Text("two")]),
                ]
            )
        ]

        self.assertEqual(result, expected)

    def test_multiple_top_level_nested_groups(self):
        result = inline_md_to_markdown_node("**bold _italic_** plain _italic **bold**_")

        expected = [
            Bold(
                children=[
                    Text("bold "),
                    Italic([Text("italic")]),
                ]
            ),
            Text(" plain "),
            Italic(
                children=[
                    Text("italic "),
                    Bold([Text("bold")]),
                ]
            ),
        ]

        self.assertEqual(result, expected)

    def test_unclosed_link_label(self):
        with self.assertRaises(MarkdownSyntaxError):
            inline_md_to_markdown_node("[broken link(https://example.com)")

    def test_missing_link_url(self):
        with self.assertRaises(MarkdownSyntaxError):
            inline_md_to_markdown_node("[link]")

    def test_unclosed_image_url(self):
        with self.assertRaises(MarkdownSyntaxError):
            inline_md_to_markdown_node("![alt](image.png")

    def test_unclosed_italic_inside_bold(self):
        with self.assertRaises(MarkdownSyntaxError):
            inline_md_to_markdown_node("**bold with _unclosed italic**")

    def test_unclosed_bold_inside_italic(self):
        with self.assertRaises(MarkdownSyntaxError):
            inline_md_to_markdown_node("_italic with **unclosed bold_")

    def test_unclosed_outer_bold(self):
        with self.assertRaises(MarkdownSyntaxError):
            inline_md_to_markdown_node("**bold with _valid italic_")

    def test_unclosed_outer_italic(self):
        with self.assertRaises(MarkdownSyntaxError):
            inline_md_to_markdown_node("_italic with **valid bold**")

    def test_unclosed_code_inside_bold(self):
        with self.assertRaises(MarkdownSyntaxError):
            inline_md_to_markdown_node("**bold with `unclosed code**")

    def test_unclosed_link_inside_bold(self):
        with self.assertRaises(MarkdownSyntaxError):
            inline_md_to_markdown_node(
                "**visit [broken link](https://example.com now**"
            )

    def test_unclosed_link_label_inside_italic(self):
        with self.assertRaises(MarkdownSyntaxError):
            inline_md_to_markdown_node("_visit [broken link(https://example.com)_")
