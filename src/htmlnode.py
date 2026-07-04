class HTMLNode:
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: list[object] | None = None,
        props: dict[str, str] | None = None,
    ) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError("to_html override required to render html")

    def props_to_html(self) -> str:
        prop_str: str = ""
        if self.props:
            for prop, value in self.props.items():
                prop_str += f' {prop}="{value}"'
        else:
            pass
        return prop_str

    def __repr__(self) -> str:
        return f"""HTMLNode
Tag: {self.tag}
Value: {self.value}
Props: {self.props}
Children: {self.children}
"""
