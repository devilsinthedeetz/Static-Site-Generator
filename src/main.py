import os
from os.path import isfile
import shutil


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


main()
