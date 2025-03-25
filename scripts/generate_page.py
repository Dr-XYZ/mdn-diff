import json
import os

DATA_FILE = "data/outdated_diff.json"
OUTPUT_DIR = "public"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 讀取過時檔案資訊
with open(DATA_FILE, "r", encoding="utf-8") as f:
    outdated_files = json.load(f)

index_content = "<h1>Outdated Translations</h1><ul>"

for item in outdated_files:
    file_path = item["file"]
    diff_file = os.path.join(OUTPUT_DIR, file_path.replace("/", "_") + ".html")

    # 生成 Diff 頁面
    with open(diff_file, "w", encoding="utf-8") as f:
        f.write(f"<h1>Diff for {file_path}</h1><pre>{item['diff']}</pre>")

    index_content += f'<li><a href="{os.path.basename(diff_file)}">{file_path}</a></li>'

index_content += "</ul>"

# 生成索引頁面
with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_content)