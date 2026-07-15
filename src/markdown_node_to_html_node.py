from __future__ import annotations

from html import escape

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
from htmlnode import HTMLNode, LeafNode, ParentNode


def markdown_nodes_to_html_node(markdown_nodes: list[BlockNode]) -> ParentNode:
    """Convert a Markdown document AST into one root ``<div>`` node.

    ``markdown_to_markdown_node()`` returns a list because a Markdown document
    can contain several top-level block nodes. This function converts each
    block independently and places the resulting HTML nodes under one root.
    """
    return ParentNode(
        "div",
        [block_node_to_html_node(node) for node in markdown_nodes],
    )


def block_node_to_html_node(node: BlockNode) -> HTMLNode:
    """Convert one block-level Markdown node into an HTML node."""
    if isinstance(node, Paragraph):
        return _container_node("p", inline_nodes_to_html_nodes(node.children))

    if isinstance(node, Heading):
        if not 1 <= node.lvl <= 6:
            raise ValueError(f"heading level must be between 1 and 6, got {node.lvl}")
        return _container_node(
            f"h{node.lvl}", inline_nodes_to_html_nodes(node.children)
        )

    if isinstance(node, CodeBlock):
        code_node = LeafNode("code", escape(_code_block_text(node), quote=False))
        return ParentNode("pre", [code_node])

    if isinstance(node, BlockQuote):
        return _container_node(
            "blockquote",
            [block_node_to_html_node(child) for child in node.children],
        )

    if isinstance(node, ListBlock):
        return list_block_to_html_node(node)

    if isinstance(node, Table):
        return table_to_html_node(node)

    raise TypeError(f"unsupported block node type: {type(node).__name__}")


def inline_nodes_to_html_nodes(nodes: list[InlineNode]) -> list[HTMLNode]:
    """Convert a sequence of inline Markdown nodes, preserving its order."""
    return [inline_node_to_html_node(node) for node in nodes]


def inline_node_to_html_node(node: InlineNode) -> HTMLNode:
    """Convert one inline Markdown node into an HTML node."""
    if isinstance(node, Text):
        return LeafNode(None, escape(node.value, quote=False))

    if isinstance(node, Bold):
        return _container_node("strong", inline_nodes_to_html_nodes(node.children))

    if isinstance(node, Italic):
        return _container_node("em", inline_nodes_to_html_nodes(node.children))

    if isinstance(node, Code):
        return LeafNode("code", escape(node.value, quote=False))

    if isinstance(node, Link):
        return _container_node(
            "a",
            inline_nodes_to_html_nodes(node.children),
            {"href": escape(node.url, quote=True)},
        )

    if isinstance(node, Image):
        return LeafNode(
            "img",
            "",
            {
                "src": escape(node.url, quote=True),
                "alt": escape(node.alt, quote=True),
            },
        )

    raise TypeError(f"unsupported inline node type: {type(node).__name__}")


def list_block_to_html_node(node: ListBlock) -> HTMLNode:
    """Convert an ordered or unordered list and all of its list items."""
    list_children = [list_item_to_html_node(item) for item in node.items]

    if node.list_type == ListType.UNORDERED:
        return _container_node("ul", list_children)

    if node.list_type == ListType.ORDERED:
        props = None if node.start == 1 else {"start": str(node.start)}
        return _container_node("ol", list_children, props)

    raise ValueError(f"unsupported list type: {node.list_type!r}")


def list_item_to_html_node(item: ListItem) -> HTMLNode:
    return _container_node("li", inline_nodes_to_html_nodes(item.children))


def table_to_html_node(table: Table) -> HTMLNode:
    """Convert a Markdown table into ``table``, ``thead``, and ``tbody`` nodes."""
    column_count = len(table.header.cells)
    alignments = _normalized_table_alignments(table.alignments, column_count)

    header_row = table_row_to_html_node(table.header, "th", alignments)
    table_children: list[HTMLNode] = [ParentNode("thead", [header_row])]

    if table.rows:
        body_rows = [
            table_row_to_html_node(row, "td", alignments) for row in table.rows
        ]
        table_children.append(ParentNode("tbody", body_rows))

    return ParentNode("table", table_children)


def table_row_to_html_node(
    row: TableRow,
    cell_tag: str,
    alignments: list[TableAlignment],
) -> HTMLNode:
    if cell_tag not in ("th", "td"):
        raise ValueError("table cell tag must be either 'th' or 'td'")

    if len(row.cells) != len(alignments):
        raise ValueError(
            f"table row has {len(row.cells)} cells; expected {len(alignments)}"
        )

    cells = [
        table_cell_to_html_node(cell, cell_tag, alignment)
        for cell, alignment in zip(row.cells, alignments)
    ]
    return _container_node("tr", cells)


def table_cell_to_html_node(
    cell: TableCell,
    tag: str,
    alignment: TableAlignment = TableAlignment.DEFAULT,
) -> HTMLNode:
    props = _table_alignment_props(alignment)
    return _container_node(tag, inline_nodes_to_html_nodes(cell.children), props)


def _code_block_text(node: CodeBlock) -> str:
    """Return code block content without interpreting inline Markdown."""
    pieces: list[str] = []

    for child in node.children:
        if not isinstance(child, (Text, Code)):
            raise TypeError(
                "code blocks may contain only literal Text or Code nodes, "
                f"got {type(child).__name__}"
            )
        pieces.append(child.value)

    return "".join(pieces)


def _normalized_table_alignments(
    alignments: list[TableAlignment],
    column_count: int,
) -> list[TableAlignment]:
    if not alignments:
        return [TableAlignment.DEFAULT] * column_count

    if len(alignments) != column_count:
        raise ValueError(
            f"table has {len(alignments)} alignments; expected {column_count}"
        )

    return alignments


def _table_alignment_props(
    alignment: TableAlignment,
) -> dict[str, str] | None:
    if alignment == TableAlignment.DEFAULT:
        return None

    if alignment not in (
        TableAlignment.LEFT,
        TableAlignment.CENTER,
        TableAlignment.RIGHT,
    ):
        raise ValueError(f"unsupported table alignment: {alignment!r}")

    return {"style": f"text-align: {alignment.value}"}


def _container_node(
    tag: str,
    children: list[HTMLNode],
    props: dict[str, str] | None = None,
) -> HTMLNode:
    """Create a renderable HTML container, including when it is empty.

    ``ParentNode.to_html()`` currently rejects an empty child list. A LeafNode
    with an empty value renders the same empty non-void element, so using it
    here lets valid constructs such as an empty table cell or link render
    without changing the HTML node implementation.
    """
    if children:
        return ParentNode(tag, children, props)
    return LeafNode(tag, "", props)
