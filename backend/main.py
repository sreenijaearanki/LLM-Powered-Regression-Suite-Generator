"""
LLM-Powered Regression Suite Generator - Backend API
Main FastAPI application for generating regression tests from GitHub PRs
"""

import os
import json
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import logging
from datetime import datetime
from pydantic import BaseModel

# Import service modules
from services.github_service import GitHubService
from services.llm_service import LLMService
from services.test_generator import TestGenerator
from services.code_analyzer import CodeAnalyzer
from database.storage import StorageManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LLM Regression Suite Generator",
    description="Automatically generate regression tests from GitHub PRs using LLMs",
    version="1.0.0"
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://sreenijaearanki.github.io", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
github_service = GitHubService()
llm_service = LLMService()
test_generator = TestGenerator()
code_analyzer = CodeAnalyzer()
storage_manager = StorageManager()

# ============================================================================
# Pydantic Models
# ============================================================================

class PRAnalysisRequest(BaseModel):
    """Request model for PR analysis"""
    github_url: str
    github_token: Optional[str] = None
    llm_provider: str = "openai"  # "openai" or "gemini"
    llm_api_key: Optional[str] = None
    output_format: str = "pytest"  # "pytest", "unittest", "jest"
    test_framework: str = "pytest"

class TestGenerationResponse(BaseModel):
    """Response model for test generation"""
    job_id: str
    status: str
    pr_info: dict
    generated_tests: list
    code_analysis: dict
    timestamp: str
    
class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: str
    progress: int
    result: Optional[dict] = None
    error: Optional[str] = None

# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "LLM Regression Suite Generator",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "analyze_pr": "/api/v1/analyze-pr",
            "generate_tests": "/api/v1/generate-tests",
            "job_status": "/api/v1/jobs/{job_id}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    import os
    github_token = os.getenv("GITHUB_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "github_token_set": bool(github_token),
        "openai_key_set": bool(openai_key),
        "github_rate_limit": "5000/hr" if github_token else "60/hr - GITHUB_TOKEN not set!",
        "services": {
            "github": "authenticated" if github_token else "unauthenticated - set GITHUB_TOKEN",
            "llm": "ready" if openai_key else "missing OPENAI_API_KEY",
            "storage": "ready"
        }
    }

# ============================================================================
# PR Analysis Endpoints
# ============================================================================

@app.post("/api/v1/analyze-pr")
async def analyze_pr(request: PRAnalysisRequest):
    """
    Analyze a GitHub PR and extract code changes
    
    Args:
        request: PRAnalysisRequest with GitHub URL and credentials
        
    Returns:
        PR analysis with code changes identified
    """
    try:
        logger.info(f"Analyzing PR: {request.github_url}")
        
        # Parse GitHub URL
        pr_info = github_service.parse_pr_url(request.github_url)
        if not pr_info:
            raise HTTPException(status_code=400, detail="Invalid GitHub PR URL")
        
        # Fetch PR details from GitHub
        pr_details = await github_service.fetch_pr_details(
            owner=pr_info["owner"],
            repo=pr_info["repo"],
            pr_number=pr_info["pr_number"],
            token=request.github_token
        )
        
        # Get diff and changed files
        diff_data = await github_service.get_pr_diff(
            owner=pr_info["owner"],
            repo=pr_info["repo"],
            pr_number=pr_info["pr_number"],
            token=request.github_token
        )
        
        # Analyze code changes
        code_analysis = code_analyzer.analyze_changes(diff_data)
        
        logger.info(f"PR analysis complete. Changed files: {len(code_analysis['changed_files'])}")
        
        return {
            "status": "success",
            "pr_info": pr_details,
            "code_analysis": code_analysis,
            "diff_summary": {
                "total_files": len(code_analysis['changed_files']),
                "additions": code_analysis['stats']['additions'],
                "deletions": code_analysis['stats']['deletions'],
                "changed_functions": code_analysis['changed_functions']
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing PR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Test Generation Endpoints
# ============================================================================

@app.post("/api/v1/generate-tests")
async def generate_tests(request: PRAnalysisRequest, background_tasks: BackgroundTasks):
    """
    Generate regression tests for a GitHub PR
    
    This is an async endpoint that processes PR changes and generates tests
    using the specified LLM provider
    
    Args:
        request: PRAnalysisRequest with PR details and LLM configuration
        background_tasks: FastAPI background tasks for async processing
        
    Returns:
        Initial response with job_id for tracking
    """
    try:
        # Create job ID
        job_id = storage_manager.create_job_id()
        logger.info(f"Creating test generation job: {job_id}")
        
        # Store initial job status
        storage_manager.update_job_status(job_id, "processing", 10)
        
        # Add background task for actual test generation
        background_tasks.add_task(
            _generate_tests_background,
            job_id,
            request
        )
        
        return {
            "status": "accepted",
            "job_id": job_id,
            "message": "Test generation job queued. Check status with job_id"
        }
        
    except Exception as e:
        logger.error(f"Error initiating test generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _generate_tests_background(job_id: str, request: PRAnalysisRequest):
    """
    Background task for generating tests (runs asynchronously)
    
    Args:
        job_id: Unique identifier for this generation job
        request: Test generation request
    """
    try:
        storage_manager.update_job_status(job_id, "fetching_code", 20)
        
        # Parse and validate GitHub URL
        pr_info = github_service.parse_pr_url(request.github_url)
        if not pr_info:
            raise ValueError("Invalid GitHub PR URL")
        
        # Fetch PR details
        storage_manager.update_job_status(job_id, "analyzing_code", 30)
        pr_details = await github_service.fetch_pr_details(
            owner=pr_info["owner"],
            repo=pr_info["repo"],
            pr_number=pr_info["pr_number"],
            token=request.github_token
        )
        
        # Get code changes
        diff_data = await github_service.get_pr_diff(
            owner=pr_info["owner"],
            repo=pr_info["repo"],
            pr_number=pr_info["pr_number"],
            token=request.github_token
        )
        
        # Analyze code
        code_analysis = code_analyzer.analyze_changes(diff_data)
        
        storage_manager.update_job_status(job_id, "generating_tests", 50)
        
        # Initialize LLM service with the chosen provider
        llm_config = {
            "provider": request.llm_provider,
            "api_key": request.llm_api_key or os.getenv(
                f"{request.llm_provider.upper()}_API_KEY"
            )
        }
        
        llm_service.initialize(llm_config)
        
        # Generate tests for each changed function/method
        generated_tests = []
        llm_errors = []
        total_items = len(code_analysis['changed_functions'])

        for idx, func_info in enumerate(code_analysis['changed_functions']):
            progress = 50 + (idx / max(total_items, 1) * 40)
            storage_manager.update_job_status(job_id, "generating_tests", int(progress))

            try:
                tests = await test_generator.generate_tests(
                    function_info=func_info,
                    code_context=diff_data,
                    llm_service=llm_service,
                    framework=request.test_framework
                )
                generated_tests.extend(tests)
            except Exception as e:
                err_msg = str(e)
                logger.error(f"Error generating tests for {func_info.get('name')}: {err_msg}")
                llm_errors.append(err_msg)
                continue
        
        storage_manager.update_job_status(job_id, "formatting_output", 90)
        
        # Format and save results
        result = {
            "pr_info": pr_details,
            "code_analysis": code_analysis,
            "generated_tests": generated_tests,
            "test_summary": {
                "total_tests_generated": len(generated_tests),
                "functions_covered": len([t for t in generated_tests if t.get("function")]),
                "framework": request.test_framework
            },
            "llm_errors": llm_errors,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save result to storage
        storage_manager.save_job_result(job_id, result)
        
        storage_manager.update_job_status(job_id, "completed", 100)
        logger.info(f"Test generation completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Error in test generation background task: {str(e)}")
        storage_manager.update_job_status(job_id, "failed", 0, error=str(e))

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status of a test generation job
    
    Args:
        job_id: The unique job identifier
        
    Returns:
        Current job status and result (if completed)
    """
    try:
        status, progress, result, error = storage_manager.get_job_status(job_id)
        
        response = {
            "job_id": job_id,
            "status": status,
            "progress": progress
        }
        
        if result:
            response["result"] = result
        if error:
            response["error"] = error
            
        return response
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

@app.get("/api/v1/jobs/{job_id}/tests")
async def get_generated_tests(job_id: str):
    """
    Get the generated tests for a job
    
    Args:
        job_id: The unique job identifier
        
    Returns:
        List of generated test cases
    """
    try:
        _, _, result, _ = storage_manager.get_job_status(job_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Job not completed yet")
        
        return {
            "job_id": job_id,
            "generated_tests": result.get("generated_tests", []),
            "test_summary": result.get("test_summary", {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Configuration & Settings Endpoints
# ============================================================================

@app.get("/api/v1/config")
async def get_config():
    """Get current configuration and available providers"""
    return {
        "llm_providers": [
            {
                "name": "openai",
                "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "env_var": "OPENAI_API_KEY",
                "configured": bool(os.getenv("OPENAI_API_KEY"))
            },
            {
                "name": "gemini",
                "models": ["gemini-pro", "gemini-pro-vision"],
                "env_var": "GEMINI_API_KEY",
                "configured": bool(os.getenv("GEMINI_API_KEY"))
            }
        ],
        "test_frameworks": [
            {"name": "pytest", "language": "python"},
            {"name": "unittest", "language": "python"},
            {"name": "jest", "language": "javascript"},
            {"name": "junit", "language": "java"}
        ],
        "supported_languages": ["python", "javascript", "java", "typescript"]
    }

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
