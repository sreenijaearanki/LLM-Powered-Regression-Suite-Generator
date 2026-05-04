"""
GitHub Service - Handles all GitHub API interactions
Auto-uses GITHUB_TOKEN env var for authenticated requests (5000 req/hr).
"""

import httpx
import re
import os
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://api.github.com"


def _make_headers(token: Optional[str] = None, accept: str = "application/vnd.github.v3+json") -> Dict:
    """Build GitHub API headers, auto-loading token from env if not provided."""
    effective_token = token or os.getenv("GITHUB_TOKEN")
    headers = {"Accept": accept}
    if effective_token:
        headers["Authorization"] = f"token {effective_token}"
        logger.info("GitHub: authenticated request (5000 req/hr)")
    else:
        logger.warning("GitHub: unauthenticated request (60 req/hr) — set GITHUB_TOKEN env var")
    return headers


def _check_response(response: httpx.Response) -> None:
    """Raise friendly errors for common GitHub API failures."""
    if response.status_code == 403:
        raise Exception(
            "GitHub API rate limit exceeded. Paste a GitHub token in the "
            "form field to get 5000 requests/hour instead of 60."
        )
    if response.status_code == 404:
        raise Exception(
            "PR not found (404). Please verify: (1) the PR number exists, "
            "(2) the repo is public, (3) or provide a GitHub token for private repos."
        )
    response.raise_for_status()


class GitHubService:

    def parse_pr_url(self, url: str) -> Optional[Dict]:
        """Parse GitHub PR URL → {owner, repo, pr_number}."""
        for pattern in [
            r'github\.com/([^/]+)/([^/]+)/pull/(\d+)',
            r'api\.github\.com/repos/([^/]+)/([^/]+)/pulls/(\d+)',
        ]:
            m = re.search(pattern, url)
            if m:
                return {"owner": m.group(1), "repo": m.group(2), "pr_number": int(m.group(3))}
        logger.warning(f"Could not parse GitHub URL: {url}")
        return None

    async def fetch_pr_details(self, owner: str, repo: str, pr_number: int,
                               token: Optional[str] = None) -> Dict:
        """Fetch PR metadata."""
        try:
            async with httpx.AsyncClient(headers=_make_headers(token), timeout=30.0) as client:
                r = await client.get(f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}")
                _check_response(r)
                pr = r.json()
                return {
                    "number": pr.get("number"),
                    "title": pr.get("title"),
                    "description": pr.get("body", ""),
                    "author": pr.get("user", {}).get("login"),
                    "created_at": pr.get("created_at"),
                    "updated_at": pr.get("updated_at"),
                    "state": pr.get("state"),
                    "commits": pr.get("commits"),
                    "additions": pr.get("additions"),
                    "deletions": pr.get("deletions"),
                    "changed_files": pr.get("changed_files"),
                    "labels": [l.get("name") for l in pr.get("labels", [])],
                    "html_url": pr.get("html_url"),
                }
        except Exception as e:
            logger.error(f"fetch_pr_details error: {e}")
            raise

    async def get_pr_diff(self, owner: str, repo: str, pr_number: int,
                          token: Optional[str] = None) -> str:
        """Fetch unified diff for a PR."""
        try:
            headers = _make_headers(token, accept="application/vnd.github.v3.diff")
            async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
                r = await client.get(f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}")
                _check_response(r)
                return r.text
        except Exception as e:
            logger.error(f"get_pr_diff error: {e}")
            raise

    async def get_pr_files(self, owner: str, repo: str, pr_number: int,
                           token: Optional[str] = None) -> List[Dict]:
        """Get list of files changed in PR."""
        try:
            all_files = []
            page = 1
            while True:
                async with httpx.AsyncClient(headers=_make_headers(token), timeout=30.0) as client:
                    r = await client.get(
                        f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/files",
                        params={"page": page, "per_page": 100}
                    )
                    _check_response(r)
                    files = r.json()
                if not files:
                    break
                all_files.extend(files)
                if len(files) < 100:
                    break
                page += 1
            return all_files
        except Exception as e:
            logger.error(f"get_pr_files error: {e}")
            raise

    async def get_commits(self, owner: str, repo: str, pr_number: int,
                          token: Optional[str] = None) -> List[Dict]:
        """Get commit list for a PR."""
        try:
            async with httpx.AsyncClient(headers=_make_headers(token), timeout=30.0) as client:
                r = await client.get(
                    f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/commits",
                    params={"per_page": 100}
                )
                _check_response(r)
                return [
                    {
                        "sha": c.get("sha"),
                        "message": c.get("commit", {}).get("message"),
                        "author": c.get("commit", {}).get("author", {}).get("name"),
                        "date": c.get("commit", {}).get("author", {}).get("date"),
                    }
                    for c in r.json()
                ]
        except Exception as e:
            logger.error(f"get_commits error: {e}")
            raise
