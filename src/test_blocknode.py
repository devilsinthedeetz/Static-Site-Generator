import unittest
from blocknode import (
    BlockType,
    markdown_to_blocks,
    block_to_block_type,
    block_node_to_html_node,
    markdown_to_html_node,
)
from htmlnode import LeafNode, ParentNode


class TestBlockConversion(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_empty_string(self):
        self.assertEqual(markdown_to_blocks(""), [])

    def test_whitespace_only(self):
        md = "   \n\n\t\n\n   "
        self.assertEqual(markdown_to_blocks(md), [])

    def test_strips_whitespace_from_blocks(self):
        md = "   First block   \n\n   Second block   "
        self.assertEqual(
            markdown_to_blocks(md),
            ["First block", "Second block"],
        )

    def test_removes_empty_blocks(self):
        md = "First block\n\n\n\nSecond block"
        self.assertEqual(
            markdown_to_blocks(md),
            ["First block", "Second block"],
        )

    def test_single_block(self):
        md = "Just one paragraph\nwith two lines"
        self.assertEqual(
            markdown_to_blocks(md),
            ["Just one paragraph\nwith two lines"],
        )

    def test_multiple_empty_lines_between_blocks(self):
        md = "First\n\n\n\n\n\nSecond"
        self.assertEqual(
            markdown_to_blocks(md),
            ["First", "Second"],
        )

    def test_mid_block_white_space(self):
        md = """
~~~
I am a code block
     with an indent
~~~

no indent here!
"""
        self.assertEqual(
            markdown_to_blocks(md),
            ["~~~\nI am a code block\n     with an indent\n~~~", "no indent here!"],
        )

    def test_block_to_ordered_list_block_type(self):
        md = "1. apple\n2. banana\n3. orange"
        self.assertEqual(block_to_block_type(md), BlockType.ORDERED_LIST)

    def test_block_to_block_type_ordered_list_defence(self):
        md = "43. not\n3. an\n2. ordered\n89. list"
        self.assertEqual(block_to_block_type(md), BlockType.PARAGRAPH)

    def test_block_to_block_type_unordered_list(self):
        md = "- chocolate cake\n- glass of beer\n- cup of rosie lee"
        self.assertEqual(block_to_block_type(md), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_heading(self):
        md_blocks = [
            "# I am a heading",
            "## I am a sub heading",
            "### I am a sub-sub heading",
            "#### And so on",
            "##### And so forth",
            "###### smol heading",
        ]
        for md in md_blocks:
            self.assertEqual(block_to_block_type(md), BlockType.HEADING)

    def test_block_to_block_type_code(self):
        md_blocks = [
            "~~~\nI am a code block\nsee me roar\n~~~",
            "```\nI am also a code block\nI don't need to roar\n```",
        ]
        for md in md_blocks:
            self.assertEqual(block_to_block_type(md), BlockType.CODE)

    def test_block_to_block_type_quote(self):
        md = """>I am a block quote
>I can make quotes look pretty
> I can have white space after the greater than sign"""
        self.assertEqual(block_to_block_type(md), BlockType.QUOTE)

    def test_block_to_block_type_paragraph(self):
        md = """```Look at me I a am a paragraph
1. it does not matter if some of my lines
> have elements of other blocks
- so we must make sure we are
       well formatted ~~~"""
        self.assertEqual(block_to_block_type(md), BlockType.PARAGRAPH)

    def test_heading_block_to_html_node(self):
        block_text = "### I am a heading block"
        self.assertEqual(
            block_node_to_html_node(BlockType.HEADING, block_text),
            ParentNode("h3", [LeafNode(None, "I am a heading block")]),
        )

    def test_paragraph_block_to_html_node(self):
        block_text = (
            "Look at **me**,\nI am a paragraph\nwith new lines\nthat will be replaced"
        )
        self.assertEqual(
            block_node_to_html_node(BlockType.PARAGRAPH, block_text),
            ParentNode(
                "p",
                [
                    LeafNode(None, "Look at "),
                    LeafNode("b", "me"),
                    LeafNode(
                        None, ", I am a paragraph with new lines that will be replaced"
                    ),
                ],
            ),
        )

    def test_code_block_to_html_node(self):
        block_text = """```
This is text that _should_ remain
the **same** even with inline stuff
```"""
        self.assertEqual(
            block_node_to_html_node(BlockType.CODE, block_text),
            ParentNode(
                "pre",
                [
                    LeafNode(
                        "code",
                        "This is text that _should_ remain\nthe **same** even with inline stuff\n",
                    )
                ],
            ),
        )

    def test_block_quote_to_html_node(self):
        block_text = """>I am a block quote
>all my lines
>begin with greater than signs"""
        self.assertEqual(
            block_node_to_html_node(BlockType.QUOTE, block_text),
            ParentNode(
                "blockquote",
                [
                    LeafNode(
                        None,
                        "I am a block quote\nall my lines\nbegin with greater than signs",
                    )
                ],
            ),
            f"{block_node_to_html_node(BlockType.QUOTE, block_text)}\n\n{
                ParentNode(
                    'blockquote',
                    [
                        LeafNode(
                            None,
                            'I am a block quote\nall my lines\nbegin with greater than signs',
                        )
                    ],
                )
            }",
        )

    def test_unordered_list_to_html_node(self):
        block_text = """- banana
- apple
- orange
- kiwi"""
        self.assertEqual(
            block_node_to_html_node(BlockType.UNORDERED_LIST, block_text),
            ParentNode(
                "ul",
                [
                    ParentNode("li", [LeafNode(None, "banana")]),
                    ParentNode("li", [LeafNode(None, "apple")]),
                    ParentNode("li", [LeafNode(None, "orange")]),
                    ParentNode("li", [LeafNode(None, "kiwi")]),
                ],
            ),
        )

    def test_ordered_list_to_html_node(self):
        block_text = """1. banana
2. apple
3. orange
4. kiwi"""
        self.assertEqual(
            block_node_to_html_node(BlockType.ORDERED_LIST, block_text),
            ParentNode(
                "ol",
                [
                    ParentNode("li", [LeafNode(None, "banana")]),
                    ParentNode("li", [LeafNode(None, "apple")]),
                    ParentNode("li", [LeafNode(None, "orange")]),
                    ParentNode("li", [LeafNode(None, "kiwi")]),
                ],
            ),
        )

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_markdown_to_html_node_builds_complete_tree(self):
        md = """# Site title

This is **bold**, _italic_, and [linked](https://example.com).

> A quoted line
> with `code`

- first item
- second item

1. one
2. two

```
raw **markdown**
```
"""

        self.assertEqual(
            markdown_to_html_node(md),
            ParentNode(
                "div",
                [
                    ParentNode("h1", [LeafNode(None, "Site title")]),
                    ParentNode(
                        "p",
                        [
                            LeafNode(None, "This is "),
                            LeafNode("b", "bold"),
                            LeafNode(None, ", "),
                            LeafNode("i", "italic"),
                            LeafNode(None, ", and "),
                            LeafNode(
                                "a",
                                "linked",
                                {"href": "https://example.com"},
                            ),
                            LeafNode(None, "."),
                        ],
                    ),
                    ParentNode(
                        "blockquote",
                        [
                            LeafNode(None, " A quoted line\n with "),
                            LeafNode("code", "code"),
                        ],
                    ),
                    ParentNode(
                        "ul",
                        [
                            ParentNode("li", [LeafNode(None, "first item")]),
                            ParentNode("li", [LeafNode(None, "second item")]),
                        ],
                    ),
                    ParentNode(
                        "ol",
                        [
                            ParentNode("li", [LeafNode(None, "one")]),
                            ParentNode("li", [LeafNode(None, "two")]),
                        ],
                    ),
                    ParentNode(
                        "pre",
                        [LeafNode("code", "raw **markdown**\n")],
                    ),
                ],
            ),
        )

    def test_markdown_to_html_node_serializes_mixed_document(self):
        md = """## Heading

A paragraph with ![alt text](image.png).

- alpha
- beta
"""

        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><h2>Heading</h2><p>A paragraph with "
            '<img src="image.png" alt="alt text">.</p>'
            "<ul><li>alpha</li><li>beta</li></ul></div>",
        )

    def test_empty_document_returns_empty_div_node(self):
        node = markdown_to_html_node("")

        self.assertEqual(node, ParentNode("div", []))
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.children, [])

    def test_unordered_list_keeps_inline_nodes_in_same_list_item(self):
        md = """- plain and **bold** text
- a [link](https://example.com) here"""

        self.assertEqual(
            markdown_to_html_node(md),
            ParentNode(
                "div",
                [
                    ParentNode(
                        "ul",
                        [
                            ParentNode(
                                "li",
                                [
                                    LeafNode(None, "plain and "),
                                    LeafNode("b", "bold"),
                                    LeafNode(None, " text"),
                                ],
                            ),
                            ParentNode(
                                "li",
                                [
                                    LeafNode(None, "a "),
                                    LeafNode(
                                        "a",
                                        "link",
                                        {"href": "https://example.com"},
                                    ),
                                    LeafNode(None, " here"),
                                ],
                            ),
                        ],
                    )
                ],
            ),
        )

    def test_ordered_list_keeps_inline_nodes_in_same_list_item(self):
        md = """1. first has _italics_
2. second has `code`"""

        self.assertEqual(
            markdown_to_html_node(md),
            ParentNode(
                "div",
                [
                    ParentNode(
                        "ol",
                        [
                            ParentNode(
                                "li",
                                [
                                    LeafNode(None, "first has "),
                                    LeafNode("i", "italics"),
                                ],
                            ),
                            ParentNode(
                                "li",
                                [
                                    LeafNode(None, "second has "),
                                    LeafNode("code", "code"),
                                ],
                            ),
                        ],
                    )
                ],
            ),
        )
