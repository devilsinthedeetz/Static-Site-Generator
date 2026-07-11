import os
import shutil
import sys
from blocknode import markdown_to_html_node


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
    template: str = ""
    with open(from_path, "r") as file:
        md = file.read()
    with open(template_path, "r") as file:
        template = file.read()
    html: str = markdown_to_html_node(md).to_html()
    title: str = extract_title(md)
    # replace stuff
    final_file: str = template.replace("{{ Title }}", title)
    final_file = final_file.replace("{{ Content }}", html)
    final_file = final_file.replace('href="/', f'href="{base_path}')
    final_file = final_file.replace('src="/', f"src={base_path}")
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
    base_path = "/"
    try:
        base_path = sys.argv[1]
    except IndexError:
        print("sys.argv[1] out of range")
        print("using base_path '/'")
    copy_static_to_public("static", "docs", False)
    generate_pages_recursive("content", "template.html", "docs", base_path)


main()
