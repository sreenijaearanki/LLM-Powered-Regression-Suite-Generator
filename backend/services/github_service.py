"""
GitHub Service - Handles all GitHub API interactions
"""

import httpx
import re
import os
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for interacting with GitHub API"""

    BASE_URL = "https://api.github.com"

    async def _get_session(self, token: Optional[str] = None):
        """Create HTTP session, auto-using GITHUB_TOKEN env var as fallback."""
        effective_token = token or os.getenv("GITHUB_TOKEN")
        headers = {"Accept": "application/vnd.github.v3+json"}
        if effective_token:
            headers["Authorization"] = f"token {effective_token}"
            logger.info("GitHub API: authenticated (5000 req/hr limit)")
        else:
            logger.warning("GitHub API: unauthenticated (60 req/hr limit)")
        return httpx.AsyncClient(headers=headers, timeout=30.0)

    def _check_response(self, response: httpx.Response) -> None:
        """Raise friendly errors for common GitHub API failures."""
        if response.status_code == 403:
            raise Exception(
                "GitHub API rate limit exceeded. Add a GitHub token in the "
                "form to get 5000 requests/hour instead of 60."
            )
        if response.status_code == 404:
            raise Exception(
                "PR not found. Check the URL is correct and the repo is "
                "public (or provide a GitHub token for private repos)."
            )
        response.raise_for_status()

    def parse_pr_url(self, url: str) -> Optional[Dict[str, str]]:
        """Parse GitHub PR URL to extract owner, repo, and PR number."""
        pattern = r'github\.com/([^/]+)/([^/]+)/pull/(\d+)'
        match = re.search(pattern, url)
        if match:
            return {
                "owner": match.group(1),
                "repo": match.group(2),
                "pr_number": int(match.group(3))
            }
        pattern = r'api\.github\.com/repos/([^/]+)/([^/]+)/pulls/(\d+)'
        match = re.search(pattern, url)
        if match:
            return {
                "owner": match.group(1),
                "repo": match.group(2),
                "pr_number": int(match.group(3))
            }
        logger.warning(f"Could not parse GitHub URL: {url}")
        return None

    async def fetch_pr_details(self, owner: str, repo: str, pr_number: int,
                               token: Optional[str] = None) -> Dict:
        """Fetch PR details from GitHub API."""
        try:
            session = await self._get_session(token)
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
            response = await session.get(url)
            self._check_response(response)
            pr = response.json()
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
            logger.error(f"Error fetching PR details: {e}")
            raise

    async def get_pr_diff(self, owner: str, repo: str, pr_number: int,
                          token: Optional[str] = None) -> str:
        """Fetch the unified diff for a PR."""
        try:
            session = await self._get_session(token)
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
            response = await session.get(url, headers={"Accept": "application/vnd.github.v3.diff"})
            self._check_response(response)
            return response.text
        except Exception as e:
            logger.error(f"Error fetching PR diff: {e}")
            raise

    async def get_pr_files(self, owner: str, repo: str, pr_number: int,
                           token: Optional[str] = None) -> List[Dict]:
        """Get list of files changed in PR."""
        try:
            session = await self._get_session(token)
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/files"
            all_files = []
            page = 1
            while True:
                response = await session.get(url, params={"page": page, "per_page": 100})
                self._check_response(response)
                files = response.json()
                if not files:
                    break
                all_files.extend(files)
                if len(files) < 100:
                    break
                page += 1
            return all_files
        except Exception as e:
            logger.error(f"Error fetching PR files: {e}")
            raise

    async def get_file_content(self, owner: str, repo: str, path: str,
                               ref: str = "main", token: Optional[str] = None) -> str:
        """Get content of a file from repository."""
        try:
            import base64
            session = await self._get_session(token)
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"
            response = await session.get(url, params={"ref": ref})
            self._check_response(response)
            data = response.json()
            if "content" in data:
                return base64.b64decode(data["content"]).decode("utf-8")
            return data.get("message", "")
        except Exception as e:
            logger.error(f"Error fetching file content: {e}")
            raise

    async def get_commits(self, owner: str, repo: str, pr_number: int,
                          token: Optional[str] = None) -> List[Dict]:
        """Get list of commits in a PR."""
        try:
            session = await self._get_session(token)
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/commits"
            response = await session.get(url, params={"per_page": 100})
            self._check_response(response)
            return [
                {
                    "sha": c.get("sha"),
                    "message": c.get("commit", {}).get("message"),
                    "author": c.get("commit", {}).get("author", {}).get("name"),
                    "date": c.get("commit", {}).get("author", {}).get("date"),
                }
                for c in response.json()
            ]
        except Exception as e:
            logger.error(f"Error fetching commits: {e}")
            raise
