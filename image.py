import os
import re
import shutil

# 定义 src 和 output 目录
src_dir = "../blog-stack/static"  # 图片的源目录
output_dir = "./static"  # 图片的目标目录

# 定义 Hugo 博客的 content 目录路径
content_dir = "content"

# 正则表达式匹配图片引用
image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

# 保存所有图片引用
image_references = {}

# 遍历 content 目录中的所有 Markdown 文件
for root, dirs, files in os.walk(content_dir):
    for file in files:
        if file.endswith(".md"):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # 查找所有图片引用
                images = image_pattern.findall(content)
                if images:
                    image_references[file_path] = images

# 处理图片引用
for file_path, images in image_references.items():
    print(f"File: {file_path}")
    for image in images:
        print(f"  Image: {image}")

        # 构建完整的图片源路径
        src_image_path = os.path.join(src_dir, image.lstrip("/"))
        if not os.path.exists(src_image_path):
            print(f"  Warning: Image not found - {src_image_path}")
            continue

        # 构建完整的图片目标路径
        output_image_path = os.path.join(output_dir, image.lstrip("/"))
        os.makedirs(os.path.dirname(output_image_path), exist_ok=True)

        # 复制图片到目标路径
        shutil.copy(src_image_path, output_image_path)
        print(f"  Copied to: {output_image_path}")

# 统计图片数量
total_images = sum(len(images) for images in image_references.values())
print(f"Total images found: {total_images}")
