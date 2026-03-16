"""
自动版本号计算脚本 (CI流程)
版本号格式: x.x.x
- 主版本号: 检测到[major]时更新
- 次版本号: 检测到[minor]时更新
- 修复版本号: 距离上一个标签的commit数
"""

import subprocess
import re
import sys
import os


def get_git_tags():
    """获取所有git标签"""
    try:
        result = subprocess.run(
            ["git", "tag", "-l", "v*"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        tags = [tag.strip() for tag in result.stdout.strip().split("\n") if tag.strip()]
        # 按字母序排序，最新的在前
        return sorted(tags, reverse=True)
    except subprocess.CalledProcessError:
        return []


def get_commits_since_tag(tag=None):
    """获取从指定标签(或从头开始)到当前的提交数"""
    try:
        if tag:
            result = subprocess.run(
                ["git", "rev-list", f"{tag}..HEAD", "--count"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )
        else:
            # 从头开始计算
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )
        return int(result.stdout.strip())
    except subprocess.CalledProcessError:
        return 0


def get_commit_messages_since_tag(tag=None):
    """获取从指定标签(或从头开始)到当前的提交信息"""
    try:
        if tag:
            result = subprocess.run(
                ["git", "log", f"{tag}..HEAD", "--pretty=format:%s"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )
        else:
            # 从头开始获取
            result = subprocess.run(
                ["git", "log", "--pretty=format:%s"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )
        return result.stdout.strip().split("\n")
    except subprocess.CalledProcessError:
        return []


def get_latest_commit():
    """获取最新的提交信息"""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def calculate_version():
    """计算版本号"""
    # 获取所有标签
    tags = get_git_tags()

    # 获取最新标签
    latest_tag = tags[0] if tags else None

    # 获取自最新标签以来的提交数
    commits_count = get_commits_since_tag(latest_tag)

    # 获取自最新标签以来的所有提交信息（改为检查所有提交，而不仅仅是最新一个）
    commit_messages = get_commit_messages_since_tag(latest_tag)

    # 解析当前版本
    if latest_tag and latest_tag.startswith("v"):
        current_version = latest_tag[1:]  # 去掉v前缀
        try:
            major, minor, patch = map(int, current_version.split("."))
        except ValueError:
            # 如果标签格式不正确，从0.0.0开始
            major, minor, patch = 0, 0, 0
    else:
        # 没有标签，从0.0.0开始
        major, minor, patch = 0, 0, 0

    # 检查所有提交信息（按优先级），决定是否更新主版本或次版本
    has_major = any("[major]" in msg.lower() for msg in commit_messages)
    has_minor = any("[minor]" in msg.lower() for msg in commit_messages)

    if has_major:
        # 更新主版本，重置次版本和修复版本
        major += 1
        minor = 0
        patch = 0
    elif has_minor:
        # 更新次版本，重置修复版本
        minor += 1
        patch = 0
    else:
        # 更新修复版本为距离上一个标签的提交数
        patch = commits_count

    return f"{major}.{minor}.{patch}"


def create_tag(version):
    """创建git标签"""
    try:
        tag_name = f"v{version}"
        # 检查标签是否已存在
        result = subprocess.run(
            ["git", "rev-parse", "--verify", f"refs/tags/{tag_name}"],
            capture_output=True,
            encoding="utf-8",
        )
        if result.returncode != 0:  # 标签不存在
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", f"Release version {version}"],
                check=True,
                encoding="utf-8",
            )
            print(f"Created tag: {tag_name}")
        else:
            print(f"Tag {tag_name} already exists")
    except subprocess.CalledProcessError as e:
        print(f"Could not create tag {version}: {e}")


def main():
    """主函数"""
    try:
        version = calculate_version()
        print(version)

        # 如果是主版本或次版本更新，创建标签
        commit_messages = get_commit_messages_since_tag(None)
        has_major = any("[major]" in msg.lower() for msg in commit_messages)
        has_minor = any("[minor]" in msg.lower() for msg in commit_messages)

        if has_major or has_minor:
            create_tag(version)

        # 同时写入VERSION文件
        with open("VERSION", "w") as f:
            f.write(version)

        print(f"Version calculated: {version}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
