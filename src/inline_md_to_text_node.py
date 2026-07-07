import re
from textnode import TextNode, TextType


def text_to_text_node(text: str) -> list[TextNode]:
    node: TextNode = TextNode(text, TextType.TEXT)
    nodes: list[TextNode] = [node]
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    return nodes


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    if not isinstance(old_nodes, list):
        raise TypeError("old_nodes must be list of TextNodes")
    if delimiter not in ["`", "**", "_"]:
        raise NotImplementedError(
            f"{delimiter} currently unsupported. supported delimiters: '`', '**', '_'"
        )
    new_nodes: list[TextNode] = []
    copied_nodes: list[TextNode] = old_nodes.copy()
    if not (
        (delimiter == "`" and text_type == TextType.CODE)
        or (delimiter == "**" and text_type == TextType.BOLD)
        or (delimiter == "_" and text_type == TextType.ITALIC)
    ):
        raise ValueError(
            "delimiter and TextType must match (** for BOLD, ` for CODE, etc.)"
        )
    for node in copied_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
        elif delimiter == "`":
            new_nodes.extend(split_nodes_delimiter_helper(node, delimiter, text_type))
        elif delimiter == "**":
            new_nodes.extend(split_nodes_delimiter_helper(node, delimiter, text_type))
        elif delimiter == "_":
            new_nodes.extend(split_nodes_delimiter_helper(node, delimiter, text_type))
    return new_nodes


def split_nodes_delimiter_helper(
    node: TextNode, delimiter: str, text_type: TextType
) -> list[TextNode]:
    if delimiter not in node.text:
        return [node]
    split_nodes = []
    sections = node.text.split(delimiter)
    if len(sections) % 2 == 0:
        raise Exception(f"invalid .md syntax, need closing '{delimiter}' delimiter")
    for i in range(len(sections)):
        if sections[i] == "":
            continue
        if i % 2 == 0:
            split_nodes.append(TextNode(sections[i], TextType.TEXT))
        else:
            split_nodes.append(TextNode(sections[i], text_type))
    return split_nodes


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    if not isinstance(old_nodes, list):
        raise TypeError("parameter must be a list of TextNodes")
    copy_nodes = old_nodes.copy()
    new_nodes: list[TextNode] = []
    for node in copy_nodes:
        extracted_images = extract_markdown_images(node.text)
        node_first_split = False
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        elif not extracted_images:
            new_nodes.append(node)
        else:
            split_nodes = []
            for extracted_image in extracted_images:
                image_inserted = False
                image_alt, image_url = extracted_image
                delimiter = f"![{image_alt}]({image_url})"
                if not node_first_split:
                    sections = node.text.split(delimiter, 1)
                    node_first_split = True
                    split_nodes.extend(
                        [
                            TextNode(sections[0], TextType.TEXT),
                            TextNode(image_alt, TextType.IMAGE, image_url),
                            TextNode(sections[1], TextType.TEXT),
                        ]
                    )
                    image_inserted = True
                if node_first_split and not image_inserted:
                    working_node = split_nodes[-1]
                    del split_nodes[-1]
                    sections = working_node.text.split(delimiter, 1)
                    split_nodes.extend(
                        [
                            TextNode(sections[0], TextType.TEXT),
                            TextNode(image_alt, TextType.IMAGE, image_url),
                            TextNode(sections[1], TextType.TEXT),
                        ]
                    )
                    image_inserted = True
                if image_inserted:
                    continue
            new_nodes.extend(remove_empty_text_nodes(split_nodes))
    return new_nodes


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    if not isinstance(old_nodes, list):
        raise TypeError("parameter must be a list of TextNodes")
    copy_nodes = old_nodes.copy()
    new_nodes: list[TextNode] = []
    for node in copy_nodes:
        extracted_links = extract_markdown_links(node.text)
        node_first_split = False
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        elif not extracted_links:
            new_nodes.append(node)
        else:
            split_nodes = []
            for extracted_link in extracted_links:
                link_inserted = False
                link_text, link_url = extracted_link
                deliminator = f"[{link_text}]({link_url})"
                if not node_first_split:
                    sections = node.text.split(deliminator, 1)
                    node_first_split = True
                    split_nodes.extend(
                        [
                            TextNode(sections[0], TextType.TEXT),
                            TextNode(link_text, TextType.LINK, link_url),
                            TextNode(sections[1], TextType.TEXT),
                        ]
                    )
                    link_inserted = True
                if node_first_split and not link_inserted:
                    working_node = split_nodes[-1]
                    del split_nodes[-1]
                    sections = working_node.text.split(deliminator, 1)
                    split_nodes.extend(
                        [
                            TextNode(sections[0], TextType.TEXT),
                            TextNode(link_text, TextType.LINK, link_url),
                            TextNode(sections[1], TextType.TEXT),
                        ]
                    )
                    link_inserted = True
                if link_inserted:
                    continue
            new_nodes.extend(remove_empty_text_nodes(split_nodes))
    return new_nodes


def remove_empty_text_nodes(old_nodes: list[TextNode]) -> list[TextNode]:
    copy_nodes = old_nodes.copy()
    return list(filter(lambda node: node.text != "", copy_nodes))


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
