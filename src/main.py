from datetime import datetime
import os
import shutil
import sys
import frontmatter
from frontmatter import Post
from dotenv import load_dotenv

from htmlnode import LeafNode
from markdown_node import BlockNode
from markdown_node_to_html_node import markdown_nodes_to_html_node
from block_md_to_markdown_node import markdown_to_markdown_node
from article import Article, ArticleMetadata, ArticleType, Author, get_article_type

load_dotenv()


def extract_metadata(metadata: Post) -> ArticleMetadata:
    title: str = ""
    description: str = ""
    article_type: ArticleType = ArticleType.INDEX
    published_at: datetime | None = None
    authors: list[Author] = []
    updated_at: datetime | None = None
    slug: str | None = None
    article_id: str | None = None
    tags: list[str] = []
    draft: bool = False
    language: str | None = os.getenv("LANGUAGE")
    image: str | None = ""
    if metadata is not None:
        if "title" in metadata.keys():
            title = metadata["title"]
        else:
            raise ValueError("front matter requires title")
        if "description" in metadata.keys():
            description = metadata["description"]
        else:
            raise ValueError("front matter requires description")
        if "type" in metadata.keys():
            if metadata["type"] in ArticleType:
                article_type = get_article_type(metadata["type"])
        if "published_at" in metadata.keys():
            published_at = datetime.fromisoformat(metadata["published_at"])
        else:
            raise ValueError("markdown frontmatter requires publushed_at")
        if "authors" in metadata.keys():
            for author in metadata["authors"]:
                if author["name"]:
                    if author["email"]:
                        authors.append(Author(author["name"], author["email"]))
                    else:
                        authors.append(Author(author["name"]))
        if "updated_at" in metadata.keys():
            updated_at = datetime.fromisoformat(metadata["updated_at"])
        if "slug" in metadata.keys():
            slug = metadata["slug"]
        if "article_id" in metadata.keys():
            article_id = metadata["article_id"]
        if "tags" in metadata.keys():
            tags = metadata["tags"]
        if "draft" in metadata.keys():
            if metadata["draft"] == "true":
                draft = True
            else:
                draft = False
        if "image" in metadata.keys():
            print(f"{metadata['image']}")
            image = metadata["image"]
    return ArticleMetadata(
        title,
        description,
        article_type,
        published_at,
        authors,
        updated_at,
        slug,
        article_id,
        tags,
        draft,
        language,
        image,
    )


def extract_title(md) -> str:
    lines = md.splitlines()
    if lines[0].startswith("#"):
        title = lines[0].lstrip("# ")
        title = title.strip()
        return title
    else:
        raise Exception("markdown file must start with heading")


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, base_path):
    content_dir_list: list[str] = os.listdir(dir_path_content)
    if not content_dir_list:
        return
    for path in content_dir_list:
        html_path = path.replace(".md", ".html")
        if os.path.exists(os.path.join(dest_dir_path, html_path)):
            continue
        elif os.path.isfile(os.path.join(dir_path_content, path)) and path.endswith(
            ".md"
        ):
            if not os.path.isdir(dest_dir_path):
                os.mkdir(dest_dir_path)
            generate_page(
                os.path.join(dir_path_content, path),
                template_path,
                os.path.join(dest_dir_path, html_path),
                base_path,
            )
        elif os.path.isdir(os.path.join(dir_path_content, path)):
            if not os.path.exists(dest_dir_path):
                os.mkdir(dest_dir_path)
            if not os.path.exists(os.path.join(dest_dir_path, path)):
                os.mkdir(os.path.join(dest_dir_path, path))
            generate_pages_recursive(
                os.path.join(dir_path_content, path),
                template_path,
                os.path.join(dest_dir_path, path),
                base_path,
            )


def generate_page(from_path, template_path, dest_path, base_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    md: str = ""
    metadata: object | None = None
    template: str = ""
    with open(from_path, "r") as file:
        metadata, md = frontmatter.parse(file.read())
    article: Article = Article(extract_metadata(metadata), md)
    if article.metadata.type == ArticleType.INDEX:
        with open("index_template.html", "r") as file:
            template = file.read()
    elif article.metadata.type == ArticleType.CONTACT:
        with open("contact_template.html", "r") as file:
            template = file.read()
    elif article.metadata.type == ArticleType.BLOG_POST:
        with open("blog_template.html", "r") as file:
            template = file.read()
    else:
        with open(template_path, "r") as file:
            template = file.read()
    nodes: list[BlockNode] = markdown_to_markdown_node(md)
    html: str = markdown_nodes_to_html_node(nodes).to_html()
    title: str = extract_title(md)
    desc = article.metadata.description
    image = ""
    if article.metadata.image:
        image = LeafNode("img", "", {"src": article.metadata.image}).to_html()
    author = article.metadata.authors[0].name
    # replace stuff
    final_file: str = template.replace("{{ Title }}", title)
    final_file = final_file.replace("{{ Content }}", html)
    final_file = final_file.replace("{{ description }}", desc)
    final_file = final_file.replace("{{ image }}", image)
    final_file = final_file.replace("{{ Author }}", author)
    final_file = final_file.replace('href="/', f'href="{base_path}')
    final_file = final_file.replace('src="/', f'src="{base_path}')
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as file:
        file.write(final_file)


def copy_static_to_public(source_path: str, dest_path: str, deleted: bool):
    if not deleted:
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
            deleted = True
            os.mkdir(dest_path)
        else:
            deleted = True
            os.mkdir(dest_path)
    source_dir: list[str] = os.listdir(source_path)
    if not source_dir:
        return
    for path in source_dir:
        if os.path.exists(os.path.join(dest_path, path)):
            continue
        else:
            if os.path.isfile(os.path.join(source_path, path)):
                if not os.path.isdir(dest_path):
                    os.mkdir(dest_path)
                print(
                    shutil.copy(
                        os.path.join(source_path, path), os.path.join(dest_path, path)
                    )
                )
            else:
                if os.path.isdir(os.path.join(source_path, path)):
                    if not os.path.exists(dest_path):
                        os.mkdir(dest_path)
                    if not os.path.exists(os.path.join(dest_path, path)):
                        os.mkdir(os.path.join(dest_path, path))
                    copy_static_to_public(
                        os.path.join(source_path, path),
                        os.path.join(dest_path, path),
                        deleted,
                    )


def main():
    base_path = "/"
    try:
        base_path = sys.argv[1]
    except IndexError:
        print("sys.argv[1] out of range")
        print("using base_path '/'")
    copy_static_to_public("static", "docs", False)
    generate_pages_recursive("content", "template.html", "docs", base_path)


main()
