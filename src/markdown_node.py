from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field


class ListType(Enum):
    UNORDERED = "unordered"
    ORDERED = "ordered"


class TableAlignment(Enum):
    DEFAULT = "default"
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class MarkdownNode:
    pass


@dataclass
class BlockNode(MarkdownNode):
    pass


@dataclass
class InlineNode(MarkdownNode):
    pass


@dataclass
class Heading(BlockNode):
    lvl: int
    children: list[MarkdownNode] = field(default_factory=list)


@dataclass
class Paragraph(BlockNode):
    children: list[MarkdownNode] = field(default_factory=list)


@dataclass
class BlockQuote(BlockNode):
    children: list[MarkdownNode] = field(default_factory=list)


@dataclass
class CodeBlock(BlockNode):
    children: list[MarkdownNode] = field(default_factory=list)


@dataclass
class ListBlock(BlockNode):
    list_type: ListType
    items: list[ListItem]
    start: int = 1
    tight: bool = True


@dataclass
class ListItem(MarkdownNode):
    children: list[BlockNode] = field(default_factory=list)


@dataclass
class Table(BlockNode):
    header: TableRow
    rows: list[TableRow] = field(default_factory=list)
    alignments: list[TableAlignment] = field(default_factory=list)


@dataclass
class TableRow(MarkdownNode):
    cells: list[TableCell] = field(default_factory=list)


@dataclass
class TableCell(MarkdownNode):
    children: list[InlineNode] = field(default_factory=list)


@dataclass
class Bold(InlineNode):
    children: list[MarkdownNode] = field(default_factory=list)


@dataclass
class Italic(InlineNode):
    children: list[MarkdownNode] = field(default_factory=list)


@dataclass
class Text(InlineNode):
    value: str


@dataclass
class Code(InlineNode):
    value: str


@dataclass
class Link(InlineNode):
    url: str
    children: list[MarkdownNode] = field(default_factory=list)


@dataclass
class Image(MarkdownNode):
    url: str
    alt: str
