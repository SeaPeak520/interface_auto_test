import shutil
from pathlib import Path


def def_path(path: Path):
    """
    删除给定的路径，可以是文件、空目录或非空目录。
    :param path: 要删除的路径（字符串或 Path 对象）
    :return: None
    """
    try:
        if path.exists():
            if path.is_file():
                # 如果是文件，直接删除
                path.unlink()
            elif path.is_dir():
                # 如果是目录，检查是否为空
                if any(path.iterdir()):
                    # 如果是非空目录，递归删除
                    shutil.rmtree(path)
                else:
                    # 如果是空目录，直接删除
                    path.rmdir()
        else:
            print(f"路径不存在：{path}")
    except Exception as e:
        print(f"删除路径报错{path}: {e}")
