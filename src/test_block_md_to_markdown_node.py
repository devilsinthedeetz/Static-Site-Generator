import unittest

from block_md_to_markdown_node import (
    BlockType,
    MarkdownSyntaxError,
    block_quote_to_markdown_node,
    block_text_to_markdown_node,
    block_to_block_type,
    code_block_to_markdown_node,
    heading_block_to_html_node,
    markdown_to_blocks,
    markdown_to_markdown_node,
    ordered_list_to_markdown_node,
    parse_table_alignment,
    paragraph_to_markdown_node,
    split_table_row,
    table_block_to_markdown_node,
    table_row_to_markdown_node,
    unordered_list_to_markdown_node,
)
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
    MarkdownNode,
    Paragraph,
    Table,
    TableAlignment,
    TableCell,
    TableRow,
    Text,
)


class TestMarkdownNodeDataModel(unittest.TestCase):
    def test_block_and_inline_nodes_share_markdown_node_base(self):
        self.assertIsInstance(Paragraph(), MarkdownNode)
        self.assertIsInstance(Paragraph(), BlockNode)
        self.assertIsInstance(Text("text"), MarkdownNode)
        self.assertIsInstance(Text("text"), InlineNode)

    def test_nodes_use_structural_equality(self):
        self.assertEqual(
            Paragraph([Text("before "), Bold([Text("bold")])]),
            Paragraph([Text("before "), Bold([Text("bold")])]),
        )
        self.assertNotEqual(Paragraph([Text("a")]), Paragraph([Text("b")]))

    def test_default_child_lists_are_not_shared(self):
        first = Paragraph()
        second = Paragraph()

        first.children.append(Text("first"))

        self.assertEqual(first.children, [Text("first")])
        self.assertEqual(second.children, [])

    def test_list_defaults(self):
        node = ListBlock(ListType.UNORDERED, [])

        self.assertEqual(node.start, 1)
        self.assertTrue(node.tight)

    def test_table_defaults(self):
        node = Table(header=TableRow())

        self.assertEqual(node.rows, [])
        self.assertEqual(node.alignments, [])


class TestBlockDispatch(unittest.TestCase):
    def test_invalid_block_type_raises(self):
        with self.assertRaisesRegex(ValueError, "invalid block_type"):
            block_text_to_markdown_node(object(), "text")


class TestMarkdownToBlocks(unittest.TestCase):
    def test_empty_document_returns_no_blocks(self):
        self.assertEqual(markdown_to_blocks(""), [])
        self.assertEqual(markdown_to_blocks(" \n\n\t"), [])

    def test_splits_on_blank_lines_and_strips_outer_whitespace(self):
        markdown = "  first block  \n\n\n  second block\n"

        self.assertEqual(markdown_to_blocks(markdown), ["first block", "second block"])

    def test_preserves_single_newlines_inside_a_block(self):
        self.assertEqual(
            markdown_to_blocks("first line\nsecond line"),
            ["first line\nsecond line"],
        )

    def test_does_not_split_on_blank_lines_inside_fenced_code(self):
        markdown = "```\nfirst line\n\nsecond line\n```\n\nafter"

        self.assertEqual(
            markdown_to_blocks(markdown),
            ["```\nfirst line\n\nsecond line\n```", "after"],
        )


class TestBlockClassification(unittest.TestCase):
    def test_classifies_each_supported_block_type(self):
        cases = {
            "# heading": BlockType.HEADING,
            "```\ncode\n```": BlockType.CODE,
            "~~~\ncode\n~~~": BlockType.CODE,
            "> quote\n> second line": BlockType.QUOTE,
            "- first\n- second": BlockType.UNORDERED_LIST,
            "3. first\n4. second": BlockType.ORDERED_LIST,
            "| A | B |\n| --- | --- |\n| 1 | 2 |": BlockType.TABLE,
            "ordinary paragraph": BlockType.PARAGRAPH,
        }

        for markdown, expected in cases.items():
            with self.subTest(markdown=markdown):
                self.assertEqual(block_to_block_type(markdown), expected)

    def test_mixed_quote_lines_are_a_paragraph(self):
        self.assertEqual(
            block_to_block_type("> quote\nnot quoted"),
            BlockType.PARAGRAPH,
        )

    def test_mixed_unordered_list_lines_are_a_paragraph(self):
        self.assertEqual(
            block_to_block_type("- item\nnot an item"),
            BlockType.PARAGRAPH,
        )

    def test_ordered_list_marker_requires_a_space(self):
        self.assertEqual(block_to_block_type("1.no space"), BlockType.PARAGRAPH)

    def test_heading_marker_requires_space_or_end_of_line(self):
        self.assertEqual(block_to_block_type("#not-a-heading"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("####### too many"), BlockType.PARAGRAPH)

    def test_descending_ordered_markers_are_not_classified_as_one_list(self):
        self.assertEqual(
            block_to_block_type("2. second\n1. first"),
            BlockType.PARAGRAPH,
        )

    def test_pipe_text_without_delimiter_row_is_a_paragraph(self):
        self.assertEqual(
            block_to_block_type("A | B\nnot | delimiters"),
            BlockType.PARAGRAPH,
        )


class TestIndividualBlockConversion(unittest.TestCase):
    def test_paragraph_replaces_soft_line_breaks_with_spaces(self):
        self.assertEqual(
            paragraph_to_markdown_node("one **bold** line\nand _italic_ text"),
            Paragraph(
                [
                    Text("one "),
                    Bold([Text("bold")]),
                    Text(" line and "),
                    Italic([Text("italic")]),
                    Text(" text"),
                ]
            ),
        )

    def test_heading_strips_marker_and_parses_inline_children(self):
        self.assertEqual(
            heading_block_to_html_node("### A **bold** heading"),
            Heading(3, [Text("A "), Bold([Text("bold")]), Text(" heading")]),
        )

    def test_all_heading_levels(self):
        for level in range(1, 7):
            with self.subTest(level=level):
                self.assertEqual(
                    heading_block_to_html_node(f"{'#' * level} heading"),
                    Heading(level, [Text("heading")]),
                )

    def test_malformed_heading_converter_input_raises(self):
        with self.assertRaisesRegex(MarkdownSyntaxError, "malformed"):
            heading_block_to_html_node("not a heading")

    def test_backtick_code_block_preserves_literal_markdown(self):
        self.assertEqual(
            code_block_to_markdown_node("```\n**not bold**\n_line_\n```"),
            CodeBlock([Text("**not bold**\n_line_\n")]),
        )

    def test_tilde_code_block(self):
        self.assertEqual(
            code_block_to_markdown_node("~~~\nprint('hello')\n~~~"),
            CodeBlock([Text("print('hello')\n")]),
        )

    def test_empty_code_block(self):
        self.assertEqual(
            code_block_to_markdown_node("```\n\n```"),
            CodeBlock([Text("\n")]),
        )

    def test_code_content_starting_or_ending_with_fence_characters_is_preserved(self):
        self.assertEqual(
            code_block_to_markdown_node("```\n`starts and ends`\n```"),
            CodeBlock([Text("`starts and ends`\n")]),
        )
        self.assertEqual(
            code_block_to_markdown_node("~~~\n~value~\n~~~"),
            CodeBlock([Text("~value~\n")]),
        )

    def test_code_fence_without_newline_raises_syntax_error(self):
        with self.assertRaises(MarkdownSyntaxError):
            code_block_to_markdown_node("```")

    def test_non_code_text_rejected_by_code_converter(self):
        with self.assertRaisesRegex(ValueError, "not a code block"):
            code_block_to_markdown_node("ordinary text")

    def test_code_fence_info_string_is_explicitly_unsupported(self):
        with self.assertRaises(NotImplementedError):
            code_block_to_markdown_node("```python\nprint('hello')\n```")

    def test_unclosed_code_block_raises_syntax_error(self):
        with self.assertRaises(MarkdownSyntaxError):
            code_block_to_markdown_node("```\nmissing close")

    def test_single_paragraph_block_quote(self):
        self.assertEqual(
            block_quote_to_markdown_node("> quoted **text**\n> continues here"),
            BlockQuote(
                [
                    Paragraph(
                        [
                            Text("quoted "),
                            Bold([Text("text")]),
                            Text(" continues here"),
                        ]
                    )
                ]
            ),
        )

    def test_block_quote_can_contain_multiple_blocks(self):
        self.assertEqual(
            block_quote_to_markdown_node("> first paragraph\n>\n> - one\n> - two"),
            BlockQuote(
                [
                    Paragraph([Text("first paragraph")]),
                    ListBlock(
                        ListType.UNORDERED,
                        [ListItem([Text("one")]), ListItem([Text("two")])],
                    ),
                ]
            ),
        )

    def test_unordered_list_parses_inline_children(self):
        self.assertEqual(
            unordered_list_to_markdown_node(
                "- plain\n- **bold** and [link](https://example.com)"
            ),
            ListBlock(
                ListType.UNORDERED,
                [
                    ListItem([Text("plain")]),
                    ListItem(
                        [
                            Bold([Text("bold")]),
                            Text(" and "),
                            Link("https://example.com", [Text("link")]),
                        ]
                    ),
                ],
            ),
        )

    def test_ordered_list_preserves_start_number(self):
        self.assertEqual(
            ordered_list_to_markdown_node("3. third\n4. fourth"),
            ListBlock(
                ListType.ORDERED,
                [ListItem([Text("third")]), ListItem([Text("fourth")])],
                start=3,
            ),
        )

    def test_table_without_body_rows(self):
        self.assertEqual(
            table_block_to_markdown_node("| A | B |\n| --- | :---: |"),
            Table(
                header=TableRow([TableCell([Text("A")]), TableCell([Text("B")])]),
                rows=[],
                alignments=[TableAlignment.DEFAULT, TableAlignment.CENTER],
            ),
        )

    def test_table_row_converter_parses_inline_children(self):
        self.assertEqual(
            table_row_to_markdown_node("| **A** | `b|c` |"),
            TableRow([TableCell([Bold([Text("A")])]), TableCell([Code("b|c")])]),
        )

    def test_blank_table_row_raises(self):
        with self.assertRaisesRegex(MarkdownSyntaxError, "cannot be blank"):
            split_table_row("   ")

    def test_invalid_alignment_delimiter_raises(self):
        for delimiter in ("--", "abc", ":--:", "---x"):
            with self.subTest(delimiter=delimiter):
                with self.assertRaises(MarkdownSyntaxError):
                    parse_table_alignment(delimiter)

    def test_table_requires_header_and_delimiter_rows(self):
        with self.assertRaisesRegex(MarkdownSyntaxError, "requires"):
            table_block_to_markdown_node("| header |")

    def test_table_header_and_delimiter_counts_must_match(self):
        with self.assertRaisesRegex(MarkdownSyntaxError, "same number"):
            table_block_to_markdown_node("| A | B |\n| --- |")


class TestMarkdownToMarkdownNodeIntegration(unittest.TestCase):
    def test_empty_document_returns_empty_list(self):
        self.assertEqual(markdown_to_markdown_node(""), [])

    def test_single_paragraph_document(self):
        self.assertEqual(
            markdown_to_markdown_node("Hello **world**."),
            [Paragraph([Text("Hello "), Bold([Text("world")]), Text(".")])],
        )

    def test_complete_document_returns_full_ast(self):
        markdown = """\
# Markdown AST

A paragraph with **bold**, _italic_, `code`, a [link](https://example.com), and ![alt](image.png).

> A quote with **bold** text.
>
> - quoted item one
> - quoted item two

- first item
- second item with _style_

3. third item
4. fourth item with [link](https://example.com/list)

```\nprint("**literal markdown**")\n```

| Name | Description | Value |
| :--- | :---------: | ----: |
| **Alpha** | [a _styled_ link](https://example.com/alpha) | `a|b` |
| Beta | ![icon](beta.png) | 2 |
"""

        expected = [
            Heading(1, [Text("Markdown AST")]),
            Paragraph(
                [
                    Text("A paragraph with "),
                    Bold([Text("bold")]),
                    Text(", "),
                    Italic([Text("italic")]),
                    Text(", "),
                    Code("code"),
                    Text(", a "),
                    Link("https://example.com", [Text("link")]),
                    Text(", and "),
                    Image("image.png", "alt"),
                    Text("."),
                ]
            ),
            BlockQuote(
                [
                    Paragraph(
                        [Text("A quote with "), Bold([Text("bold")]), Text(" text.")]
                    ),
                    ListBlock(
                        ListType.UNORDERED,
                        [
                            ListItem([Text("quoted item one")]),
                            ListItem([Text("quoted item two")]),
                        ],
                    ),
                ]
            ),
            ListBlock(
                ListType.UNORDERED,
                [
                    ListItem([Text("first item")]),
                    ListItem([Text("second item with "), Italic([Text("style")])]),
                ],
            ),
            ListBlock(
                ListType.ORDERED,
                [
                    ListItem([Text("third item")]),
                    ListItem(
                        [
                            Text("fourth item with "),
                            Link("https://example.com/list", [Text("link")]),
                        ]
                    ),
                ],
                start=3,
            ),
            CodeBlock([Text('print("**literal markdown**")\n')]),
            Table(
                header=TableRow(
                    [
                        TableCell([Text("Name")]),
                        TableCell([Text("Description")]),
                        TableCell([Text("Value")]),
                    ]
                ),
                rows=[
                    TableRow(
                        [
                            TableCell([Bold([Text("Alpha")])]),
                            TableCell(
                                [
                                    Link(
                                        "https://example.com/alpha",
                                        [
                                            Text("a "),
                                            Italic([Text("styled")]),
                                            Text(" link"),
                                        ],
                                    )
                                ]
                            ),
                            TableCell([Code("a|b")]),
                        ]
                    ),
                    TableRow(
                        [
                            TableCell([Text("Beta")]),
                            TableCell([Image("beta.png", "icon")]),
                            TableCell([Text("2")]),
                        ]
                    ),
                ],
                alignments=[
                    TableAlignment.LEFT,
                    TableAlignment.CENTER,
                    TableAlignment.RIGHT,
                ],
            ),
        ]

        self.assertEqual(markdown_to_markdown_node(markdown), expected)

    def test_fenced_code_with_blank_lines_survives_full_document_parsing(self):
        markdown = "```\nfirst line\n\nsecond line\n```\n\nafter"

        self.assertEqual(
            markdown_to_markdown_node(markdown),
            [
                CodeBlock([Text("first line\n\nsecond line\n")]),
                Paragraph([Text("after")]),
            ],
        )

    def test_unclosed_fenced_code_error_propagates_from_full_document(self):
        with self.assertRaises(ValueError):
            markdown_to_markdown_node("```\nmissing close")

    def test_nodes_appear_in_document_order(self):
        result = markdown_to_markdown_node(
            "first\n\n- item\n\n| H |\n| --- |\n| cell |\n\nlast"
        )

        self.assertEqual(
            [type(node) for node in result],
            [Paragraph, ListBlock, Table, Paragraph],
        )
        self.assertEqual(result[0], Paragraph([Text("first")]))
        self.assertEqual(result[-1], Paragraph([Text("last")]))

    def test_inline_syntax_error_propagates_from_nested_block(self):
        with self.assertRaisesRegex(ValueError, "unclosed"):
            markdown_to_markdown_node("- valid\n- **broken")


if __name__ == "__main__":
    unittest.main()
