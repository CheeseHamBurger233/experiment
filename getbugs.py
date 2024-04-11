import jsonlines
import os
import re
import shutil

# 打开 JSONL 文件
with jsonlines.open("pypi-bugs.jsonl") as reader:
    number = 0
    for obj in reader:
        repo_url = obj["repo"]
        commit_hash = obj["hash"]
        diff = obj["diff"]
        old_path = obj["old_path"]
        number += 1

        # 获取 Python 文件名
        file_name = os.path.basename(old_path)

        # 创建临时目录
        temp_dir = "temp_repo"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # 克隆存储库
        repo_path = os.path.join(temp_dir, "repo" + str(number))
        if not os.path.exists(repo_path):
            clone_cmd = f"git clone {repo_url} {repo_path}"
            os.system(clone_cmd)

        # 切换到指定提交
        checkout_cmd = f"cd {repo_path} && git checkout {commit_hash}"
        os.system(checkout_cmd)

        # # 提取指定文件内容并保存
        # target_path = os.path.join("downloaded_files", file_name)

        # target_dir = "temp_repo/repo1/downloaded_files"
        # if not os.path.exists(target_dir):
        #     os.makedirs(target_dir)

        # # 使用 git show 命令来提取指定文件的内容
        # show_cmd = (
        #     f"cd {repo_path} && git show {commit_hash}:{old_path} > {target_path}"
        # )
        # os.system(show_cmd)

        # 解析 diff 获取修改的行和内容
        modified_lines = []
        diff_lines = diff.split("\n")
        change = -1
        new_line = ""
        old_line = ""
        for line in diff_lines:
            change += 1
            if line.startswith("@@"):
                match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@.*", line)
                if match:
                    modified_lines.append(int(match.group(1)))
            elif line.startswith("+"):
                modified_lines.append(change + modified_lines[0] - 1)
                new_line = line
            elif line.startswith("-"):
                modified_lines.append(change + modified_lines[0] - 1)
                old_line = line
        # print(new_line[1:])
        # print(old_line[1:])
        # 读取文件内容
        file_path = os.path.join(repo_path, old_path)
        with open(file_path, "r") as file:
            file_content = file.readlines()

        # 构造注释内容
        comment_lines = []
        comment_lines.append(f"{old_path}")
        comment_lines.append(f"{modified_lines[1]}")
        comment_lines.append(old_line)
        comment_lines.append(new_line)
        target_dir = "bugs"
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        output_file = os.path.join(target_dir, "bug" + str(number) + ".txt")
        with open(output_file, "w") as file:
            for line in comment_lines:
                file.write(line + "\n")
        # for line_number, line_content in enumerate(diff.split("\n"), start=1):
        #     if line_number in modified_lines:
        #         comment_lines.append(
        #             f"Line {line_number+modified_lines[0]-1}: {line_content}"
        #         )

        # 根据修改的行号替换文件内容
        for line_number, line_content in enumerate(file_content, start=1):
            if line_number == modified_lines[1]:
                file_content[line_number - 1] = f"{old_line[1:]}\n"

        # 保存修改后的文件内容
        with open(file_path, "w") as file:
            file.writelines(file_content)

        source_file = os.path.join(repo_path, old_path)
        target_directory = "download_files"
        new_filename = "bug" + str(number) + "_" + file_name
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        target_file = os.path.join(target_directory, new_filename)
        shutil.copy(source_file, target_file)
        # # 删除临时目录
        # os.system(f"rm -rf {temp_dir}")
