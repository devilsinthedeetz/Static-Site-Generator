from __future__ import annotations


class HTMLNode:
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: list[HTMLNode] | None = None,
        props: dict[str, str] | None = None,
    ) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
        self.voidTags = [
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        ]

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
        if self.children:
            return f"HTMLNode(tag={self.tag}, value={self.value}, props={self.props}, children: {self.children})"
        else:
            return f"HTMLNode(tag={self.tag}, value={self.value}, props={self.props}, children: None)"

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, HTMLNode):
            return False
        return (
            self.tag == other.tag
            and self.value == other.value
            and self.props == other.props
            and self.children == other.children
        )


class LeafNode(HTMLNode):
    def __init__(
        self, tag: str | None, value: str, props: dict[str, str] | None = None
    ) -> None:
        super().__init__(tag, value, None, props)

    def to_html(self) -> str:
        if self.value is None:
            raise ValueError("LeafNode must have a value")
        if not self.tag:
            return self.value
        if self.tag in self.voidTags:
            return f"<{self.tag}{self.props_to_html()}>{self.value}"
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self) -> str:
        return f"LeafNode(tag={self.tag}, value={self.value}, props={self.props})"


class ParentNode(HTMLNode):
    def __init__(
        self, tag: str, children: list[HTMLNode], props: dict[str, str] | None = None
    ) -> None:
        super().__init__(tag, None, children, props)

    def to_html(self) -> str:
        if not self.tag:
            raise ValueError("ParentNode must have a tag")
        if not self.children:
            raise ValueError("ParentNode must have children")
        if self.tag in self.voidTags:
            return f"<{self.tag}{self.props_to_html()}>{''.join(map(lambda node: node.to_html(), self.children))}"
        return f"<{self.tag}{self.props_to_html()}>{''.join(map(lambda node: node.to_html(), self.children))}</{self.tag}>"
