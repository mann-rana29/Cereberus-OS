# Cerberus OS — Architecture Document

## System Overview

Cerberus OS is a local-first, event-driven industrial safety platform that detects **compound hazards** — situations where elevated gas levels coincide with active work permits in the same zone. It runs entirely on-device with no cloud dependencies.

---

## System Diagram

```mermaid
flowchart TD
    subgraph SCADA Layer
        S1[Battery 4 Sensors]
        S2[Battery 3 Sensors]
        S3[Pump Station P3A Sensors]
    end

    subgraph Ingestion Layer
        KC[Stream Consumer<br/>stream_consumer.py]
        TF{Threshold Filter<br/>telemetry_service.py}
    end

    subgraph Data Layer
        DB[(SQLite<br/>active_plant.db)]
        SL[sensor_logs table]
        PT[permits table]
    end

    subgraph Intelligence Layer
        SM[State Manager<br/>state_manager.py]
        PS[Permit Service<br/>permit_service.py]
        LLM[Qwen3 0.6B<br/>via Ollama<br/>llm_service.py]
    end

    subgraph API Layer
        AR[Alerts Router<br/>SSE + Latest]
        PR[Permit Router<br/>CRUD]
        TR[Telemetry Router<br/>Logs + Ingest]
    end

    subgraph Frontend Layer
        FD[index.html<br/>Plant Dashboard]
        FC[compliance.html<br/>Audit Log]
        FO[copilot.html<br/>Operator Portal]
    end

    S1 & S2 & S3 --> KC
    KC -->|every 5s| TF
    TF -->|below threshold| DROP[Drop silently]
    TF -->|above threshold| SL
    SL --> SM
    SM -->|query permits| PS
    PS --> PT
    SM -->|gas + permit context| LLM
    LLM -->|CRITICAL_HAZARD_VIOLATION| AR
    LLM -->|OPERATIONS_CLEAR| LOG[Log only]
    AR -->|SSE stream| FD
    AR -->|GET /latest| FO
    TR -->|GET /logs| FC
    PR -->|CRUD| FD & FO

    style LLM fill:#dc2626,stroke:#991b1b,color:#fff
    style DB fill:#1e40af,stroke:#1e3a5f,color:#fff
    style AR fill:#059669,stroke:#047857,color:#fff
```

---

## Model Pipeline

### Inference Flow

```mermaid
sequenceDiagram
    participant SC as Stream Consumer
    participant TS as Telemetry Service
    participant SM as State Manager
    participant PS as Permit Service
    participant LLM as Qwen3 0.6B (Ollama)
    participant AR as Alerts Router
    participant FE as Frontend (SSE)

    SC->>TS: ingest_sensor_log(zone, gas, ppm)
    TS->>TS: check_threshold(gas, ppm)
    alt Below threshold
        TS-->>SC: None (dropped)
    else Above threshold
        TS->>TS: INSERT into sensor_logs
        TS->>SM: evaluate_compound_hazard(zone, gas, ppm)
        SM->>PS: get_active_permits_for_zone(zone)
        alt No active permits
            SM-->>TS: None
        else Permits exist
            SM->>LLM: get_llm_verdict(zone, gas, ppm, permits)
            Note over LLM: Prompt includes:<br/>- Zone ID<br/>- Gas type + PPM<br/>- Active permit details<br/>- Safety thresholds<br/>- Required JSON format
            LLM-->>SM: {status_code, reason, audio_phrase}
            SM->>SM: Enrich with zone, gas_type, gas_ppm
            SM->>AR: set_latest_alert(verdict)
            alt CRITICAL_HAZARD_VIOLATION
                AR-->>FE: SSE event broadcast
            end
            SM-->>TS: verdict
        end
    end
```

---

## Data Flow

### Sensor Data Path

```
Raw Reading → Threshold Check → DB Insert → Permit Lookup → LLM Evaluation → Alert Broadcast
     ↓              ↓                                              ↓
  (all data)    (filtered ~70%)                              (only ~5% reach LLM)
```

**Key optimization**: The system is designed as a funnel. Most readings never reach the expensive LLM inference step.

| Stage | Data Volume | Latency |
|-------|-------------|---------|
| Raw sensor reading | 100% | <1 ms |
| Threshold filter | ~30% pass | <1 ms |
| DB insert + permit lookup | ~30% | <10 ms |
| LLM inference | ~5% (only when permits exist) | 1-3 seconds |
| Alert broadcast | <1% | <10 ms |

---

## Local vs Cloud Components

### Fully Local (No Internet Required)

| Component | Technology | Runs Where |
|-----------|-----------|------------|
| REST API Server | FastAPI + Uvicorn | Local CPU |
| Database | SQLite3 | Local disk |
| LLM Inference | Qwen3 0.6B via Ollama | Local CPU/GPU |
| Threshold Evaluation | Python logic | Local CPU |
| Permit Management | SQLite CRUD | Local CPU |
| SSE Alert Stream | FastAPI StreamingResponse | Local CPU |
| Frontend | Static HTML + JS | Browser |

### Internet Required (Setup Only)

| Component | When | Purpose |
|-----------|------|---------|
| `pip install` | First setup | Download Python packages |
| `ollama pull` | First setup | Download model weights (~400 MB) |
| CDN scripts | Page load | Tailwind CSS + Alpine.js (can be cached/bundled) |

> **After initial setup, the entire system runs air-gapped.** This is critical for industrial plants where internet may be restricted or unavailable.

---

## Key Design Decisions

### 1. Compound Hazard Only

**Decision**: Only trigger alerts when gas AND permit coexist.

**Rationale**: Gas sensors trigger constantly in industrial environments. Permit systems process continuously. Alerting on either alone would create alert fatigue. The real danger is the **intersection** — when humans are working in a zone with elevated gas.

### 2. Small Local Model (0.6B)

**Decision**: Use Qwen3:0.6B instead of a larger model.

**Rationale**:
- Runs on any modern laptop CPU without GPU
- ~400 MB disk footprint (quantized)
- 1-3 second inference — fast enough for safety alerts
- Deterministic with `temperature: 0`
- Structured JSON output is well within 0.6B capability

**Trade-off**: Borderline cases may be less accurate than a 7B+ model, but the threshold pre-filter handles most edge cases before reaching the LLM.

### 3. SQLite Over PostgreSQL

**Decision**: Use SQLite with WAL mode (`journal_mode=WAL`) and `timeout=30`.

**Rationale**:
- Zero configuration, no separate database server
- Single-file deployment
- Sufficient for single-plant, single-shift usage
- WAL mode ensures readers never block writers and writers never block readers
- `timeout=30` prevents lock failures during concurrent consumer writes

**Trade-off**: Not suitable for multi-plant or distributed deployment.

### 4. SSE Over WebSocket for Alerts

**Decision**: Use Server-Sent Events instead of WebSocket.

**Rationale**:
- Unidirectional (server → client) is sufficient for alerts
- Simpler implementation
- Automatic reconnection built into `EventSource` API
- Works through HTTP proxies and firewalls

### 5. Threshold Pre-Filter

**Decision**: Drop readings below safe limits before any DB or AI interaction.

**Rationale**:
- Reduces DB writes by ~70%
- Reduces LLM calls by ~95%
- Keeps the system responsive under high sensor frequency
- Safety thresholds are based on OISD standards

### 6. No Authentication

**Decision**: API endpoints are open with `allow_origins=["*"]`.

**Rationale**: Designed for isolated plant LANs where the network itself is the security boundary. Adding auth would complicate deployment in environments where IT support is minimal.

**Risk**: Must not be exposed to public networks.

### 7. Robust JSON Extraction

**Decision**: Extract JSON using `raw[raw.find("{"):raw.rfind("}")+1]` instead of markdown stripping.

**Rationale**: Small LLMs frequently wrap JSON in explanation text, markdown fences, or thinking tokens. Brace-finding is the most reliable extraction method across model variations.

### 8. Error-Resilient Consumer Loop

**Decision**: Wrap `ingest_sensor_log()` in try/except within the stream consumer.

**Rationale**: A single failed DB write or LLM timeout must not kill the entire sensor ingestion loop. The consumer must stay alive to process subsequent readings.

---

## Technology Stack Summary

```mermaid
graph LR
    subgraph Backend
        PY[Python 3.10+]
        FA[FastAPI]
        UV[Uvicorn]
        SQ[SQLite3]
        OL[Ollama]
        QW[Qwen3 0.6B]
    end

    subgraph Frontend
        HTML[HTML5]
        TW[Tailwind CSS]
        ALP[Alpine.js]
        SSE[EventSource API]
    end

    PY --> FA --> UV
    FA --> SQ
    FA --> OL --> QW
    HTML --> TW
    HTML --> ALP
    HTML --> SSE
```

---

## Security Boundary

```
┌──────────────────────────────────────────┐
│              Plant LAN (Air-gapped)       │
│                                          │
│  ┌─────────┐     ┌──────────┐            │
│  │ SCADA   │────▶│ Cerberus │            │
│  │ Sensors │     │ Backend  │            │
│  └─────────┘     │ :8000    │            │
│                  └────┬─────┘            │
│                       │                  │
│              ┌────────┴────────┐         │
│              │                 │         │
│         ┌────▼─────┐    ┌─────▼────┐    │
│         │ Frontend │    │ Ollama   │    │
│         │ :3000    │    │ LLM      │    │
│         └──────────┘    └──────────┘    │
│                                          │
│  No data leaves this boundary            │
└──────────────────────────────────────────┘
```
