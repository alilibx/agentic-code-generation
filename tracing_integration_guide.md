# Comprehensive Tracing Integration Guide (Azure AI Foundry + Application Insights + OpenTelemetry)

This guide explains how to enable and analyze distributed tracing using **Azure AI Foundry** or directly via **Azure Application Insights**, including **KQL (Kusto Query Language)** examples for custom telemetry analysis. It also aligns with the provided TelemetryManager and Evaluations utilities.

---

## 🔹 1. Overview
Tracing provides deep visibility into your GenAI workloads — including latency, token usage, evaluator scores, and multi-agent interactions — by correlating spans emitted by OpenTelemetry with Azure Monitor or Application Insights.

There are **two main setups**:
1. **Using Azure AI Foundry Tracing (simplified setup)** – automatic correlation with model calls, evaluations, and agents.
2. **Direct Application Insights Integration (manual setup)** – without linking to AI Foundry.

---

## 🔸 2. Setup A — Azure AI Foundry + Application Insights (Recommended)

### **Step 1 — Connect App Insights to Project**
1. Go to **Azure AI Foundry → Your Project → Tracing**.
2. Associate an **Application Insights** resource.
3. Copy the **Project Endpoint URI**.

### **Step 2 — Use the TelemetryManager class**
The `TelemetryManager` automatically retrieves your Application Insights connection string from the project and initializes tracing.

```python
telemetry_manager.initialize(
    project_endpoint="https://<your-resource>.services.ai.azure.com/api/projects/<project>",
    enable_console_export=True
)
```

### **Step 3 — Use decorators and spans**
```python
@trace_function(attributes={"operation": "generate_summary"}, capture_args=True)
def generate_summary(doc: str):
    # Your model call here
    return summarize_text(doc)
```

You can also wrap code blocks:
```python
with telemetry_manager.create_span("agent_decision", {"agent": "retrieval"}):
    result = run_retrieval()
```

### **Step 4 — Log Evaluations**
```python
from evaluations import log_relevance_score, log_coherence_score

log_relevance_score(0.88, response_id="resp_123", comments="Highly relevant")
log_coherence_score(0.75, response_id="resp_123", comments="Some repetition")
```

### **Step 5 — View in Azure AI Foundry**
Navigate to **Project → Tracing**. You’ll see spans with metadata such as:
- Function name
- Token usage
- Evaluation metrics
- Custom span attributes

Click **View in Application Insights** for advanced analytics.

---

## 🔸 3. Setup B — Direct Application Insights (Without AI Foundry)

### **Option 1 — Using Environment Variable**
```bash
export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=<your-key>;IngestionEndpoint=https://<region>.in.applicationinsights.azure.com/"
```

Then initialize telemetry directly:
```python
telemetry_manager.initialize(connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"))
```

### **Option 2 — Without TelemetryManager**
You can configure OpenTelemetry manually:
```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

configure_azure_monitor(connection_string="InstrumentationKey=<key>")

tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("local_span_test"):
    print("This trace goes to Application Insights.")
```

---

## 🔹 4. KQL Queries for Application Insights
Once spans are flowing to Application Insights, use these queries for debugging and evaluation tracking.

### **Query 1 — All traces grouped by span name**
```kql
traces
| summarize Count = count(), AvgDuration = avg(duration) by name
| order by Count desc
```

### **Query 2 — Function performance overview**
```kql
traces
| where message contains "function.duration_ms"
| extend Duration = toreal(todynamic(customDimensions).['function.duration_ms'])
| summarize AvgDurationMs = avg(Duration), Calls = count() by name
| order by AvgDurationMs desc
```

### **Query 3 — AI Evaluation Scores**
```kql
traces
| where name startswith "gen_ai.evaluation"
| extend Evaluator = tostring(customDimensions.['gen_ai.evaluator.name']),
         Score = toreal(customDimensions.['gen_ai.evaluation.score'])
| summarize AvgScore = avg(Score), Count = count() by Evaluator
| order by AvgScore desc
```

### **Query 4 — End-to-End Request Correlation**
```kql
requests
| join kind=inner (traces) on operation_Id
| project operation_Id, name, timestamp, message, customDimensions
```

### **Query 5 — Recent Errors in Traces**
```kql
traces
| where severityLevel >= 3
| project timestamp, name, message, customDimensions
| order by timestamp desc
```

---

## 🔹 5. Advanced AI Foundry Features
When using Azure AI Foundry:
- Evaluations (`log_evaluation`, `EvaluationContext`) appear automatically under trace events.
- You can visualize **agent hops**, **model completions**, and **evaluation metrics** in sequence.
- The Foundry UI correlates spans from multiple services (e.g., LangChain → RAG → Evaluator).

**Tip:** Click *“View in Application Insights”* to access raw traces and run KQL queries directly.

---

## 🔹 6. Troubleshooting & Best Practices
- Ensure `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true` is set **before** SDK instrumentation.
- Avoid logging sensitive data.
- Use `EvaluationContext` for grouped metric logging.
- Use console export during development.

---

### ✅ Example — Combined Evaluation and Tracing
```python
with telemetry_manager.create_span("chat_response", {"user_id": "42"}):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Tell me about Dubai."}],
    )

    with EvaluationContext(response_id="resp_42") as eval_ctx:
        eval_ctx.add_metric("relevance", 0.9, "Accurate and to the point")
        eval_ctx.add_metric("coherence", 0.8, "Well-structured")
```

This will emit structured telemetry visible both in Azure AI Foundry and in Application Insights with all span, evaluation, and custom attributes captured.

---

**References:**
- [Microsoft Learn: View trace results for AI applications](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/trace-results-sdk)
- [Azure Monitor OpenTelemetry documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable)
- [KQL reference for Application Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/query-language)

