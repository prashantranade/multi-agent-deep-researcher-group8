# Strategic Multi-Agent Deep Researcher

A production-ready, decoupled deep research platform. It deploys stateful groups of autonomous agents to discover web resources, perform semantic analysis, and compile market-ready reports.

## Architecture
- **Backend**: Python FastAPI REST server that runs compiled stateful **LangGraph** workflows in background threads.
- **Frontend**: A minimalist, light-mode **Next.js & React** dashboard with step-by-step guided intake wizards, execution progress tracking, and professional document rendering.

---

## Prerequisites
Before running the application, ensure you have the following installed:
1. **Python** (version 3.11 or higher)
2. **Node.js** (version 18 or higher) and **npm**

---

## 1. Environment Configuration

Create a `.env.local` file in the root of the project and add your API keys:

```ini
OPENROUTER_API_KEY=your_openrouter_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

---

## 2. Running the FastAPI Backend

### Setup & Installation
Activate your Python virtual environment and install dependencies:
```bash
# If using venv:
python -m venv .venv
source .venv/bin/activate  # On Linux/macOS
.venv\Scripts\activate.bat # On Windows CommandLine
.venv\Scripts\Activate.ps1 # On Windows PowerShell

# Install packages
pip install -r requirements.txt
```

### Start Backend
Run the backend web server on port 8000:
```bash
uvicorn api:app --reload --port 8000
```
- The API endpoints will be running at `http://localhost:8000`.
- You can explore the interactive API docs at `http://localhost:8000/docs`.

### Stop Backend
To stop the backend server, return to the terminal where it is running and press:
```
Ctrl + C
```

---

## 3. Running the Next.js Frontend

### Setup & Installation
Navigate into the `/frontend` directory and install npm packages:
```bash
cd frontend
npm install
```

### Start Frontend
Run the frontend development server on port 3000:
```bash
npm run dev
```
- The web application will be accessible at **`http://localhost:3000`**.

### Stop Frontend
To stop the frontend dev server, return to the terminal where it is running and press:
```
Ctrl + C
```

---

## 4. Verification & Testing

### Running Backend Tests
Ensure the backend agents and endpoints are functioning correctly:
```bash
pytest
```

### Building the Frontend for Production
Verify that the Next.js frontend compiles cleanly:
```bash
cd frontend
npm run build
```
