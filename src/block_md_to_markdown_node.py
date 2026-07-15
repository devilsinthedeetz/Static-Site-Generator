from __future__ import annotations
from enum import Enum
import re
from markdown_node import (
    InlineNode,
    BlockNode,
    Paragraph,
    Text,
    Heading,
    CodeBlock,
    BlockQuote,
    ListBlock,
    ListItem,
    ListType,
    Table,
    TableRow,
    TableCell,
    TableAlignment,
)
from inline_md_to_markdown_node import inline_md_to_markdown_node


class MarkdownSyntaxError(ValueError):
    pass


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    TABLE = "table"


def markdown_to_markdown_node(md) -> list[BlockNode]:
    split_text_blocks: list[str] = markdown_to_blocks(md)
    nodes: list[BlockNode] = []
    for block_text in split_text_blocks:
        block_type: BlockType = block_to_block_type(block_text)
        block_node: BlockNode = block_text_to_markdown_node(block_type, block_text)
        nodes.append(block_node)
    return nodes


def block_text_to_markdown_node(block_type, block_text) -> BlockNode:
    if block_type == BlockType.HEADING:
        return heading_block_to_html_node(block_text)
    if block_type == BlockType.CODE:
        return code_block_to_markdown_node(block_text)
    if block_type == BlockType.QUOTE:
        return block_quote_to_markdown_node(block_text)
    if block_type == BlockType.UNORDERED_LIST:
        return unordered_list_to_markdown_node(block_text)
    if block_type == BlockType.ORDERED_LIST:
        return ordered_list_to_markdown_node(block_text)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_markdown_node(block_text)
    if block_type == BlockType.TABLE:
        return table_block_to_markdown_node(block_text)
    raise ValueError("invalid block_type")


def markdown_to_blocks(md: str) -> list[str]:
    """Split a document on blank lines, except inside fenced code blocks."""
    blocks: list[str] = []
    current_lines: list[str] = []
    active_fence: str | None = None

    for line in md.splitlines():
        stripped_line = line.strip()

        if active_fence is not None:
            current_lines.append(line)
            if stripped_line == active_fence:
                active_fence = None
            continue

        if stripped_line.startswith("```"):
            active_fence = "```"
            current_lines.append(line)
            continue

        if stripped_line.startswith("~~~"):
            active_fence = "~~~"
            current_lines.append(line)
            continue

        if stripped_line == "":
            if current_lines:
                blocks.append("\n".join(current_lines).strip())
                current_lines.clear()
            continue

        current_lines.append(line)

    if current_lines:
        blocks.append("\n".join(current_lines).strip())

    return blocks


def block_to_block_type(block: str) -> BlockType:
    if re.match(r"^#{1,6}(?:[ \t]+|$)", block):
        return BlockType.HEADING
    if (block.startswith("```\n") and block.endswith("\n```")) or (
        block.startswith("~~~\n") and block.endswith("\n~~~")
    ):
        return BlockType.CODE
    new_lines = block.split("\n")
    if all(line.startswith(">") for line in new_lines):
        return BlockType.QUOTE
    if all(line.startswith("- ") for line in new_lines):
        return BlockType.UNORDERED_LIST
    if is_table_block(block):
        return BlockType.TABLE
    num_list: list[int] = []
    has_num_list = True
    for line in new_lines:
        match = re.match(r"^(\d+)\. ", line)
        if match:
            num_list.append(int(match.group(1)))

        else:
            has_num_list = False
    if has_num_list:
        copy_nums = num_list.copy()
        sorted_nums = sorted(copy_nums)
        if sorted_nums == num_list:
            return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def block_text_to_children(block_text: str) -> list[InlineNode]:
    return inline_md_to_markdown_node(block_text)


def paragraph_to_markdown_node(block_text: str) -> BlockNode:
    paragraph_text = block_text.replace("\n", " ")
    children = block_text_to_children(paragraph_text)
    return Paragraph(children)


def heading_block_to_html_node(block_text: str) -> BlockNode:
    match = re.match(r"^(#{1,6})(?:[ \t]+|$)(.*)$", block_text, re.DOTALL)
    if not match:
        raise MarkdownSyntaxError("heading text is malformed")

    level = len(match.group(1))
    heading_text = match.group(2)
    return Heading(level, block_text_to_children(heading_text))


def code_block_to_markdown_node(block_text: str) -> CodeBlock:
    for delimiter in ("```", "~~~"):
        if not block_text.startswith(delimiter):
            continue

        first_line, separator, _ = block_text.partition("\n")
        if not separator:
            raise MarkdownSyntaxError(f"no closing '{delimiter}' for code block")

        if first_line != delimiter:
            raise NotImplementedError("Code styles not implemented at this time")

        closing_fence = f"\n{delimiter}"
        if not block_text.endswith(closing_fence):
            raise MarkdownSyntaxError(f"no closing '{delimiter}' for code block")

        content_start = len(delimiter) + 1
        content_end = -len(delimiter)
        content = block_text[content_start:content_end]
        return CodeBlock([Text(content)])

    raise ValueError("not a code block")


def block_quote_to_markdown_node(block_text: str) -> BlockNode:
    block_text_copy = "\n".join(line[1:].strip() for line in block_text.splitlines())
    return BlockQuote(markdown_to_markdown_node(block_text_copy))


def ordered_list_to_markdown_node(block_text: str) -> BlockNode:
    lines = block_text.splitlines()
    list_items: list[ListItem] = []
    first_number: int = -1
    for i in range(len(lines)):
        list_elements = lines[i].split(". ", 1)
        if i == 0:
            first_number = int(list_elements[0])
        list_items.append(ListItem(block_text_to_children(list_elements[1])))
        # for now using block_text_to_children() until we add support for
        # loose lists.
    return ListBlock(ListType.ORDERED, list_items, first_number)


def unordered_list_to_markdown_node(block_text: str) -> BlockNode:
    lines = block_text.splitlines()
    list_items: list[ListItem] = []
    for line in lines:
        new_line = line.split("- ", 1)[1]
        list_items.append(ListItem(block_text_to_children(new_line)))
        # for now using block_text_to_children() until we add support for
        # loose lists.
    return ListBlock(ListType.UNORDERED, list_items)


_TABLE_DELIMITER_CELL = re.compile(r"^:?-{3,}:?$")


def _is_escaped(text: str, position: int) -> bool:
    backslash_count = 0
    position -= 1

    while position >= 0 and text[position] == "\\":
        backslash_count += 1
        position -= 1

    return backslash_count % 2 == 1


def split_table_row(line: str) -> list[str]:
    """Split one table row without splitting pipes inside code spans.

    Leading and trailing pipes are optional. A backslash-escaped pipe is
    treated as cell content and the escaping backslash is removed.
    """
    row = line.strip()

    if not row:
        raise MarkdownSyntaxError("table rows cannot be blank")

    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|") and not _is_escaped(row, len(row) - 1):
        row = row[:-1]

    cells: list[str] = []
    current: list[str] = []
    in_code = False
    position = 0

    while position < len(row):
        character = row[position]

        if character == "`":
            in_code = not in_code
            current.append(character)
            position += 1
            continue

        if character == "|" and not in_code:
            if _is_escaped(row, position):
                current.pop()  # remove the escaping backslash
                current.append("|")
                position += 1
                continue

            cells.append("".join(current).strip())
            current.clear()
            position += 1
            continue

        current.append(character)
        position += 1

    cells.append("".join(current).strip())
    return cells


def parse_table_alignment(cell: str) -> TableAlignment:
    delimiter = cell.strip()

    if not _TABLE_DELIMITER_CELL.fullmatch(delimiter):
        raise MarkdownSyntaxError(
            f"invalid table delimiter cell {cell!r}; expected at least three hyphens "
            "with optional leading/trailing colons"
        )

    if delimiter.startswith(":") and delimiter.endswith(":"):
        return TableAlignment.CENTER
    if delimiter.startswith(":"):
        return TableAlignment.LEFT
    if delimiter.endswith(":"):
        return TableAlignment.RIGHT
    return TableAlignment.DEFAULT


def table_cells_to_markdown_node(cells: list[str]) -> TableRow:
    return TableRow(
        [TableCell(block_text_to_children(cell_text)) for cell_text in cells]
    )


def table_row_to_markdown_node(line: str) -> TableRow:
    return table_cells_to_markdown_node(split_table_row(line))


def is_table_block(block_text: str) -> bool:
    """Return True only when the second line is a valid delimiter row."""
    lines = block_text.splitlines()

    if len(lines) < 2 or "|" not in lines[0] or "|" not in lines[1]:
        return False

    try:
        header_cells = split_table_row(lines[0])
        delimiter_cells = split_table_row(lines[1])
    except MarkdownSyntaxError:
        return False

    return (
        len(header_cells) == len(delimiter_cells)
        and len(header_cells) > 0
        and all(
            _TABLE_DELIMITER_CELL.fullmatch(cell.strip()) for cell in delimiter_cells
        )
    )


def table_block_to_markdown_node(block_text: str) -> Table:
    lines = block_text.splitlines()

    if len(lines) < 2:
        raise MarkdownSyntaxError("a table requires a header row and a delimiter row")

    header_cells = split_table_row(lines[0])
    delimiter_cells = split_table_row(lines[1])
    column_count = len(header_cells)

    if len(delimiter_cells) != column_count:
        raise MarkdownSyntaxError(
            "table header and delimiter row must contain the same number of cells"
        )

    alignments = [parse_table_alignment(cell) for cell in delimiter_cells]
    header = table_cells_to_markdown_node(header_cells)
    rows: list[TableRow] = []

    for line_number, line in enumerate(lines[2:], start=3):
        row_cells = split_table_row(line)

        if len(row_cells) != column_count:
            raise MarkdownSyntaxError(
                f"table row {line_number} has {len(row_cells)} cells; "
                f"expected {column_count}"
            )

        rows.append(table_cells_to_markdown_node(row_cells))

    return Table(header=header, rows=rows, alignments=alignments)
