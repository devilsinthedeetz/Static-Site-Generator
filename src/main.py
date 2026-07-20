import os
import shutil
import sys

import frontmatter

from article import Article, ArticleType, extract_metadata, article_type_to_template
from block_md_to_markdown_node import markdown_to_markdown_node
from htmlnode import LeafNode
from markdown_node_to_html_node import markdown_nodes_to_html_node
from constants import BASE_DIR, DEFAULT_TEMPLATE, DOMAIN, BLOG_INDEX_LOCATION
from blog_post_cards import (
    get_visible_articles,
    articles_to_card_list,
    generate_blog_cards,
)


def extract_title(md) -> str:
    lines = md.splitlines()
    if lines[0].startswith("#"):
        title = lines[0].lstrip("# ")
        title = title.strip()
        return title
    else:
        raise Exception("markdown file must start with heading")


def replace_placeholders(template: str, article: Article, base_path) -> str:
    image = (
        LeafNode(
            "img",
            "",
            {"src": article.metadata.image, "alt": article.metadata.description},
        ).to_html()
        if article.metadata.image
        else ""
    )
    html = markdown_nodes_to_html_node(
        markdown_to_markdown_node(article.body)
    ).to_html()

    replacements: dict[str, str] = {
        "{{ Title }}": article.metadata.title,
        "{{ Content }}": html,
        "{{ description }}": article.metadata.description,
        "{{ image }}": image,
        "{{ author }}": article.metadata.authors[0].name,
        'href="/': f'href="{base_path}',
        'src="/': f'src="{base_path}',
    }

    for placeholder, replacement in replacements.items():
        template = template.replace(placeholder, replacement)

    return template


def generate_pages_recursive(
    dir_path_content,
    template_path,
    dest_dir_path,
    base_path,
    articles: list[Article],
):
    if articles is None:
        articles = []
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
            articles = generate_page(
                os.path.join(dir_path_content, path),
                template_path,
                os.path.join(dest_dir_path, html_path),
                base_path,
                articles,
            )
        elif os.path.isdir(os.path.join(dir_path_content, path)):
            if not os.path.exists(dest_dir_path):
                os.mkdir(dest_dir_path)
            if not os.path.exists(os.path.join(dest_dir_path, path)):
                os.mkdir(os.path.join(dest_dir_path, path))
            articles = generate_pages_recursive(
                os.path.join(dir_path_content, path),
                template_path,
                os.path.join(dest_dir_path, path),
                base_path,
                articles,
            )
    return articles


def generate_page(
    from_path,
    template_path,
    dest_path,
    base_path,
    articles: list[Article],
):
    print(f"Generating page from {from_path} to {dest_path}")
    with open(from_path, "r") as file:
        metadata, md = frontmatter.parse(file.read())
    article: Article = Article(extract_metadata(metadata), md)
    articles.append(article)
    if article.metadata.draft:
        print(f"  Page from {from_path} is a draft. Skipping...")
        return
    template_path = article_type_to_template(
        article.metadata.article_type, template_path
    )
    print(f"  using {template_path}")
    with open(template_path, "r") as file:
        template = file.read()
    final_file = replace_placeholders(template, article, base_path)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as file:
        file.write(final_file)
    return articles


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
    base_path = BASE_DIR
    try:
        base_path = sys.argv[1]
    except IndexError:
        print(f"using base_path '{BASE_DIR}'")
    copy_static_to_public("static", "docs", False)
    articles = generate_pages_recursive(
        "content", DEFAULT_TEMPLATE, "docs", base_path, []
    )
    with open(f"docs/{BLOG_INDEX_LOCATION}/index.html", "r") as file:
        template = file.read()
    visible_articles = get_visible_articles(
        articles,
        ignored_type=[
            ArticleType.ABOUT,
            ArticleType.BLOG_INDEX,
            ArticleType.CONTACT,
            ArticleType.INDEX,
        ],
    )
    content = articles_to_card_list(visible_articles, base_path)
    final_file = generate_blog_cards(template, content)
    with open(f"docs/{BLOG_INDEX_LOCATION}/index.html", "w") as file:
        file.write(final_file)


main()
