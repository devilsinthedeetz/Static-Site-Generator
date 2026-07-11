from enum import Enum
import re
from htmlnode import HTMLNode, ParentNode, LeafNode
from textnode import TextNode, TextType, text_node_to_html_node
from inline_md_to_text_node import text_to_text_node


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_html_node(md) -> ParentNode:
    split_text_blocks: list[str] = markdown_to_blocks(md)
    nodes: list[HTMLNode] = []
    for block_text in split_text_blocks:
        block_type: BlockType = block_to_block_type(block_text)
        html_node: HTMLNode = block_node_to_html_node(block_type, block_text)
        nodes.append(html_node)
    return ParentNode("div", nodes)


def markdown_to_blocks(md) -> list[str]:
    blocks: list[str] = md.split("\n\n")
    new_blocks = []
    for block in blocks:
        strip_block = block.strip()
        if strip_block == "":
            pass
        else:
            new_blocks.append(strip_block)
    return new_blocks


def block_to_block_type(block: str) -> BlockType:
    if block.startswith(("#", "##", "###", "####", "#####", "######")):
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
    num_list: list[int] = []
    has_num_list = True
    for line in new_lines:
        if re.match(r"^\d+\.", line):
            num = re.search(r"^\d+", line)
            if num:
                num_list.append(int(num.group()))
            else:
                has_num_list = False
        else:
            has_num_list = False
    if has_num_list:
        if num_list[0] == 1:
            copy_nums = num_list.copy()
            sorted_nums = sorted(copy_nums)
            if sorted_nums == num_list:
                return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def block_node_to_html_node(block_type: BlockType, block_text: str) -> HTMLNode:
    if block_type == BlockType.HEADING:
        return heading_block_to_html_node(block_text)
    if block_type == BlockType.CODE:
        return code_block_to_html_node(block_text)
    if block_type == BlockType.QUOTE:
        return block_quote_to_html_node(block_text)
    if block_type == BlockType.UNORDERED_LIST:
        return unordered_list_to_html_node(block_text)
    if block_type == BlockType.ORDERED_LIST:
        return ordered_list_to_html_node(block_text)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block_text)


def text_to_children(block_text: str) -> list[HTMLNode]:
    text_nodes: list[TextNode] = text_to_text_node(block_text)
    leaf_nodes: list[HTMLNode] = []
    for text_node in text_nodes:
        leaf_nodes.append(text_node_to_html_node(text_node))
    return leaf_nodes


def paragraph_to_html_node(block_text: str) -> ParentNode:
    paragraph_text = block_text.replace("\n", " ")
    leaf_nodes = text_to_children(paragraph_text)
    return ParentNode("p", leaf_nodes)


def block_quote_to_html_node(block_text: str) -> ParentNode:
    return ParentNode(
        "blockquote",
        text_to_children("\n".join(line[1:] for line in block_text.splitlines())),
    )


def unordered_list_to_html_node(block_text: str) -> ParentNode:
    lines = block_text.splitlines()
    parent_nodes: list[HTMLNode] = []
    for line in lines:
        new_line = line.split("- ", 1)[1]
        parent_nodes.append(ParentNode("li", text_to_children(new_line)))
    return ParentNode("ul", parent_nodes)


def ordered_list_to_html_node(block_text: str) -> ParentNode:
    lines = block_text.splitlines()
    parent_nodes: list[HTMLNode] = []
    for line in lines:
        new_line = line.split(". ", 1)[1]
        parent_nodes.append(ParentNode("li", text_to_children(new_line)))
    return ParentNode("ol", parent_nodes)


def heading_block_to_html_node(block_text: str) -> ParentNode:
    hashes = re.search(r"^#{1,6}", block_text)
    if hashes:
        num_hashes: int = len(hashes.group())
    else:
        raise Exception("header text is malformed")
    return ParentNode(f"h{num_hashes}", text_to_children(block_text.lstrip("# ")))


def code_block_to_html_node(block_text: str) -> HTMLNode:
    lines_to_keep = ""
    if block_text.startswith("```\n") and block_text.endswith("\n```"):
        lines_to_keep = block_text.lstrip("```\n")
        lines_to_keep = lines_to_keep.rstrip("```")
    elif block_text.startswith("~~~\n") and block_text.endswith("\n~~~"):
        lines_to_keep = block_text.lstrip("~~~\n")
        lines_to_keep = lines_to_keep.rstrip("~~~")
    else:
        raise ValueError("not a code block")
    code_text_node = TextNode(lines_to_keep, TextType.CODE)
    return ParentNode("pre", [text_node_to_html_node(code_text_node)])
