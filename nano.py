#!/usr/bin/env python3
"""
Git File Uploader
-----------------
Kisi bhi local file ko GitHub repo me upload karne ke liye.
"""

import os
import sys
import base64
import requests
from pathlib import Path


class GitUploader:
    def __init__(self, token: str, username: str, repo: str, branch: str = "main"):
        self.token = token
        self.username = username
        self.repo = repo
        self.branch = branch
        self.api_base = f"https://api.github.com/repos/{username}/{repo}/contents"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def _get_file_sha(self, repo_path: str):
        """Agar file already exists to uska SHA nikalta hai (update ke liye)."""
        url = f"{self.api_base}/{repo_path}"
        r = requests.get(url, headers=self.headers, params={"ref": self.branch})
        if r.status_code == 200:
            return r.json().get("sha")
        return None

    def upload_file(self, local_path: str, remote_name: str, commit_msg: str = None,
                    remote_folder: str = ""):
        local_path = Path(local_path)
        if not local_path.is_file():
            print(f"❌ File nahi mili: {local_path}")
            return False

        # File read karo aur base64 me encode karo
        with open(local_path, "rb") as f:
            content_bytes = f.read()
        content_b64 = base64.b64encode(content_bytes).decode("utf-8")

        # Remote path banao (folder + filename)
        repo_path = f"{remote_folder.strip('/')}/{remote_name}" if remote_folder else remote_name

        # Agar same naam ki file pehle se hai to SHA lo
        sha = self._get_file_sha(repo_path)

        payload = {
            "message": commit_msg or f"Upload {remote_name}",
            "content": content_b64,
            "branch": self.branch,
        }
        if sha:
            payload["sha"] = sha

        url = f"{self.api_base}/{repo_path}"
        r = requests.put(url, headers=self.headers, json=payload)

        if r.status_code in (200, 201):
            action = "Updated" if sha else "Uploaded"
            print(f"✅ {action}: {repo_path}")
            print(f"🔗 {r.json()['content']['html_url']}")
            return True
        else:
            print(f"❌ Upload failed ({r.status_code}): {r.text}")
            return False


def main():
    print("=" * 50)
    print("      🚀 GitHub File Uploader")
    print("=" * 50)

    # --- Inputs ---
    token = input("🔑 GitHub Token: ").strip()
    username = input("👤 GitHub Username: ").strip()
    repo = input("📦 Repository Name: ").strip()
    branch = input("🌿 Branch (default: main): ").strip() or "main"

    local_path = input("📁 Local File Path: ").strip().strip('"').strip("'")
    remote_name = input("📝 Remote File Name (jaise file.txt): ").strip()
    remote_folder = input("📂 Remote Folder (optional, Enter skip): ").strip()
    commit_msg = input("💬 Commit Message (optional): ").strip() or None

    uploader = GitUploader(token, username, repo, branch)
    uploader.upload_file(local_path, remote_name, commit_msg, remote_folder)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⛔ Cancelled.")
        sys.exit(1)