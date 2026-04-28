"""
GitHub Service - Handles all GitHub API interactions
"""

import httpx
import json
import re
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    """Service for interacting with GitHub API"""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self):
        self.session = None
        
    async def _get_session(self, token: Optional[str] = None):
        """Create or get HTTP session with GitHub auth"""
        if not self.session:
            headers = {}
            if token:
                headers["Authorization"] = f"token {token}"
            headers["Accept"] = "application/vnd.github.v3+json"
            self.session = httpx.AsyncClient(headers=headers, timeout=30.0)
        return self.session
    
    def parse_pr_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Parse GitHub PR URL to extract owner, repo, and PR number
        
        Supports formats:
        - https://github.com/owner/repo/pull/123
        - https://api.github.com/repos/owner/repo/pulls/123
        """
        # Pattern for standard GitHub URL
        pattern = r'github\.com/([^/]+)/([^/]+)/pull/(\d+)'
        match = re.search(pattern, url)
        
        if match:
            return {
                "owner": match.group(1),
                "repo": match.group(2),
                "pr_number": int(match.group(3))
            }
        
        # Pattern for API URL
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
        """
        Fetch PR details from GitHub API
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: PR number
            token: GitHub API token (optional)
            
        Returns:
            PR details dictionary
        """
        try:
            session = await self._get_session(token)
            
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
            response = await session.get(url)
            response.raise_for_status()
            
            pr_data = response.json()
            
            return {
                "number": pr_data.get("number"),
                "title": pr_data.get("title"),
                "description": pr_data.get("body", ""),
                "author": pr_data.get("user", {}).get("login"),
                "created_at": pr_data.get("created_at"),
                "updated_at": pr_data.get("updated_at"),
                "state": pr_data.get("state"),
                "commits": pr_data.get("commits"),
                "additions": pr_data.get("additions"),
                "deletions": pr_data.get("deletions"),
                "changed_files": pr_data.get("changed_files"),
                "labels": [label.get("name") for label in pr_data.get("labels", [])],
                "html_url": pr_data.get("html_url")
            }
            
        except Exception as e:
            logger.error(f"Error fetching PR details: {str(e)}")
            raise
    
    async def get_pr_diff(self, owner: str, repo: str, pr_number: int,
                          token: Optional[str] = None) -> str:
        """
        Fetch the diff for a PR
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: PR number
            token: GitHub API token (optional)
            
        Returns:
            Unified diff format
        """
        try:
            session = await self._get_session(token)
            
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
            headers = {"Accept": "application/vnd.github.v3.diff"}
            
            response = await session.get(url, headers=headers)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error fetching PR diff: {str(e)}")
            raise
    
    async def get_pr_files(self, owner: str, repo: str, pr_number: int,
                           token: Optional[str] = None) -> List[Dict]:
        """
        Get list of files changed in PR
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: PR number
            token: GitHub API token (optional)
            
        Returns:
            List of file change objects
        """
        try:
            session = await self._get_session(token)
            
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/files"
            
            all_files = []
            page = 1
            per_page = 100
            
            while True:
                response = await session.get(
                    url,
                    params={"page": page, "per_page": per_page}
                )
                response.raise_for_status()
                
                files = response.json()
                if not files:
                    break
                
                all_files.extend(files)
                
                # Check if there are more pages
                if len(files) < per_page:
                    break
                page += 1
            
            return all_files
            
        except Exception as e:
            logger.error(f"Error fetching PR files: {str(e)}")
            raise
    
    async def get_file_content(self, owner: str, repo: str, path: str,
                               ref: str = "main", token: Optional[str] = None) -> str:
        """
        Get content of a file from repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path in repository
            ref: Git reference (branch, tag, commit)
            token: GitHub API token (optional)
            
        Returns:
            File content
        """
        try:
            session = await self._get_session(token)
            
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"
            
            response = await session.get(url, params={"ref": ref})
            response.raise_for_status()
            
            import base64
            data = response.json()
            
            if "content" in data:
                return base64.b64decode(data["content"]).decode("utf-8")
            else:
                return data.get("message", "")
            
        except Exception as e:
            logger.error(f"Error fetching file content: {str(e)}")
            raise
    
    async def get_commits(self, owner: str, repo: str, pr_number: int,
                          token: Optional[str] = None) -> List[Dict]:
        """
        Get list of commits in a PR
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: PR number
            token: GitHub API token (optional)
            
        Returns:
            List of commit objects
        """
        try:
            session = await self._get_session(token)
            
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/commits"
            
            response = await session.get(url, params={"per_page": 100})
            response.raise_for_status()
            
            commits = response.json()
            
            return [
                {
                    "sha": commit.get("sha"),
                    "message": commit.get("commit", {}).get("message"),
                    "author": commit.get("commit", {}).get("author", {}).get("name"),
                    "date": commit.get("commit", {}).get("author", {}).get("date")
                }
                for commit in commits
            ]
            
        except Exception as e:
            logger.error(f"Error fetching commits: {str(e)}")
            raise
    
    async def close_session(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.aclose()
            self.session = None
