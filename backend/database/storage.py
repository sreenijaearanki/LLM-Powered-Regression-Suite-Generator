"""
Storage Manager - Handles data persistence for jobs and results
Uses file-based storage for simplicity, can be extended to use databases
"""

import json
import os
import uuid
import logging
from typing import Optional, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages storage of job data and results"""
    
    def __init__(self, storage_dir: str = "/tmp/llm_regression_storage"):
        self.storage_dir = Path(storage_dir)
        self.jobs_dir = self.storage_dir / "jobs"
        self.results_dir = self.storage_dir / "results"
        
        # Create directories if they don't exist
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Storage initialized at {self.storage_dir}")
    
    def create_job_id(self) -> str:
        """Create a unique job ID"""
        return str(uuid.uuid4())
    
    def update_job_status(self, job_id: str, status: str, progress: int,
                         error: Optional[str] = None) -> bool:
        """
        Update the status of a job
        
        Args:
            job_id: Unique job identifier
            status: Current status (processing, completed, failed, etc.)
            progress: Progress percentage (0-100)
            error: Optional error message
            
        Returns:
            True if successful
        """
        try:
            job_file = self.jobs_dir / f"{job_id}.json"
            
            job_data = {
                "job_id": job_id,
                "status": status,
                "progress": progress,
                "updated_at": datetime.now().isoformat(),
                "error": error
            }
            
            # Load existing data if available
            if job_file.exists():
                with open(job_file, 'r') as f:
                    existing = json.load(f)
                job_data.update(existing)
                job_data["status"] = status
                job_data["progress"] = progress
                job_data["updated_at"] = datetime.now().isoformat()
                if error:
                    job_data["error"] = error
            else:
                job_data["created_at"] = datetime.now().isoformat()
            
            with open(job_file, 'w') as f:
                json.dump(job_data, f, indent=2)
            
            logger.info(f"Updated job {job_id}: {status} ({progress}%)")
            return True
            
        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
            return False
    
    def save_job_result(self, job_id: str, result: dict) -> bool:
        """
        Save the final result of a job
        
        Args:
            job_id: Unique job identifier
            result: Result data to save
            
        Returns:
            True if successful
        """
        try:
            result_file = self.results_dir / f"{job_id}.json"
            
            result_data = {
                "job_id": job_id,
                "result": result,
                "saved_at": datetime.now().isoformat()
            }
            
            with open(result_file, 'w') as f:
                json.dump(result_data, f, indent=2)
            
            # Update job status to completed
            self.update_job_status(job_id, "completed", 100)
            
            logger.info(f"Saved result for job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving result: {str(e)}")
            return False
    
    def get_job_status(self, job_id: str) -> Tuple[str, int, Optional[dict], Optional[str]]:
        """
        Get the status of a job
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Tuple of (status, progress, result, error)
        """
        try:
            job_file = self.jobs_dir / f"{job_id}.json"
            
            if not job_file.exists():
                raise FileNotFoundError(f"Job {job_id} not found")
            
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            status = job_data.get("status", "unknown")
            progress = job_data.get("progress", 0)
            error = job_data.get("error")
            result = None
            
            # Load result if available
            if status == "completed":
                result_file = self.results_dir / f"{job_id}.json"
                if result_file.exists():
                    with open(result_file, 'r') as f:
                        result_data = json.load(f)
                        result = result_data.get("result")
            
            return status, progress, result, error
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting job status: {str(e)}")
            return "unknown", 0, None, str(e)
    
    def get_all_jobs(self, limit: int = 50) -> list:
        """
        Get a list of all jobs
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of job data
        """
        try:
            jobs = []
            
            # Get all job files, sorted by modification time (newest first)
            job_files = sorted(
                self.jobs_dir.glob("*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:limit]
            
            for job_file in job_files:
                with open(job_file, 'r') as f:
                    job_data = json.load(f)
                    jobs.append(job_data)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting jobs list: {str(e)}")
            return []
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job and its results
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            True if successful
        """
        try:
            job_file = self.jobs_dir / f"{job_id}.json"
            result_file = self.results_dir / f"{job_id}.json"
            
            if job_file.exists():
                job_file.unlink()
            
            if result_file.exists():
                result_file.unlink()
            
            logger.info(f"Deleted job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting job: {str(e)}")
            return False
    
    def export_results(self, job_id: str, format: str = "json") -> Optional[str]:
        """
        Export job results in specified format
        
        Args:
            job_id: Unique job identifier
            format: Export format (json, md, html)
            
        Returns:
            Formatted output string
        """
        try:
            _, _, result, _ = self.get_job_status(job_id)
            
            if not result:
                return None
            
            if format == "json":
                return json.dumps(result, indent=2)
            
            elif format == "md":
                return self._format_as_markdown(result)
            
            elif format == "html":
                return self._format_as_html(result)
            
            else:
                return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error exporting results: {str(e)}")
            return None
    
    def _format_as_markdown(self, result: dict) -> str:
        """Format result as markdown"""
        
        md = "# Test Generation Results\n\n"
        
        if "pr_info" in result:
            md += "## PR Information\n"
            pr = result["pr_info"]
            md += f"- **Title**: {pr.get('title')}\n"
            md += f"- **Author**: {pr.get('author')}\n"
            md += f"- **State**: {pr.get('state')}\n"
            md += f"- **Files Changed**: {pr.get('changed_files')}\n"
            md += f"- **Additions**: +{pr.get('additions')}\n"
            md += f"- **Deletions**: -{pr.get('deletions')}\n\n"
        
        if "test_summary" in result:
            md += "## Test Summary\n"
            summary = result["test_summary"]
            md += f"- **Tests Generated**: {summary.get('total_tests_generated')}\n"
            md += f"- **Framework**: {summary.get('framework')}\n"
            md += f"- **Functions Covered**: {summary.get('functions_covered')}\n\n"
        
        if "generated_tests" in result:
            md += "## Generated Tests\n"
            for test in result["generated_tests"][:5]:  # Show first 5
                md += f"### {test.get('name')}\n"
                md += f"- **Function**: {test.get('function')}\n"
                md += f"- **Priority**: {test.get('priority')}\n"
                md += "```\n"
                md += test.get('code', '')[:500] + "\n"
                md += "```\n\n"
        
        return md
    
    def _format_as_html(self, result: dict) -> str:
        """Format result as HTML"""
        
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Generation Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { margin-bottom: 30px; }
        h1, h2 { color: #333; }
        .test-case { background: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }
        pre { background: #f9f9f9; padding: 10px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>Test Generation Results</h1>
"""
        
        if "pr_info" in result:
            pr = result["pr_info"]
            html += f"""
    <div class="section">
        <h2>PR Information</h2>
        <p><strong>Title:</strong> {pr.get('title')}</p>
        <p><strong>Author:</strong> {pr.get('author')}</p>
        <p><strong>Files Changed:</strong> {pr.get('changed_files')}</p>
    </div>
"""
        
        if "generated_tests" in result:
            html += """
    <div class="section">
        <h2>Generated Tests</h2>
"""
            for test in result["generated_tests"][:10]:
                html += f"""
        <div class="test-case">
            <h3>{test.get('name')}</h3>
            <p><strong>Function:</strong> {test.get('function')}</p>
            <pre>{test.get('code', '')[:300]}</pre>
        </div>
"""
            html += "    </div>"
        
        html += "\n</body>\n</html>"
        return html
    
    def cleanup_old_jobs(self, days: int = 7) -> int:
        """
        Delete jobs older than specified number of days
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of jobs deleted
        """
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days * 86400)
            
            deleted_count = 0
            
            for job_file in self.jobs_dir.glob("*.json"):
                if job_file.stat().st_mtime < cutoff_time:
                    job_id = job_file.stem
                    if self.delete_job(job_id):
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old jobs")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up jobs: {str(e)}")
            return 0
