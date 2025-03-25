import os
import json
import re
import git

TRANSLATED_PATH = "translated-content/files/zh-tw"
CONTENT_PATH = "content/files/en-us"
OUTPUT_FILE = "outdated_diff.json"

repo_content = git.Repo(CONTENT_PATH)

outdated_files = []

for root, _, files in os.walk(TRANSLATED_PATH):
    for file in files:
        translated_file_path = os.path.join(root, file)

        # 讀取翻譯文件
        with open(translated_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 檢查 sourceCommit
        match = re.search(r"sourceCommit:\s*([a-f0-9]{40})", content)
        if not match:
            continue  # 沒有 sourceCommit，跳過

        source_commit = match.group(1)

        # 找到對應的英文原文檔案
        relative_path = os.path.relpath(translated_file_path, TRANSLATED_PATH)
        original_file_path = os.path.join(CONTENT_PATH, relative_path)

        if not os.path.exists(original_file_path):
            continue  # 原文已刪除

        # 取得 diff
        latest_commit = repo_content.head.object.hexsha
        diff = repo_content.git.diff(source_commit, latest_commit, "--", original_file_path)

        if diff:
            outdated_files.append({
                "file": relative_path,
                "diff": diff
            })

# 儲存結果
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(outdated_files, f, indent=2, ensure_ascii=False)