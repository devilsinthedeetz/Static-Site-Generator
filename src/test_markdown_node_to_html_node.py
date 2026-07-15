import unittest

from block_md_to_markdown_node import markdown_to_markdown_node
from htmlnode import LeafNode, ParentNode
from markdown_node import (
    BlockNode,
    BlockQuote,
    Bold,
    Code,
    CodeBlock,
    Heading,
    Image,
    InlineNode,
    Italic,
    Link,
    ListBlock,
    ListItem,
    ListType,
    Paragraph,
    Table,
    TableAlignment,
    TableCell,
    TableRow,
    Text,
)
from markdown_node_to_html_node import (
    block_node_to_html_node,
    inline_node_to_html_node,
    list_block_to_html_node,
    markdown_nodes_to_html_node,
    table_row_to_html_node,
    table_to_html_node,
)


class UnknownBlock(BlockNode):
    pass


class UnknownInline(InlineNode):
    pass


class TestMarkdownNodesToHTMLNode(unittest.TestCase):
    def test_document_returns_div_with_converted_block_children(self):
        markdown_nodes = [
            Heading(1, [Text("Title")]),
            Paragraph([Text("Body")]),
        ]

        actual = markdown_nodes_to_html_node(markdown_nodes)
        expected = ParentNode(
            "div",
            [
                ParentNode("h1", [LeafNode(None, "Title")]),
                ParentNode("p", [LeafNode(None, "Body")]),
            ],
        )

        self.assertEqual(actual, expected)
        self.assertEqual(actual.to_html(), "<div><h1>Title</h1><p>Body</p></div>")

    def test_empty_document_still_returns_an_empty_div_parent_node(self):
        actual = markdown_nodes_to_html_node([])

        self.assertIsInstance(actual, ParentNode)
        self.assertEqual(actual.tag, "div")
        self.assertEqual(actual.children, [])

        # ParentNode.to_html() currently rejects empty child lists. This test
        # documents the converter's result without assigning that HTMLNode
        # behavior to this converter.
        with self.assertRaisesRegex(ValueError, "ParentNode must have children"):
            actual.to_html()


class TestInlineNodeToHTMLNode(unittest.TestCase):
    def test_text_is_escaped(self):
        actual = inline_node_to_html_node(Text("5 < 7 & 8 > 3"))

        self.assertEqual(actual, LeafNode(None, "5 &lt; 7 &amp; 8 &gt; 3"))
        self.assertEqual(actual.to_html(), "5 &lt; 7 &amp; 8 &gt; 3")

    def test_nested_bold_and_italic_are_preserved(self):
        node = Bold(
            [
                Text("bold "),
                Italic([Text("and italic")]),
                Text(" text"),
            ]
        )

        actual = inline_node_to_html_node(node)

        self.assertEqual(
            actual.to_html(),
            "<strong>bold <em>and italic</em> text</strong>",
        )

    def test_inline_code_is_escaped_but_not_parsed_as_markdown(self):
        actual = inline_node_to_html_node(Code("<tag> **not bold** & value"))

        self.assertEqual(
            actual.to_html(),
            "<code>&lt;tag&gt; **not bold** &amp; value</code>",
        )

    def test_link_renders_nested_inline_children_and_escaped_url(self):
        node = Link(
            'https://example.com/search?q="markdown"&page=1',
            [Text("a "), Italic([Text("spicy")]), Text(" link")],
        )

        actual = inline_node_to_html_node(node)

        self.assertEqual(
            actual.to_html(),
            '<a href="https://example.com/search?q=&quot;markdown&quot;&amp;page=1">'
            "a <em>spicy</em> link</a>",
        )

    def test_image_renders_void_tag_with_escaped_attributes(self):
        node = Image(
            'images/cat"photo.png?size=1&crop=yes',
            'A "cat" <sleeping> & dreaming',
        )

        actual = inline_node_to_html_node(node)

        self.assertEqual(
            actual.to_html(),
            '<img src="images/cat&quot;photo.png?size=1&amp;crop=yes" '
            'alt="A &quot;cat&quot; &lt;sleeping&gt; &amp; dreaming">',
        )

    def test_empty_inline_container_renders_an_empty_element(self):
        actual = inline_node_to_html_node(Bold([]))

        self.assertIsInstance(actual, LeafNode)
        self.assertEqual(actual.to_html(), "<strong></strong>")

    def test_unknown_inline_node_raises_type_error(self):
        with self.assertRaisesRegex(
            TypeError, "unsupported inline node type: UnknownInline"
        ):
            inline_node_to_html_node(UnknownInline())


class TestBlockNodeToHTMLNode(unittest.TestCase):
    def test_paragraph_renders_inline_children(self):
        node = Paragraph(
            [
                Text("A "),
                Bold([Text("bold")]),
                Text(" paragraph with "),
                Code("x < y"),
                Text("."),
            ]
        )

        actual = block_node_to_html_node(node)

        self.assertEqual(
            actual.to_html(),
            "<p>A <strong>bold</strong> paragraph with "
            "<code>x &lt; y</code>.</p>",
        )

    def test_heading_uses_its_level(self):
        for level in range(1, 7):
            with self.subTest(level=level):
                actual = block_node_to_html_node(Heading(level, [Text("Heading")]))
                self.assertEqual(
                    actual.to_html(),
                    f"<h{level}>Heading</h{level}>",
                )

    def test_invalid_heading_level_raises_value_error(self):
        for level in (0, 7, -1):
            with self.subTest(level=level):
                with self.assertRaisesRegex(
                    ValueError, "heading level must be between 1 and 6"
                ):
                    block_node_to_html_node(Heading(level, [Text("Bad")]))

    def test_code_block_renders_literal_content_inside_pre_and_code(self):
        node = CodeBlock(
            [
                Text("def compare(a, b):\n"),
                Code('    return a < b and a != "**bold**"\n'),
            ]
        )

        actual = block_node_to_html_node(node)

        self.assertEqual(
            actual.to_html(),
            "<pre><code>def compare(a, b):\n"
            '    return a &lt; b and a != "**bold**"\n'
            "</code></pre>",
        )

    def test_code_block_rejects_nonliteral_inline_children(self):
        node = CodeBlock([Bold([Text("not literal")])])

        with self.assertRaisesRegex(
            TypeError, "code blocks may contain only literal Text or Code nodes"
        ):
            block_node_to_html_node(node)

    def test_block_quote_recursively_converts_block_children(self):
        node = BlockQuote(
            [
                Heading(3, [Text("Quoted heading")]),
                Paragraph([Text("Quoted "), Italic([Text("paragraph")])]),
            ]
        )

        actual = block_node_to_html_node(node)

        self.assertEqual(
            actual.to_html(),
            "<blockquote><h3>Quoted heading</h3>"
            "<p>Quoted <em>paragraph</em></p></blockquote>",
        )

    def test_empty_paragraph_renders_an_empty_p_element(self):
        actual = block_node_to_html_node(Paragraph([]))

        self.assertIsInstance(actual, LeafNode)
        self.assertEqual(actual.to_html(), "<p></p>")

    def test_unknown_block_node_raises_type_error(self):
        with self.assertRaisesRegex(
            TypeError, "unsupported block node type: UnknownBlock"
        ):
            block_node_to_html_node(UnknownBlock())


class TestListBlockToHTMLNode(unittest.TestCase):
    def test_unordered_list(self):
        node = ListBlock(
            ListType.UNORDERED,
            [
                ListItem([Text("First")]),
                ListItem([Text("Second with "), Bold([Text("bold")])]),
            ],
        )

        actual = list_block_to_html_node(node)

        self.assertEqual(
            actual.to_html(),
            "<ul><li>First</li><li>Second with <strong>bold</strong></li></ul>",
        )

    def test_ordered_list_starting_at_one_omits_start_attribute(self):
        node = ListBlock(
            ListType.ORDERED,
            [ListItem([Text("One")]), ListItem([Text("Two")])],
            start=1,
        )

        actual = list_block_to_html_node(node)

        self.assertEqual(actual.to_html(), "<ol><li>One</li><li>Two</li></ol>")
        self.assertIsNone(actual.props)

    def test_ordered_list_with_nondefault_start_adds_start_attribute(self):
        node = ListBlock(
            ListType.ORDERED,
            [ListItem([Text("Three")]), ListItem([Text("Four")])],
            start=3,
        )

        actual = list_block_to_html_node(node)

        self.assertEqual(
            actual.to_html(),
            '<ol start="3"><li>Three</li><li>Four</li></ol>',
        )

    def test_empty_list_item_renders_an_empty_li_element(self):
        node = ListBlock(ListType.UNORDERED, [ListItem([])])

        actual = list_block_to_html_node(node)

        self.assertEqual(actual.to_html(), "<ul><li></li></ul>")

    def test_unsupported_list_type_raises_value_error(self):
        node = ListBlock("definition", [ListItem([Text("Term")])])  # type: ignore[arg-type]

        with self.assertRaisesRegex(ValueError, "unsupported list type"):
            list_block_to_html_node(node)


class TestTableToHTMLNode(unittest.TestCase):
    def test_table_with_header_body_and_column_alignments(self):
        table = Table(
            header=TableRow(
                [
                    TableCell([Text("Name")]),
                    TableCell([Text("Role")]),
                    TableCell([Text("Score")]),
                    TableCell([Text("Notes")]),
                ]
            ),
            rows=[
                TableRow(
                    [
                        TableCell([Bold([Text("Ada")])]),
                        TableCell([Text("Engineer")]),
                        TableCell([Code("100 < 101")]),
                        TableCell([]),
                    ]
                )
            ],
            alignments=[
                TableAlignment.LEFT,
                TableAlignment.CENTER,
                TableAlignment.RIGHT,
                TableAlignment.DEFAULT,
            ],
        )

        actual = table_to_html_node(table)

        self.assertEqual(
            actual.to_html(),
            '<table><thead><tr><th style="text-align: left">Name</th>'
            '<th style="text-align: center">Role</th>'
            '<th style="text-align: right">Score</th><th>Notes</th></tr></thead>'
            '<tbody><tr><td style="text-align: left"><strong>Ada</strong></td>'
            '<td style="text-align: center">Engineer</td>'
            '<td style="text-align: right"><code>100 &lt; 101</code></td>'
            "<td></td></tr></tbody></table>",
        )

    def test_missing_alignments_default_every_column(self):
        table = Table(
            header=TableRow(
                [TableCell([Text("A")]), TableCell([Text("B")])]
            ),
            rows=[
                TableRow([TableCell([Text("1")]), TableCell([Text("2")])])
            ],
        )

        actual = table_to_html_node(table)

        self.assertEqual(
            actual.to_html(),
            "<table><thead><tr><th>A</th><th>B</th></tr></thead>"
            "<tbody><tr><td>1</td><td>2</td></tr></tbody></table>",
        )

    def test_header_only_table_omits_tbody(self):
        table = Table(
            header=TableRow([TableCell([Text("Only header")])]),
            alignments=[TableAlignment.DEFAULT],
        )

        actual = table_to_html_node(table)

        self.assertEqual(
            actual.to_html(),
            "<table><thead><tr><th>Only header</th></tr></thead></table>",
        )

    def test_alignment_count_must_match_header_column_count(self):
        table = Table(
            header=TableRow(
                [TableCell([Text("A")]), TableCell([Text("B")])]
            ),
            alignments=[TableAlignment.LEFT],
        )

        with self.assertRaisesRegex(
            ValueError, "table has 1 alignments; expected 2"
        ):
            table_to_html_node(table)

    def test_each_row_must_match_table_column_count(self):
        table = Table(
            header=TableRow(
                [TableCell([Text("A")]), TableCell([Text("B")])]
            ),
            rows=[TableRow([TableCell([Text("only one")])])],
            alignments=[TableAlignment.DEFAULT, TableAlignment.DEFAULT],
        )

        with self.assertRaisesRegex(
            ValueError, "table row has 1 cells; expected 2"
        ):
            table_to_html_node(table)

    def test_table_row_rejects_invalid_cell_tag(self):
        row = TableRow([TableCell([Text("Cell")])])

        with self.assertRaisesRegex(
            ValueError, "table cell tag must be either 'th' or 'td'"
        ):
            table_row_to_html_node(
                row,
                "div",
                [TableAlignment.DEFAULT],
            )


class TestEndToEndMarkdownConversion(unittest.TestCase):
    def test_markdown_document_parses_and_renders_to_html(self):
        markdown = """# Site **Title**

A paragraph with _emphasis_, `code`, and a [link](https://example.com?a=1&b=2).

> A quoted paragraph with **bold** text.

3. Third
4. Fourth

| Name | Score |
| :--- | ---: |
| Ada | 100 |

```
if a < b:
    print("yes")
```"""

        markdown_nodes = markdown_to_markdown_node(markdown)
        actual = markdown_nodes_to_html_node(markdown_nodes)

        self.assertEqual(
            actual.to_html(),
            '<div><h1>Site <strong>Title</strong></h1>'
            '<p>A paragraph with <em>emphasis</em>, <code>code</code>, and a '
            '<a href="https://example.com?a=1&amp;b=2">link</a>.</p>'
            '<blockquote><p>A quoted paragraph with <strong>bold</strong> '
            'text.</p></blockquote>'
            '<ol start="3"><li>Third</li><li>Fourth</li></ol>'
            '<table><thead><tr><th style="text-align: left">Name</th>'
            '<th style="text-align: right">Score</th></tr></thead>'
            '<tbody><tr><td style="text-align: left">Ada</td>'
            '<td style="text-align: right">100</td></tr></tbody></table>'
            '<pre><code>if a &lt; b:\n    print("yes")\n</code></pre></div>',
        )


if __name__ == "__main__":
    unittest.main()
