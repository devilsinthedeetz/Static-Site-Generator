import unittest

from block_md_to_markdown_node import (
    BlockType,
    MarkdownSyntaxError,
    block_to_block_type,
    markdown_to_markdown_node,
    split_table_row,
    table_block_to_markdown_node,
)
from markdown_node import (
    Bold,
    Code,
    Italic,
    Link,
    Table,
    TableAlignment,
    TableCell,
    TableRow,
    Text,
)


class TestMarkdownTables(unittest.TestCase):
    def test_parses_table_with_alignment_and_inline_markdown(self):
        markdown = """\
| Name | Description | Expression |
| :--- | :---------: | ---------: |
| **Alpha** | [a _spicy_ link](https://example.com) | `a|b` |
"""

        self.assertEqual(
            markdown_to_markdown_node(markdown),
            [
                Table(
                    header=TableRow(
                        [
                            TableCell([Text("Name")]),
                            TableCell([Text("Description")]),
                            TableCell([Text("Expression")]),
                        ]
                    ),
                    rows=[
                        TableRow(
                            [
                                TableCell([Bold([Text("Alpha")])]),
                                TableCell(
                                    [
                                        Link(
                                            url="https://example.com",
                                            children=[
                                                Text("a "),
                                                Italic([Text("spicy")]),
                                                Text(" link"),
                                            ],
                                        )
                                    ]
                                ),
                                TableCell([Code("a|b")]),
                            ]
                        )
                    ],
                    alignments=[
                        TableAlignment.LEFT,
                        TableAlignment.CENTER,
                        TableAlignment.RIGHT,
                    ],
                )
            ],
        )

    def test_leading_and_trailing_pipes_are_optional(self):
        markdown = """\
Name | Value
--- | ---:
Alpha | 10
"""

        table = markdown_to_markdown_node(markdown)[0]

        self.assertIsInstance(table, Table)
        self.assertEqual(table.alignments, [TableAlignment.DEFAULT, TableAlignment.RIGHT])
        self.assertEqual(table.rows[0].cells[1].children, [Text("10")])

    def test_escaped_pipe_remains_inside_cell(self):
        self.assertEqual(
            split_table_row(r"| left \| right | other |"),
            ["left | right", "other"],
        )

    def test_empty_cells_are_preserved(self):
        table = table_block_to_markdown_node(
            "| A | B |\n| --- | --- |\n| | value |"
        )

        self.assertEqual(table.rows[0].cells[0], TableCell([]))
        self.assertEqual(table.rows[0].cells[1], TableCell([Text("value")]))

    def test_body_row_with_wrong_cell_count_raises(self):
        with self.assertRaisesRegex(
            MarkdownSyntaxError,
            r"table row 3 has 1 cells; expected 2",
        ):
            table_block_to_markdown_node(
                "| A | B |\n| --- | --- |\n| only one cell |"
            )

    def test_pipe_block_without_delimiter_row_is_not_a_table(self):
        block = "| this | has | pipes |\n| but | no | delimiter |"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


if __name__ == "__main__":
    unittest.main()
