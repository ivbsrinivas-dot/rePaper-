from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.agent import AgentResponse, run_calculator_agent
from app.calculator import CalculatorError


app = FastAPI(title="Mathematical Calculator Agent")


class AgentRequest(BaseModel):
    query: str


class ErrorResponse(BaseModel):
    error: str


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Calculator Agent</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f7f7f2;
      color: #202124;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 32px;
    }
    main {
      width: min(760px, 100%);
      background: #ffffff;
      border: 1px solid #deded6;
      border-radius: 8px;
      box-shadow: 0 20px 60px rgba(32, 33, 36, 0.10);
      padding: 28px;
    }
    h1 {
      margin: 0 0 8px;
      font-size: clamp(1.8rem, 4vw, 2.4rem);
      line-height: 1.1;
      letter-spacing: 0;
    }
    p {
      margin: 0 0 24px;
      color: #5f6368;
      line-height: 1.5;
    }
    form {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 12px;
      margin-bottom: 20px;
    }
    input {
      min-width: 0;
      min-height: 48px;
      border: 1px solid #c8c8c0;
      border-radius: 8px;
      padding: 0 14px;
      font-size: 1rem;
    }
    button {
      min-height: 48px;
      border: 0;
      border-radius: 8px;
      padding: 0 18px;
      background: #146c5f;
      color: white;
      font-weight: 700;
      cursor: pointer;
    }
    button:disabled {
      opacity: 0.65;
      cursor: wait;
    }
    .result {
      display: grid;
      gap: 12px;
      border-top: 1px solid #e7e7de;
      padding-top: 20px;
    }
    .row {
      display: grid;
      grid-template-columns: 140px 1fr;
      gap: 16px;
      align-items: start;
    }
    .label {
      color: #6b6f76;
      font-weight: 700;
    }
    .answer {
      font-size: 2rem;
      font-weight: 800;
      color: #174ea6;
      overflow-wrap: anywhere;
    }
    .error {
      color: #b3261e;
      font-weight: 700;
    }
    @media (max-width: 620px) {
      body { padding: 16px; }
      main { padding: 20px; }
      form { grid-template-columns: 1fr; }
      .row { grid-template-columns: 1fr; gap: 4px; }
    }
  </style>
</head>
<body>
  <main>
    <h1>Calculator Agent</h1>
    <p>Ask a small math question. The agent identifies the task, chooses the calculator tool, and returns the answer.</p>
    <form id="agent-form">
      <input id="query" name="query" value="calculate 20% of 8500" autocomplete="off" aria-label="Math question">
      <button id="submit" type="submit">Run</button>
    </form>
    <section class="result" aria-live="polite">
      <div class="row"><div class="label">Task</div><div id="task">I need percentage calculation</div></div>
      <div class="row"><div class="label">Answer</div><div id="answer" class="answer">1700</div></div>
      <div class="row"><div class="label">Tool</div><div id="tool">calculator</div></div>
      <div class="row"><div class="label">Expression</div><div id="expression">20% of 8500</div></div>
    </section>
  </main>
  <script>
    const form = document.querySelector("#agent-form");
    const button = document.querySelector("#submit");
    const fields = {
      task: document.querySelector("#task"),
      answer: document.querySelector("#answer"),
      tool: document.querySelector("#tool"),
      expression: document.querySelector("#expression")
    };

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      button.disabled = true;
      fields.answer.classList.remove("error");
      try {
        const response = await fetch("/agent", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: new FormData(form).get("query") })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Calculation failed");
        fields.task.textContent = data.task;
        fields.answer.textContent = data.answer;
        fields.tool.textContent = data.tool;
        fields.expression.textContent = data.expression;
      } catch (error) {
        fields.task.textContent = "I could not complete the calculation";
        fields.answer.textContent = error.message;
        fields.answer.classList.add("error");
        fields.tool.textContent = "calculator";
        fields.expression.textContent = "-";
      } finally {
        button.disabled = false;
      }
    });
  </script>
</body>
</html>
"""


@app.post("/agent", response_model=AgentResponse, responses={400: {"model": ErrorResponse}})
def run_agent(request: AgentRequest) -> AgentResponse:
    try:
        return run_calculator_agent(request.query)
    except CalculatorError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
