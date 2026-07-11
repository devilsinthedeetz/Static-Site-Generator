import os
import shutil
from blocknode import markdown_to_html_node
from pathlib import Path


def extract_title(md) -> str:
    lines = md.splitlines()
    if lines[0].startswith("#"):
        title = lines[0].lstrip("# ")
        title = title.strip()
        return title
    else:
        raise Exception("markdown file must start with heading")


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    md: str = ""
    template: str = ""
    with open(from_path, "r") as file:
        md = file.read()
    with open(template_path, "r") as file:
        template = file.read()
    html: str = markdown_to_html_node(md).to_html()
    title: str = extract_title(md)
    final_file: str = template.replace("{{ Title }}", title)
    final_file = final_file.replace("{{ Content }}", html)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as file:
        file.write(final_file)


def copy_static_to_public(source_path: str, dest_path: str, deleted: bool):
    if not deleted:
        if os.path.exists("public"):
            shutil.rmtree("public")
            deleted = True
            os.mkdir("public")
        else:
            deleted = True
            os.mkdir("public")
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
    copy_static_to_public("static", "public", False)
    generate_page("content/index.md", "template.html", "public/index.html")


main()
