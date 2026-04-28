# Setup & Installation Guide

Complete step-by-step guide to get the LLM Regression Suite Generator up and running.

## Prerequisites

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)
- API Keys (choose at least one):
  - OpenAI API key - [Get it](https://platform.openai.com/api-keys)
  - Google Gemini API key - [Get it](https://ai.google.dev)
  - GitHub token (optional) - [Create](https://github.com/settings/tokens)

## Step 1: Clone the Repository

```bash
git clone https://github.com/sreenijaearanki/LLM-Powered-Regression-Suite-Generator.git
cd LLM-Powered-Regression-Suite-Generator
```

## Step 2: Backend Setup

### 2.1 Create Python Virtual Environment

```bash
cd backend

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 2.2 Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2.3 Set Up Environment Variables

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Choose at least one LLM provider
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here

# Optional: GitHub token for private repositories
GITHUB_TOKEN=ghp_your-github-token-here

# Server configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Storage
STORAGE_DIR=/tmp/llm_regression_storage
```

### 2.4 Create Required Directories

```bash
# Create empty __init__.py files for Python packages
touch services/__init__.py
touch database/__init__.py
```

### 2.5 Run Backend Server

```bash
# Using uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Or directly
python main.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**API Documentation**: Open http://localhost:8000/docs in your browser

## Step 3: Frontend Setup

### 3.1 Navigate to Frontend Directory

```bash
cd ../frontend
```

### 3.2 Install Node Dependencies

```bash
npm install
```

### 3.3 Configure Environment (Optional)

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

### 3.4 Run Development Server

```bash
npm run dev
```

**Expected output:**
```
  VITE v5.0.0  ready in 234 ms

  ➜  Local:   http://localhost:3000/
  ➜  press h to show help
```

**Access the application**: Open http://localhost:3000 in your browser

## Step 4: Verify Installation

### 4.1 Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
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

### 4.2 Frontend Verification

1. Open http://localhost:3000
2. You should see the home page with "LLM-Powered Regression Suite Generator" title
3. Try entering a test GitHub PR URL

## Step 5: Test the Application

### Manual Testing

1. **Test PR URL**: Use a public GitHub PR
   ```
   https://github.com/django/django/pull/16826
   ```

2. **Fill in the form**:
   - GitHub URL: (paste the PR URL above)
   - LLM Provider: OpenAI
   - API Key: (paste your actual API key)
   - Test Framework: pytest
   - Click "Generate Tests"

3. **Monitor Progress**: You should see real-time progress updates

4. **View Results**: Once complete, you can download or view the generated tests

### Automated Testing (Backend)

```bash
cd backend

# Run unit tests (if available)
pytest tests/

# Test API endpoint
curl -X POST http://localhost:8000/api/v1/analyze-pr \
  -H "Content-Type: application/json" \
  -d '{
    "github_url": "https://github.com/django/django/pull/16826"
  }'
```

## Troubleshooting

### Python Issues

**Error: "python: command not found"**
```bash
# Use python3
python3 --version
# Or add alias
alias python=python3
```

**Error: "No module named 'fastapi'"**
```bash
# Ensure venv is activated
source venv/bin/activate  # macOS/Linux
# Then reinstall
pip install -r requirements.txt
```

### Node Issues

**Error: "npm: command not found"**
- Reinstall Node.js from https://nodejs.org/

**Error: "VITE v4.0.0 ready"** but can't access localhost:3000
```bash
# Kill process on port 3000
# macOS/Linux
lsof -ti:3000 | xargs kill -9

# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### API Issues

**Error: "Invalid API key"**
1. Verify key in `.env` file
2. Check key format (shouldn't have spaces)
3. Verify key is active on provider's website
4. Restart backend server

**Error: "Connection refused on port 8000"**
1. Ensure backend server is running
2. Check if port 8000 is available
3. Try different port: `uvicorn main:app --port 8001`

**Error: "CORS error in browser console"**
1. Check backend CORS configuration in main.py
2. Verify frontend URL is in allowed origins
3. Restart both servers

### GitHub Integration Issues

**Error: "Invalid GitHub PR URL"**
- Ensure URL format: `https://github.com/owner/repo/pull/123`
- URL must include `/pull/`
- PR number must be a valid integer

**Error: "404 Not Found" for private repo**
1. Generate GitHub personal access token
2. Add token to form or environment
3. Ensure token has `repo` scope

## Production Deployment

### Using Docker

**1. Create Dockerfile for Backend**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. Create Dockerfile for Frontend**

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**3. Docker Compose**

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

**Run:**
```bash
docker-compose up
```

### Cloud Platforms

**AWS EC2:**
```bash
# SSH into instance
ssh -i key.pem ubuntu@instance-ip

# Install dependencies
sudo apt update && sudo apt install python3 python3-venv nodejs npm

# Clone and setup
git clone <repo>
cd LLM-Powered-Regression-Suite-Generator
# ... follow setup steps

# Use screen or tmux to keep services running
screen -S backend
# Run backend

screen -S frontend
# Run frontend
```

**Heroku:**
```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Create app
heroku create your-app-name

# Set config vars
heroku config:set OPENAI_API_KEY=your-key
heroku config:set GEMINI_API_KEY=your-key

# Deploy
git push heroku main
```

## Next Steps

1. ✅ Start generating tests!
2. 📖 Read the [API Reference](API.md)
3. 💡 Check out [Examples](EXAMPLES.md)
4. 🐛 Report issues on [GitHub Issues](https://github.com/sreenijaearanki/LLM-Powered-Regression-Suite-Generator/issues)

## Support

- **Documentation**: See README.md
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

Need help? Check the [FAQ](README.md#faq) or open an issue!
