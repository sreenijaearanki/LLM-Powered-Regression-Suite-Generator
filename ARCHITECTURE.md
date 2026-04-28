# Project Structure & Architecture

Complete overview of the LLM-Powered Regression Suite Generator project structure, components, and architecture.

## Directory Structure

```
llm-regression-suite-generator/
├── backend/                          # Python FastAPI Backend
│   ├── main.py                      # FastAPI application entry point
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                 # Environment variables template
│   │
│   ├── services/                     # Business logic services
│   │   ├── __init__.py
│   │   ├── github_service.py        # GitHub API integration
│   │   ├── llm_service.py           # LLM providers (OpenAI, Gemini)
│   │   ├── code_analyzer.py         # Code diff analysis & parsing
│   │   └── test_generator.py        # Test case generation logic
│   │
│   ├── database/                     # Data persistence layer
│   │   ├── __init__.py
│   │   └── storage.py               # File-based job storage
│   │
│   └── tests/                        # Unit tests (optional)
│       └── test_*.py
│
├── frontend/                         # React + Vite Frontend
│   ├── index.html                   # HTML entry point
│   ├── package.json                 # Node.js dependencies
│   ├── vite.config.js               # Vite configuration
│   ├── .env.example                 # Environment variables template
│   │
│   ├── src/
│   │   ├── index.jsx                # React DOM render
│   │   ├── App.jsx                  # Main App component
│   │   ├── App.css                  # Global styles
│   │   │
│   │   ├── pages/                   # Page components
│   │   │   ├── Home.jsx             # Landing page
│   │   │   ├── Dashboard.jsx        # Job management dashboard
│   │   │   ├── JobStatus.jsx        # Job progress tracking
│   │   │   └── Documentation.jsx    # Help documentation
│   │   │
│   │   ├── components/              # Reusable UI components
│   │   │   ├── Navbar.jsx           # Navigation bar
│   │   │   ├── PRForm.jsx           # GitHub PR input form
│   │   │   ├── JobCard.jsx          # Job display card
│   │   │   ├── TestsList.jsx        # Test results list
│   │   │   ├── ProgressBar.jsx      # Progress indicator
│   │   │   ├── Features.jsx         # Feature highlights
│   │   │   └── ...
│   │   │
│   │   ├── styles/                  # CSS stylesheets
│   │   │   ├── Home.css
│   │   │   ├── Dashboard.css
│   │   │   ├── JobStatus.css
│   │   │   ├── Documentation.css
│   │   │   └── PRForm.css
│   │   │
│   │   └── utils/                   # Utility functions
│   │       ├── api.js               # API client
│   │       └── helpers.js           # Helper functions
│   │
│   └── dist/                        # Build output (after npm run build)
│
├── docs/                             # Documentation files
│   ├── SETUP.md                     # Setup & installation guide
│   ├── API.md                       # API reference
│   ├── EXAMPLES.md                  # Usage examples
│   └── ARCHITECTURE.md              # This file
│
├── docker-compose.yml               # Docker Compose configuration
├── Dockerfile                        # Docker image definition
│
├── .github/
│   └── workflows/                   # GitHub Actions CI/CD
│       ├── tests.yml
│       ├── deploy.yml
│       └── ...
│
├── README.md                         # Project README
├── LICENSE                           # MIT License
└── .gitignore                        # Git ignore rules
```

## Backend Architecture

### Core Components

#### 1. **main.py** - FastAPI Application
The main entry point that sets up:
- FastAPI application instance
- CORS middleware for frontend communication
- Route handlers (endpoints)
- Error handling
- Service initialization

**Key Endpoints:**
```
GET     /                          # API info
GET     /health                    # Health check
POST    /api/v1/analyze-pr         # Analyze PR
POST    /api/v1/generate-tests     # Generate tests (async)
GET     /api/v1/jobs/{job_id}      # Get job status
GET     /api/v1/jobs/{job_id}/tests # Get generated tests
GET     /api/v1/config             # Get configuration
```

#### 2. **services/github_service.py** - GitHub Integration
Handles all GitHub API interactions:

**Key Methods:**
- `parse_pr_url()` - Extract owner/repo/PR number from URL
- `fetch_pr_details()` - Get PR metadata (title, author, stats)
- `get_pr_diff()` - Fetch unified diff for PR
- `get_pr_files()` - List changed files
- `get_file_content()` - Fetch file from repo
- `get_commits()` - Get commit history

**Features:**
- Async HTTP requests with httpx
- GitHub API authentication
- Error handling and logging

#### 3. **services/llm_service.py** - LLM Provider Integration
Manages LLM provider abstraction:

**Providers:**
- **OpenAIProvider** - GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **GeminiProvider** - Google's Gemini models

**Key Methods:**
- `initialize()` - Set up LLM provider
- `generate_tests()` - Generate test code via LLM
- `analyze_code()` - Code analysis using LLM

**Features:**
- Provider-agnostic interface
- Configurable temperature and tokens
- System prompts for consistent output
- Error handling and fallbacks

#### 4. **services/code_analyzer.py** - Code Analysis
Analyzes code changes and extracts testing requirements:

**Key Methods:**
- `analyze_changes()` - Parse diff and identify changes
- `_parse_diff()` - Parse unified diff format
- `_detect_language()` - Detect programming language
- `_extract_changed_functions()` - Find modified functions
- `_extract_parameters()` - Get function parameters
- `_extract_return_type()` - Determine return types

**Supports:**
- Python, JavaScript, TypeScript, Java
- Function/method extraction
- Class detection
- Type hint parsing

#### 5. **services/test_generator.py** - Test Generation
Creates regression tests using LLM output:

**Key Methods:**
- `generate_tests()` - Main test generation
- `_build_prompt()` - Create LLM prompt
- `_parse_generated_tests()` - Structure test output
- `format_test()` - Format for specific framework
- Template methods for each framework

**Test Frameworks:**
- pytest (Python)
- unittest (Python)
- Jest (JavaScript)
- JUnit (Java)

#### 6. **database/storage.py** - Data Persistence
Manages job storage and results:

**Key Methods:**
- `create_job_id()` - Generate unique ID
- `update_job_status()` - Update progress
- `save_job_result()` - Store final result
- `get_job_status()` - Retrieve job info
- `get_all_jobs()` - List all jobs
- `delete_job()` - Clean up job
- `export_results()` - Format results (JSON/MD/HTML)
- `cleanup_old_jobs()` - Remove old data

**Storage:**
- File-based (JSON)
- Location: `/tmp/llm_regression_storage`
- Can be extended to use databases

### Data Flow

```
User Input (PR URL)
        ↓
    Validate
        ↓
   GitHub Service (Fetch PR)
        ↓
   Code Analyzer (Parse changes)
        ↓
    LLM Service (Generate tests)
        ↓
   Test Generator (Format tests)
        ↓
   Storage (Save results)
        ↓
    JSON Response
```

### Async Processing

The `/api/v1/generate-tests` endpoint uses background tasks for long-running operations:

```python
# Client sends request
POST /api/v1/generate-tests
├── Backend creates job
├── Returns job_id immediately
└── Starts background task

# Background task
_generate_tests_background(job_id)
├── Updates status: 10%
├── Fetches PR details: 20%
├── Analyzes code: 30%
├── Generates tests: 50-90%
├── Formats output: 90%
└── Saves results: 100%

# Client polls for results
GET /api/v1/jobs/{job_id}
└── Returns current status & results
```

## Frontend Architecture

### Component Hierarchy

```
App
├── Navbar
│   └── Navigation buttons
├── Main Content Router
│   ├── Home
│   │   ├── PRForm
│   │   └── Features
│   ├── Dashboard
│   │   ├── FilterButtons
│   │   └── JobCard (list)
│   ├── JobStatus
│   │   ├── ProgressBar
│   │   ├── PRInfo
│   │   ├── TestSummary
│   │   └── TestsList
│   └── Documentation
│       └── DocTabs
└── Footer
```

### Page Components

#### 1. **Home.jsx**
Landing page with:
- Hero section
- PR input form (`PRForm`)
- Feature highlights (`Features`)
- Benefits section

#### 2. **Dashboard.jsx**
Job management interface:
- Filter buttons (all, completed, processing, failed)
- Job cards list
- Statistics (total, success rate, avg tests)
- Local storage integration

#### 3. **JobStatus.jsx**
Real-time job tracking:
- Progress bar
- PR information display
- Test summary
- Generated tests list
- Export functionality (JSON, MD, HTML)
- Real-time polling (2s interval)

#### 4. **Documentation.jsx**
Help documentation with tabs:
- Setup & Installation
- Usage Guide
- API Reference
- Examples
- FAQ

### Component Features

#### **PRForm.jsx**
Form component for test generation input:
- GitHub URL input with validation
- GitHub token field
- LLM provider selection
- API key input
- Test framework selection
- Error handling
- Loading states

#### **JobCard.jsx**
Displays job summary:
- Job ID (truncated)
- Status badge
- Progress percentage
- PR title
- Actions (view, delete)

#### **TestsList.jsx**
Displays generated tests:
- Test code with syntax highlighting
- Searchable/filterable
- Copy to clipboard
- Download individual tests

#### **ProgressBar.jsx**
Visual progress indicator:
- Percentage display
- Color-coded status
- Status text

### State Management

**Local State:**
- Page routing
- Form inputs
- Loading states
- Filters

**Local Storage:**
- Job history
- User preferences
- Generated results

**Backend State:**
- Job status
- Progress tracking
- Final results

### API Integration

**api.js** - HTTP client wrapper:

```javascript
// Endpoints
POST   /api/v1/generate-tests    → Generate tests
GET    /api/v1/jobs/{id}         → Get job status
GET    /api/v1/jobs/{id}/tests   → Get tests
POST   /api/v1/analyze-pr        → Analyze PR
GET    /api/v1/config            → Get configuration
```

## Technology Stack

### Backend
```
Python 3.10+
├── FastAPI          Web framework
├── Uvicorn          ASGI server
├── httpx            Async HTTP client
├── OpenAI SDK       GPT-4 integration
├── Google GenAI     Gemini integration
└── Pydantic         Data validation
```

### Frontend
```
Node.js 16+
├── React 18         UI library
├── Vite             Build tool
├── CSS3             Styling
└── Fetch API        HTTP requests
```

### Infrastructure
```
Docker              Container
Docker Compose      Orchestration
GitHub              Version control & Actions
```

## Data Models

### Job Model
```python
{
  "job_id": "uuid",
  "status": "processing|completed|failed",
  "progress": 0-100,
  "github_url": "https://...",
  "llm_provider": "openai|gemini",
  "test_framework": "pytest|jest|...",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp",
  "error": "optional error message"
}
```

### Result Model
```python
{
  "job_id": "uuid",
  "pr_info": {
    "number": int,
    "title": string,
    "author": string,
    "changes": int,
    ...
  },
  "code_analysis": {
    "changed_files": {...},
    "changed_functions": [...],
    "stats": {...}
  },
  "generated_tests": [
    {
      "id": string,
      "name": string,
      "function": string,
      "code": string,
      "framework": string,
      ...
    }
  ],
  "test_summary": {
    "total_tests_generated": int,
    "framework": string,
    "functions_covered": int
  }
}
```

## Processing Flow

### Test Generation Pipeline

```
1. User Input
   └─ GitHub URL, LLM provider, framework

2. GitHub Integration
   ├─ Parse URL
   ├─ Fetch PR details
   ├─ Get code diff
   └─ Retrieve file contents

3. Code Analysis
   ├─ Parse diff format
   ├─ Identify changed files
   ├─ Extract functions/classes
   ├─ Detect programming language
   └─ Build context

4. LLM Processing
   ├─ Build test prompt
   ├─ Call LLM API
   ├─ Parse response
   └─ Extract test code

5. Test Formatting
   ├─ Apply framework conventions
   ├─ Add assertions
   ├─ Include docstrings
   └─ Format code

6. Storage & Results
   ├─ Save job metadata
   ├─ Store generated tests
   ├─ Export in multiple formats
   └─ Return to user
```

## Performance Considerations

### Backend
- **Async I/O**: Non-blocking API calls
- **Background Jobs**: Long-running tasks don't block responses
- **Polling**: Client-side polling for job status
- **Caching**: Could add for repeated PRs

### Frontend
- **Lazy Loading**: Load components on demand
- **Local Storage**: Cache job history locally
- **Real-time Updates**: 2-second polling interval
- **Optimized Assets**: CSS/JS minification with Vite

## Security

### API Security
- CORS configured for specific origins
- No persistent storage of sensitive data
- Environment variables for API keys
- Rate limiting (can be added)

### Data Privacy
- PR code analyzed locally
- No external logging of code
- Optional data retention policies
- User-controlled data export

## Extensibility

### Add New LLM Provider

1. Create new provider class in `llm_service.py`
```python
class NewProvider(LLMProvider):
    async def generate_completion(self, prompt, **kwargs):
        # Implementation
```

2. Register in `LLMService.initialize()`

### Add New Test Framework

1. Add template in `test_generator.py`
2. Implement format method
3. Update config endpoint
4. Add to frontend selector

### Add New Language Support

1. Add language patterns to `code_analyzer.py`
2. Create extraction methods
3. Update language detection

## Monitoring & Logging

### Logging Setup
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Metrics to Track
- Job success rate
- Average generation time
- API latency
- Error frequency

## Deployment Targets

### Development
```bash
python main.py
npm run dev
```

### Production
- Docker containers
- Cloud platforms (AWS, GCP, Azure)
- Kubernetes orchestration
- CI/CD pipelines (GitHub Actions)

## Future Enhancements

- [ ] Database integration (PostgreSQL)
- [ ] User authentication
- [ ] Team collaboration
- [ ] Custom templates
- [ ] Batch processing
- [ ] CI/CD integration
- [ ] Webhook support
- [ ] Advanced analytics
- [ ] Performance optimization
- [ ] Multi-language support (UI)

---

For deployment and setup details, see [SETUP.md](SETUP.md)
For API details, see [API.md](API.md)
