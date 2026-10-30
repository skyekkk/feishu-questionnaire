#!/usr/bin/env python3
"""从安装时绑定的 GitHub 私有仓库安全同步技能；不覆盖本地改动。"""
import json
import re
import subprocess
import sys
from pathlib import Path


def git(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True,
        timeout=35, env=git_env(),
    )
    if result.returncode:
        raise RuntimeError("Git 操作未完成，请检查网络、GitHub 登录或仓库权限。")
    return result.stdout.strip()


def git_env():
    import os
    return dict(os.environ, GIT_TERMINAL_PROMPT="0")


def sync(root, expected):
    if git(root, "rev-parse", "--show-toplevel") != str(root):
        return {"status": "blocked", "message": "技能目录不是独立仓库，已停止更新。"}
    if git(root, "remote", "get-url", "origin") != expected:
        return {"status": "blocked", "message": "远端来源发生变化，已停止更新。"}
    if git(root, "symbolic-ref", "--short", "HEAD") != "main":
        return {"status": "blocked", "message": "当前不在 main 分支，已保留原状。"}
    if git(root, "status", "--porcelain", "--untracked-files=all"):
        return {"status": "blocked", "message": "存在本地改动，已保留，未覆盖。"}
    before = git(root, "rev-parse", "HEAD")
    git(root, "fetch", "--no-tags", "origin", "main")
    latest = git(root, "rev-parse", "FETCH_HEAD")
    if before == latest:
        return {"status": "current", "commit": before, "message": "当前已是最新版。"}
    ancestor = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", before, latest],
        capture_output=True, timeout=15, env=git_env(),
    )
    if ancestor.returncode != 0:
        return {"status": "blocked", "message": "本地与远端版本分叉，已保留，未强制覆盖。"}
    git(root, "merge", "--ff-only", latest)
    return {"status": "updated", "commit": latest, "previous": before,
            "message": "已同步新版，请重新读取技能入口后继续。"}


def main():
    root = Path(__file__).resolve().parents[1]
    if not (root / ".git").is_dir():
        result = {"status": "not-managed", "message": "这是未绑定更新源的副本，请按仓库首页使用 Git 安装。"}
    else:
        try:
            expected = git(root, "config", "--local", "--get", "--default", "", "skill.trustedOrigin")
            if not re.fullmatch(r"https://github[.]com/[A-Za-z0-9_.-]+/feishu-questionnaire[.]git", expected):
                result = {"status": "blocked", "message": "缺少有效的安装来源绑定，未更新。"}
            else:
                result = sync(root, expected)
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            result = {"status": "unavailable", "message": "未能检查新版，请检查 GitHub 登录、仓库权限和网络；本地文件已保留。"}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in ("current", "updated") else 2


if __name__ == "__main__":
    sys.exit(main())
