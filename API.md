# API Reference

Complete API reference for the LLM Regression Suite Generator backend.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

Most endpoints don't require authentication, but GitHub operations may require a token.

**GitHub Token Header:**
```
Authorization: token ghp_YOUR_TOKEN_HERE
```

## Endpoints

### Health & Information

#### Health Check
```
GET /health
```

Check if the backend is running and all services are healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "services": {
    "github": "ready",
    "llm": "ready",
    "storage": "ready"
  }
}
```

**Status Codes:**
- `200` - All systems operational
- `503` - One or more services down

---

#### Get Configuration
```
GET /api/v1/config
```

Get available LLM providers, test frameworks, and supported languages.

**Response:**
```json
{
  "llm_providers": [
    {
      "name": "openai",
      "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
      "env_var": "OPENAI_API_KEY",
      "configured": true
    },
    {
      "name": "gemini",
      "models": ["gemini-pro", "gemini-pro-vision"],
      "env_var": "GEMINI_API_KEY",
      "configured": false
    }
  ],
  "test_frameworks": [
    {
      "name": "pytest",
      "language": "python"
    },
    {
      "name": "unittest",
      "language": "python"
    },
    {
      "name": "jest",
      "language": "javascript"
    },
    {
      "name": "junit",
      "language": "java"
    }
  ],
  "supported_languages": [
    "python",
    "javascript",
    "java",
    "typescript"
  ]
}
```

---

### PR Analysis

#### Analyze GitHub PR
```
POST /api/v1/analyze-pr
```

Analyze a GitHub PR and extract code changes without generating tests.

**Request Body:**
```json
{
  "github_url": "https://github.com/owner/repo/pull/123",
  "github_token": "ghp_optional-token"
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `github_url` | string | Yes | GitHub PR URL |
| `github_token` | string | No | GitHub personal access token |

**Response:**
```json
{
  "status": "success",
  "pr_info": {
    "number": 123,
    "title": "Add user authentication",
    "description": "Implements OAuth2 authentication",
    "author": "octocat",
    "created_at": "2024-01-10T12:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z",
    "state": "open",
    "commits": 3,
    "additions": 245,
    "deletions": 67,
    "changed_files": 8,
    "labels": ["feature", "authentication"],
    "html_url": "https://github.com/owner/repo/pull/123"
  },
  "code_analysis": {
    "changed_files": {
      "auth/login.py": {
        "path": "auth/login.py",
        "added_lines": [...],
        "removed_lines": [...],
        "language": "python",
        "changes": [...]
      }
    },
    "changed_functions": [
      {
        "name": "authenticate_user",
        "file": "auth/login.py",
        "language": "python",
        "type": "function",
        "code": "...",
        "parameters": ["username", "password"],
        "return_type": "User"
      }
    ]
  },
  "diff_summary": {
    "total_files": 8,
    "additions": 245,
    "deletions": 67,
    "changed_functions": 5
  }
}
```

**Status Codes:**
- `200` - Analysis successful
- `400` - Invalid GitHub URL
- `401` - Unauthorized (invalid token)
- `404` - Repository or PR not found
- `500` - Server error

---

### Test Generation

#### Generate Regression Tests
```
POST /api/v1/generate-tests
```

Generate regression tests for a GitHub PR (asynchronous operation).

**Request Body:**
```json
{
  "github_url": "https://github.com/owner/repo/pull/123",
  "github_token": "ghp_optional-token",
  "llm_provider": "openai",
  "llm_api_key": "optional-if-set-in-env",
  "test_framework": "pytest",
  "output_format": "pytest"
}
```

**Parameters:**
| Parameter | Type | Required | Options | Description |
|-----------|------|----------|---------|-------------|
| `github_url` | string | Yes | - | GitHub PR URL |
| `github_token` | string | No | - | GitHub personal access token |
| `llm_provider` | string | No | openai, gemini | LLM provider (default: openai) |
| `llm_api_key` | string | No | - | LLM API key (use env if not provided) |
| `test_framework` | string | No | pytest, unittest, jest, junit | Test framework (default: pytest) |
| `output_format` | string | No | pytest, unittest, jest | Output format |

**Response:**
```json
{
  "status": "accepted",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Test generation job queued. Check status with job_id"
}
```

**Status Codes:**
- `200` - Job created successfully
- `400` - Invalid request parameters
- `500` - Server error

**Note:** This is an asynchronous endpoint. Use the returned `job_id` to poll for results.

---

### Job Status

#### Get Job Status
```
GET /api/v1/jobs/{job_id}
```

Get the status and results of a test generation job.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | string (UUID) | Job identifier returned from generate-tests |

**Response (In Progress):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45
}
```

**Response (Completed):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "result": {
    "pr_info": {...},
    "code_analysis": {...},
    "generated_tests": [...],
    "test_summary": {
      "total_tests_generated": 12,
      "functions_covered": 3,
      "framework": "pytest"
    },
    "timestamp": "2024-01-15T10:45:00Z"
  }
}
```

**Response (Failed):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "progress": 0,
  "error": "Invalid API key for LLM provider"
}
```

**Status Values:**
- `processing` - Job is still running
- `completed` - Job finished successfully
- `failed` - Job encountered an error

**Status Codes:**
- `200` - Status retrieved successfully
- `404` - Job not found
- `500` - Server error

---

#### Get Generated Tests
```
GET /api/v1/jobs/{job_id}/tests
```

Get the generated test cases for a completed job.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | string (UUID) | Job identifier |

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "generated_tests": [
    {
      "id": "authenticate_user_test_0",
      "name": "test_authenticate_user_0",
      "function": "authenticate_user",
      "file": "auth/login.py",
      "framework": "pytest",
      "language": "python",
      "code": "def test_authenticate_user_happy_path():\n    result = authenticate_user('user@example.com', 'password123')\n    assert result is not None\n    assert result.username == 'user@example.com'",
      "type": "regression",
      "priority": "high",
      "description": "Regression test 1 for authenticate_user()",
      "tags": ["regression", "authenticate_user", "pytest"]
    },
    {
      "id": "authenticate_user_test_1",
      "name": "test_authenticate_user_1",
      "function": "authenticate_user",
      "file": "auth/login.py",
      "framework": "pytest",
      "language": "python",
      "code": "def test_authenticate_user_invalid_credentials():\n    with pytest.raises(AuthenticationError):\n        authenticate_user('user@example.com', 'wrongpassword')",
      "type": "regression",
      "priority": "high",
      "description": "Regression test 2 for authenticate_user()",
      "tags": ["regression", "authenticate_user", "pytest"]
    }
  ],
  "test_summary": {
    "total_tests_generated": 12,
    "functions_covered": 3,
    "framework": "pytest"
  }
}
```

**Status Codes:**
- `200` - Tests retrieved successfully
- `404` - Job not found or not completed
- `500` - Server error

---

## Error Handling

All error responses follow this format:

```json
{
  "error": "Error message describing what went wrong",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Common Error Codes

| Code | Message | Solution |
|------|---------|----------|
| `400` | Invalid GitHub PR URL | Check URL format: `https://github.com/owner/repo/pull/123` |
| `400` | Missing API key | Set LLM API key in environment or request body |
| `401` | Unauthorized | Invalid GitHub token or API key |
| `404` | Job not found | Check job_id is correct |
| `404` | Repository not found | Repository is private or doesn't exist |
| `429` | Rate limited | Wait before making next request |
| `500` | Internal server error | Check backend logs for details |
| `503` | Service unavailable | LLM provider is down or unreachable |

---

## Rate Limiting

Currently, no strict rate limiting is implemented. However:
- Keep requests to reasonable frequency
- Avoid sending duplicate requests for the same PR
- Respect external API rate limits (OpenAI, Gemini, GitHub)

---

## Examples

### cURL Examples

**Analyze a PR:**
```bash
curl -X POST http://localhost:8000/api/v1/analyze-pr \
  -H "Content-Type: application/json" \
  -d '{
    "github_url": "https://github.com/django/django/pull/16826"
  }'
```

**Generate Tests:**
```bash
curl -X POST http://localhost:8000/api/v1/generate-tests \
  -H "Content-Type: application/json" \
  -d '{
    "github_url": "https://github.com/django/django/pull/16826",
    "llm_provider": "openai",
    "llm_api_key": "sk-your-key",
    "test_framework": "pytest"
  }'
```

**Check Job Status:**
```bash
curl http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000
```

**Get Generated Tests:**
```bash
curl http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000/tests
```

### Python Examples

```python
import requests

BASE_URL = "http://localhost:8000"

# Generate tests
response = requests.post(
    f"{BASE_URL}/api/v1/generate-tests",
    json={
        "github_url": "https://github.com/django/django/pull/16826",
        "llm_provider": "openai",
        "llm_api_key": "sk-your-key",
        "test_framework": "pytest"
    }
)

job_id = response.json()["job_id"]

# Poll for results
import time
while True:
    status_response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}")
    status = status_response.json()
    
    if status["status"] in ["completed", "failed"]:
        print(f"Job {status['status']}!")
        if status["status"] == "completed":
            print(f"Generated {len(status['result']['generated_tests'])} tests")
        break
    
    print(f"Progress: {status['progress']}%")
    time.sleep(2)
```

### JavaScript Examples

```javascript
const BASE_URL = "http://localhost:8000";

async function generateTests() {
  const response = await fetch(`${BASE_URL}/api/v1/generate-tests`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      github_url: "https://github.com/django/django/pull/16826",
      llm_provider: "openai",
      llm_api_key: "sk-your-key",
      test_framework: "pytest"
    })
  });

  const { job_id } = await response.json();

  // Poll for results
  while (true) {
    const statusResponse = await fetch(`${BASE_URL}/api/v1/jobs/${job_id}`);
    const status = await statusResponse.json();

    console.log(`Progress: ${status.progress}%`);

    if (status.status !== "processing") {
      console.log(`Job ${status.status}`);
      return status.result;
    }

    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}
```

---

## WebSocket Support (Future)

Real-time job status updates via WebSocket (planned for v2.0):

```javascript
const ws = new WebSocket("ws://localhost:8000/api/v1/jobs/{job_id}/stream");

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log(`Progress: ${update.progress}%`);
  
  if (update.status === "completed") {
    console.log("Tests ready:", update.result);
    ws.close();
  }
};
```

---

## Changelog

### Version 1.0.0 (Current)
- Initial release
- Support for GPT-4 and Gemini
- Multiple test frameworks
- Job status tracking
- Export functionality

---

Need help? Check the [main README](README.md) or open an issue on GitHub!
