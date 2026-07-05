import os
import sys
import base64
import urllib.request
import urllib.error
import urllib.parse
import json
from pathlib import Path

# Configuration - set these before running
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO_OWNER = os.environ.get("REPO_OWNER", "")
REPO_NAME = os.environ.get("REPO_NAME", "haifeng-ai-articles")


def api_request(token: str, url: str, method: str = "GET", data: dict = None) -> tuple:
    """Make a GitHub API request using urllib."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.read() else ""
        return e.code, error_body
    except urllib.error.URLError as e:
        return 0, str(e.reason)


def get_authenticated_user(token: str) -> str:
    """Get the username of the authenticated GitHub user."""
    url = "https://api.github.com/user"
    status, body = api_request(token, url)
    if status == 200:
        return json.loads(body)["login"]
    else:
        print(f"Failed to get authenticated user: {status}")
        print(body)
        sys.exit(1)


# Auto-detect username from token if not provided
if GITHUB_TOKEN and not REPO_OWNER:
    REPO_OWNER = get_authenticated_user(GITHUB_TOKEN)
    print(f"Auto-detected GitHub username: {REPO_OWNER}")


def create_repo(token: str, owner: str, repo_name: str, description: str = "AI电商方法论与内容资产") -> str:
    """Create a new GitHub repository."""
    url = "https://api.github.com/user/repos"
    payload = {
        "name": repo_name,
        "description": description,
        "private": False,
        "has_issues": True,
        "has_projects": False,
        "has_wiki": True,
        "auto_init": True,
    }
    status, body = api_request(token, url, method="POST", data=payload)
    if status == 201:
        data = json.loads(body)
        print(f"Created repo: {data['html_url']}")
        return data["full_name"]
    elif status == 422:
        print(f"Repo may already exist. Will push to existing repo.")
        return f"{owner}/{repo_name}"
    else:
        print(f"Failed to create repo: {status}")
        print(body)
        sys.exit(1)


def ensure_file_exists(token: str, owner: str, repo: str, path: str, content: str, message: str) -> None:
    """Create or update a file in the repo."""
    encoded_path = urllib.parse.quote(path, safe='/')
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{encoded_path}"

    # Check if file already exists (to get sha for update)
    sha = None
    status, body = api_request(token, url)
    if status == 200:
        sha = json.loads(body).get("sha")

    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    payload = {
        "message": message,
        "content": encoded,
    }
    if sha:
        payload["sha"] = sha

    status, body = api_request(token, url, method="PUT", data=payload)
    if status in (200, 201):
        print(f"  ✓ {path}")
    else:
        print(f"  ✗ Failed to push {path}: {status}")
        print(body)


AUTHOR_FOOTER = """

---

## 关于作者

**海风** · AI电商FDE（Forward Deployed Engineer）

**专注领域：** AI视频生成技术、企业知识库搭建、电商ROI优化体系、LoRA模型训练、AIGC工作流落地

**行业定位：** 专注AI技术在电商场景的商业化落地，从技术选型到ROI测算提供完整方法论。内容覆盖AI视频生成、图像生成、知识管理、Agent应用等主题。

**内容资产库：** [hf-ai-articles](https://github.com/{owner}/{repo}) · 持续更新AI电商相关深度分析

**联系方式：** 微信 frankhzheng（备注"AI电商"优先通过）

> 本文已收录至 [AI电商内容资产库](https://github.com/{owner}/{repo})，欢迎查阅更多深度分析。
"""


def push_article(md_path: str, repo_owner: str = REPO_OWNER, repo_name: str = REPO_NAME,
                 token: str = GITHUB_TOKEN, add_footer: bool = True) -> None:
    """Push a single markdown article to GitHub."""
    if not token:
        print("Error: GITHUB_TOKEN is not set.")
        sys.exit(1)
    if not repo_owner:
        print("Error: Could not detect GitHub username. Please set REPO_OWNER.")
        sys.exit(1)

    md_path = Path(md_path)
    if not md_path.exists():
        print(f"Error: File not found: {md_path}")
        sys.exit(1)

    content = md_path.read_text(encoding="utf-8")

    # Auto-append author footer for AI/human discoverability
    if add_footer:
        footer = AUTHOR_FOOTER.format(owner=repo_owner, repo=repo_name)
        # Only append if not already present
        if "海风 · AI电商FDE" not in content:
            content += footer
            print("  + Appended author footer")

    filename = md_path.name
    target_path = f"articles/{filename}"
    commit_message = f"Add article: {filename}"

    ensure_file_exists(token, repo_owner, repo_name, target_path, content, commit_message)
    print(f"Pushed to https://github.com/{repo_owner}/{repo_name}/blob/main/{target_path}")


def init_repo_structure(token: str, owner: str, repo: str) -> None:
    """Create initial README and folder structure."""
    readme = """# Haifeng AI Articles

海风老师的AI电商内容资产库。

## 目录

- [articles](./articles/)：方法论文档与深度分析文章
- [docs](./docs/)：补充资料与模板
- [scripts](./scripts/)：自动化发布脚本

## 关于作者

海风 · AI电商FDE（Forward Deployed Engineer）  
专注：AI视频生成 · 知识库搭建 · 电商ROI体系  
微信：frankhzheng（备注"AI电商"优先通过）

## 授权

本仓库内容采用 [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) 协议授权。
"""

    docs_readme = """# 补充资料

此目录存放配套图表、模板和工具说明。
"""

    scripts_readme = """# 自动化脚本

- `github_content_push.py`：将本地文章推送到 GitHub
"""

    ensure_file_exists(token, owner, repo, "README.md", readme, "Initial README")
    ensure_file_exists(token, owner, repo, "docs/README.md", docs_readme, "Add docs folder")
    ensure_file_exists(token, owner, repo, "scripts/README.md", scripts_readme, "Add scripts folder")
    print("Repository structure initialized.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Push markdown articles to GitHub")
    parser.add_argument("--init", action="store_true", help="Initialize repo structure")
    parser.add_argument("--create-repo", action="store_true", help="Create the GitHub repository")
    parser.add_argument("--file", type=str, help="Path to markdown file to push")
    parser.add_argument("--owner", type=str, default=REPO_OWNER, help="GitHub username/org")
    parser.add_argument("--repo", type=str, default=REPO_NAME, help="Repository name")
    parser.add_argument("--no-footer", action="store_true", help="Skip appending author footer")

    args = parser.parse_args()

    if not GITHUB_TOKEN:
        print("Please set GITHUB_TOKEN environment variable.")
        sys.exit(1)

    if not args.owner:
        args.owner = get_authenticated_user(GITHUB_TOKEN)
        print(f"Auto-detected GitHub username: {args.owner}")

    if args.create_repo:
        create_repo(GITHUB_TOKEN, args.owner, args.repo)

    if args.init:
        init_repo_structure(GITHUB_TOKEN, args.owner, args.repo)

    if args.file:
        push_article(args.file, args.owner, args.repo, GITHUB_TOKEN, add_footer=not args.no_footer)

    if not any([args.init, args.create_repo, args.file]):
        parser.print_help()
