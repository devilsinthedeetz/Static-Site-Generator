from textnode import TextNode, TextType


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    if not isinstance(old_nodes, list):
        raise TypeError("old_nodes must be list of nodes")
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
    first_splits = node.text.split(delimiter, 1)
    if delimiter not in first_splits[-1]:
        raise Exception(f"invalid .md syntax, need closing '{delimiter}' delimiter")
    else:
        second_splits = first_splits[-1].split(delimiter, 1)
        return [
            TextNode(first_splits[0], TextType.TEXT),
            TextNode(second_splits[0], text_type),
            TextNode(second_splits[1], TextType.TEXT),
        ]
