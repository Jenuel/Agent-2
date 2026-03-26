# GitHub Repo Evaluator Agent 🚀

A powerful, automated tool that evaluates GitHub repositories using a multi-agent system powered by **LangGraph** and **Google Gemini**. It analyzes git commit history, project architecture, test coverage, and documentation to provide a comprehensive evaluation score and hiring recommendation.

## 🛠️ Tech Stack

- **Backend**: Python 3.x, FastAPI
- **AI/LLM**: Google Gemini and OpenAI (swappable via abstraction layer)
- **Workflow**: LangGraph (Decision nodes and agent coordination)
- **Git Analysis**: GitPython
- **Data Persistence**: JSON Reports
- **Utilities**: python-dotenv, HTTPX, Logger

## 🌟 Key Features

- **Automated Repository Cloning**: Clones public GitHub repositories for deep analysis.
- **Git History Evaluation**: Analyzes commit messages for quality, frequency, and meaningfulness.
- **Architecture Detection**: Identifies common patterns (MVC, Hexagonal, Layered, etc.) and evaluates their implementation.
- **Test Coverage Analysis**: Detects tests and evaluates their thoroughness.
- **AI-Powered Recommendation**: Generates a senior recruiter-style hiring recommendation based on the combined metrics.
- **Parallel Analysis**: Uses LangGraph to run multiple evaluation agents concurrently.
- **Resilient AI Pipeline**: Implements automatic retries for LLM calls to handle rate limits and transient errors.

## 📁 Project Structure

```text
├── app/
│   ├── backend/             # Primary FastAPI Server
│   │   ├── app/
│   │   │   ├── agents/      # LLM Agents for specialized analysis
│   │   │   ├── services/    # External service integrations (GitHub)
│   │   │   ├── main.py      # Entry point for the FastAPI API
│   │   │   ├── evaluator.py # LangGraph workflow definition
│   │   │   ├── logger.py    # Standardized logging setup
│   │   │   └── ...          # Utilities for retry and reporting
│   │   ├── reports/         # Generated evaluation reports (JSON)
│   │   ├── .env             # Configuration (API Keys)
│   │   └── requirements.txt # Project dependencies
│   └── frontend/            # (Future) Web interface for evaluations
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A Google Gemini API Key

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/github-repo-evaluator.git
   cd github-repo-evaluator
   ```

2. **Set up a Virtual Environment**:
   ```bash
   cd app/backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in `app/backend/`:
   ```env
   # Choose your provider: 'gemini' or 'openai' (default: gemini)
   LLM_PROVIDER=gemini
   
   # For Gemini:
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL_ID=gemini-2.5-flash
   
   # For OpenAI:
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL_ID=gpt-4o-mini
   ```

### Running the API

```bash
uvicorn app.main:app --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

## 📡 API Endpoints

### `GET /`
Health-check endpoint to verify if the API is running.

**Example Curl:**
```bash
curl -X GET "http://localhost:8000/"
```

### `POST /evaluate`
Evaluates a user's GitHub repositories.

**Request Body:**
```json
{
  "github_url": "https://github.com/username"
}
```

**Example Curl:**
```bash
curl -X POST "http://localhost:8000/evaluate?github_url=https://github.com/octocat"
```

## 🔄 Evaluation Pipeline (LangGraph)

The system uses a directed graph to process repository evaluations:

1. **Clone Node**: Clones the repo and performs initial structural analysis.
2. **Parallel Analysis**:
   - **Git Agent**: Runs git commit quality checks.
   - **Arch Agent**: Investigates project architecture.
   - **Test Agent**: Scans for test suites and coverage.
3. **Compile Node**: Aggregates scores from all analysis agents.
4. **Recommend Node**: Passes the final report to the LLM to generate a plain-English hiring recommendation.

## ⚠️ Known Limitations

> **Note**: When utilizing the Gemini free tier, due to request-per-minute (RPM) and daily quota constraints, evaluations on large repositories with many files may occasionally be incomplete or face `429` errors. Switching the `LLM_PROVIDER` to `openai` is recommended for more robust, high-throughput analysis.

## 🛠️ Future Improvements

- [ ] **Code Cleaning**: 
  - Refactor agents into a more modular plugin system. 
  - Improve error handling for edge cases (e.g., massive repos, non-standard project structures).
  - Add unit tests for the evaluation logic.
- [ ] **Frontend Application**: Build a React/Next.js dashboard to visualize the evaluation scores and repo statistics.
- [ ] **PDF Export**: Generate professional PDF reports using `reportlab`.
- [ ] **CI/CD Depth**: Add analysis for `.github/workflows` to evaluate CI/CD maturity.
- [ ] **Deep Code Linting**: Integrate static analysis tools to provide more objective code quality scores beyond LLM intuition.