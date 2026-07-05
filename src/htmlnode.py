class HTMLNode:
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        props: dict[str, str] | None = None,
        children: list[HTMLNode] | None = None,
    ) -> None:
        self.tag = tag
        self.value = value
        self.props = props
        self.children = children

    def to_html(self):
        raise NotImplementedError("to_html override required to render html")

    def props_to_html(self) -> str:
        prop_str: str = ""
        if self.props:
            for prop, prop_value in self.props.items():
                prop_str += f' {prop}="{prop_value}"'
        else:
            pass
        return prop_str

    def __repr__(self) -> str:
        child_str = ""
        if self.children:
            for child_node in self.children:
                if not child_node.tag:
                    child_str += "raw,"
                else:
                    child_str += f"{child_node.tag},"
            return f"HTMLNode(tag={self.tag}, value={self.value}, props={self.props}, children={len(self.children if self.children else '')}(child tags=[{child_str}]))"
        else:
            return f"HTMLNode(tag={self.tag}, value={self.value}, props={self.props}, children=None)"


class LeafNode(HTMLNode):
    def __init__(
        self, tag: str | None, value: str, props: dict[str, str] | None = None
    ) -> None:
        super().__init__(tag, value, props)
        self.children = None

    def to_html(self):
        if self.value is None:
            raise ValueError("LeafNode must have a value")
        if not self.tag:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self) -> str:
        return f"LeafNode(tag={self.tag}, value={self.value}, props={self.props})"
