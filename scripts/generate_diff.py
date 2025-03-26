import os
import json
import git
import difflib
from markdownify import markdownify

TRANSLATED_DIR = "translated-content/files/zh-tw"
CONTENT_DIR = "content/files/en-us"
OUTPUT_DIR = "output"
DIFF_DIR = os.path.join(OUTPUT_DIR, "diff")


def read_source_commit(file_path):
    """ 讀取 sourceCommit """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if "sourceCommit:" in line:
                    return line.strip().split("sourceCommit:")[-1].strip()
    except Exception:
        pass
    return None


def generate_diff(old_text, new_text):
    """ 產生 HTML 差異比對 """
    diff = difflib.HtmlDiff().make_file(old_text.splitlines(), new_text.splitlines())
    return diff


def main():
    os.makedirs(DIFF_DIR, exist_ok=True)

    repo = git.Repo("content")
    outdated_files = []

    for root, _, files in os.walk(TRANSLATED_DIR):
        for file in files:
            trans_file_path = os.path.join(root, file)
            rel_path = os.path.relpath(trans_file_path, TRANSLATED_DIR)
            src_file_path = os.path.join(CONTENT_DIR, rel_path)

            # 讀取 sourceCommit
            source_commit = read_source_commit(trans_file_path)
            if not source_commit:
                continue  # 跳過無 sourceCommit 的文件

            # 取得該檔案最新版本
            latest_content = repo.git.show(f"HEAD:{os.path.relpath(src_file_path, 'content')}")

            # 取得 sourceCommit 版本
            try:
                old_content = repo.git.show(f"{source_commit}:{os.path.relpath(src_file_path, 'content')}")
            except git.exc.GitCommandError:
                continue  # 若找不到舊版本，跳過

            # 檢查是否有變化
            if old_content != latest_content:
                diff_html = generate_diff(old_content, latest_content)
                diff_path = os.path.join(DIFF_DIR, f"{rel_path}.html")

                os.makedirs(os.path.dirname(diff_path), exist_ok=True)
                with open(diff_path, "w", encoding="utf-8") as f:
                    f.write(diff_html)

                outdated_files.append({"path": rel_path, "diff_url": f"diff/{rel_path}.html"})

    # 生成 index.html
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write("<html><body><h1>Outdated MDN Translations</h1><ul>")
        for item in outdated_files:
            f.write(f'<li><a href="{item["diff_url"]}">{item["path"]}</a></li>')
        f.write("</ul></body></html>")


if __name__ == "__main__":
    main()