#!/usr/bin/env python3
"""Regenerate the auto-updated 'Recently Updated' section of the profile README.

- With no token: lists the user's PUBLIC repos (GitHub public API).
- With a PROFILE_TOKEN secret (a PAT with `repo` scope): also includes PRIVATE repos.

The section is delimited by the START/END markers below; everything between them
is replaced on each run.
"""
import json
import os
import re
import urllib.request

USER = "ahmedessameldeen"
README = "README.md"
START = "<!--START_SECTION:projects-->"
END = "<!--END_SECTION:projects-->"
MAX_REPOS = 6

token = os.environ.get("PROFILE_TOKEN")  # optional user PAT; enables private repos
headers = {"Accept": "application/vnd.github+json", "User-Agent": USER}
if token:
    headers["Authorization"] = f"Bearer {token}"
    url = "https://api.github.com/user/repos?per_page=100&sort=pushed&affiliation=owner"
else:
    url = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed&type=owner"


def fetch(u):
    req = urllib.request.Request(u, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


repos = fetch(url)
repos = [
    r for r in repos
    if not r.get("fork") and not r.get("archived") and r["name"].lower() != USER.lower()
]
repos.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
repos = repos[:MAX_REPOS]

rows = ["| Project | Description | Language | Updated |", "|---|---|---|---|"]
for r in repos:
    desc = (r.get("description") or "—").replace("|", "\\|")
    lang = r.get("language") or "—"
    updated = (r.get("pushed_at") or "")[:10]
    rows.append(f"| [{r['name']}]({r['html_url']}) | {desc} | {lang} | {updated} |")
section = "\n".join(rows)

with open(README, encoding="utf-8") as f:
    content = f.read()

new = re.sub(
    re.escape(START) + r".*?" + re.escape(END),
    f"{START}\n{section}\n{END}",
    content,
    flags=re.DOTALL,
)

if new != content:
    with open(README, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"README updated with {len(repos)} repos.")
else:
    print("No changes.")
