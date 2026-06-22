# rePaper-

## Small Mathematical Calculator Agent

This branch contains a simple FastAPI calculator agent.

The agent flow is:

1. Take user input.
2. Understand the mathematical task.
3. Choose the calculator tool.
4. Execute the calculation.
5. Return the answer.

Example:

```text
User: calculate 20% of 8500
Agent: I need percentage calculation
Answer: 1700
Tool: calculator
```

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload --port 8001
```

Open:

```text
http://localhost:8001
```

On Windows PowerShell, use:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload --port 8001
```

## API

```bash
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{"query":"calculate 20% of 8500"}'
```

Response:

```json
{
  "input": "calculate 20% of 8500",
  "task": "I need percentage calculation",
  "tool": "calculator",
  "answer": "1700",
  "expression": "20% of 8500"
}
```

## Test

```bash
python -m pytest
```
