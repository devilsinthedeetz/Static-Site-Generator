from __future__ import annotations
from markdown_node import (
    InlineNode,
    Bold,
    Italic,
    Text,
    Code,
    Link,
    Image,
)


class MarkdownSyntaxError(ValueError):
    pass


def inline_md_to_markdown_node(text: str) -> list[InlineNode]:
    nodes, position = parse_inline(text)

    if position != len(text):
        raise MarkdownSyntaxError("inline parser stopped unexpectedly")

    return nodes


def parse_inline(
    text: str,
    position: int = 0,
    closing_delimiter: str | None = None,
    allow_links: bool = True,
) -> tuple[list[InlineNode], int]:
    nodes: list[InlineNode] = []
    plain_text: list[str] = []

    def flush_plain_text() -> None:
        if plain_text:
            nodes.append(Text("".join(plain_text)))
            plain_text.clear()

    while position < len(text):
        if closing_delimiter and text.startswith(closing_delimiter, position):
            flush_plain_text()
            return nodes, position + len(closing_delimiter)

        if text[position] == "`":
            flush_plain_text()
            closing_position = text.find("`", position + 1)
            if closing_position == -1:
                raise MarkdownSyntaxError("unclosed '`' delimiter")
            code = text[position + 1 : closing_position]
            nodes.append(Code(code))
            position = closing_position + 1
            continue

        if text.startswith("![", position):
            flush_plain_text()
            image, position = parse_image(text, position)
            nodes.append(image)
            continue

        if text[position] == "[" and allow_links:
            flush_plain_text()
            link, position = parse_link(text, position)
            nodes.append(link)
            continue

        if text.startswith("**", position):
            flush_plain_text()
            children, position = parse_inline(
                text, position + 2, closing_delimiter="**"
            )
            nodes.append(Bold(children))
            continue

        if text[position] == "_":
            flush_plain_text()
            children, position = parse_inline(text, position + 1, closing_delimiter="_")
            nodes.append(Italic(children))
            continue

        plain_text.append(text[position])
        position += 1

    if closing_delimiter is not None:
        raise MarkdownSyntaxError(f"unclosed '{closing_delimiter}' delimiter")

    flush_plain_text()
    return nodes, position


def parse_link(text: str, position: int) -> tuple[Link, int]:
    """
    Parse:

        [label](url)

    beginning at position.
    """
    if not text.startswith("[", position):
        raise MarkdownSyntaxError("link must start with '['")

    label_end = find_closing_bracket(text, position + 1)

    if label_end == -1:
        raise MarkdownSyntaxError("unclosed link label")

    url_open = label_end + 1

    if url_open >= len(text) or text[url_open] != "(":
        raise MarkdownSyntaxError("link label must be followed by '(url)'")

    url_end = find_closing_parenthesis(text, url_open + 1)

    if url_end == -1:
        raise MarkdownSyntaxError("unclosed link URL")

    label_text = text[position + 1 : label_end]
    url = text[url_open + 1 : url_end]

    if not url:
        raise MarkdownSyntaxError("link URL cannot be empty")

    children, child_position = parse_inline(label_text, allow_links=False)

    if child_position != len(label_text):
        raise MarkdownSyntaxError("could not parse link label")

    return Link(url=url, children=children), url_end + 1


def parse_image(text: str, position: int) -> tuple[Image, int]:
    """
    Parse:

        ![alt text](url)

    beginning at position.
    """
    if not text.startswith("![", position):
        raise MarkdownSyntaxError("image must start with '!['")

    alt_start = position + 2
    alt_end = find_closing_bracket(text, alt_start)

    if alt_end == -1:
        raise MarkdownSyntaxError("unclosed image alt text")

    url_open = alt_end + 1

    if url_open >= len(text) or text[url_open] != "(":
        raise MarkdownSyntaxError("image alt text must be followed by '(url)'")

    url_end = find_closing_parenthesis(text, url_open + 1)

    if url_end == -1:
        raise MarkdownSyntaxError("unclosed image URL")

    alt = text[alt_start:alt_end]
    url = text[url_open + 1 : url_end]

    if not url:
        raise MarkdownSyntaxError("image URL cannot be empty")

    return Image(url=url, alt=alt), url_end + 1


def find_closing_bracket(text: str, position: int) -> int:
    """
    Find the closing ']' while allowing nested square brackets.
    """
    depth = 0

    while position < len(text):
        character = text[position]

        if character == "[":
            depth += 1
        elif character == "]":
            if depth == 0:
                return position
            depth -= 1

        position += 1

    return -1


def find_closing_parenthesis(text: str, position: int) -> int:
    """
    Find the closing ')' while allowing parentheses inside the URL.
    """
    depth = 0

    while position < len(text):
        character = text[position]

        if character == "(":
            depth += 1
        elif character == ")":
            if depth == 0:
                return position
            depth -= 1

        position += 1

    return -1
