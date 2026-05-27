import os

# 设置 Hugo 博客的 content 目录路径
content_dir = "."

# 忽略的目录（可选）
ignore_dirs = ["drafts"]  # 如果需要忽略某些目录，可以在这里添加

# 遍历 content 目录中的所有 Markdown 文件
for root, dirs, files in os.walk(content_dir):
    # 跳过忽略的目录
    dirs[:] = [d for d in dirs if d not in ignore_dirs]

    for file in files:
        if file.endswith(".md"):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # 检查是否包含 draft: true
                if "draft: true" in content:
                    print(f"Deleting draft file: {file_path}")
                    os.remove(file_path)  # 删除文件

