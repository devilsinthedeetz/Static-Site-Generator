from textnode import TextNode, TextType


def main():
    my_node = TextNode(
        "This is some anchor text", TextType.LINK, "https://www.boot.dev"
    )
    print(my_node)


main()
