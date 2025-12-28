# Life AI Agentic - Molecule Generation & Screening

[![Python](https://img.shields.io/badge/python-3.9+-blue)]() [![FastAPI](https://img.shields.io/badge/FastAPI-async-009688)]() [![RDKit](https://img.shields.io/badge/RDKit-chemistry-orange)]()

Production-style agentic backend for drug-like molecule discovery using multi-agent system architecture and real chemistry validation.

## 🚀 Quick Start

```bash
# Setup (one time)
./setup.sh

# Start server
./run.sh

# Run demo
./demo.sh
```

**Server runs at:** http://localhost:8000  

## ✨ Key Features

- **Multi-Agent System** - Planner, Generator, and Ranker agents with clear separation
- **Factory Pattern** - Strict architectural compliance for maintainability
- **RDKit Integration** - Real chemistry validation and property computation
- **Rule-Based Screening** - Lipinski Rule of Five + TPSA constraints
- **Multi-Round Feedback** - Top molecules seed next generation round
- **Full Traceability** - Every decision logged and queryable via API
- **Async Execution** - Non-blocking background processing

## 🎯 Scope

This project focuses on **agentic backend system design** and **traceable workflows**.  
It intentionally excludes ML model training, molecular docking, QSAR prediction, and biological validation.  
Runs are deterministic and reproducible given the same configuration and seed.

## ️ Architecture

### Agentic Workflow

```
┌──────────────┐
│   Planner    │ → Define strategy (rounds, candidates, constraints)
└──────┬───────┘
       │
       v
┌──────────────┐
│  Generator   │ → Propose candidate molecules (SMILES)
└──────┬───────┘
       │
       v
┌──────────────┐
│ RDKit Tool   │ → Validate & compute properties
└──────┬───────┘
       │
       v
┌──────────────┐
│  Screening   │ → Apply Lipinski rules & score
└──────┬───────┘
       │
       v
┌──────────────┐
│   Ranker     │ → Score, rank, select top molecules
└──────────────┘
       │
       v
  Repeat N rounds
```

### Design Principles

1. **Separation of Concerns** - Agents make decisions, Tools provide facts, Pipeline orchestrates
2. **Factory Pattern** - All agents/tools created via factories, zero direct instantiation
3. **Single Responsibility** - Each module has one clear purpose
4. **Deterministic Agents** - Rule-based policies for full explainability and auditability
5. **Observable** - Structured logging and queryable trace

## 📁 Project Structure

```
life-ai-agentic/
├── app/
│   ├── main.py                      # FastAPI app + router setup
│   │
│   ├── agents/                      # Decision-making units
│   │   ├── base.py                  # - Abstract agent interface
│   │   ├── planner.py               # - Defines run strategy
│   │   ├── generator.py             # - Proposes candidate molecules
│   │   └── ranker.py                # - Scores and selects top-K
│   │
│   ├── chemistry/                   # RDKit integration (single source of truth)
│   │   └── rdkit_tool.py            # - Validate & compute descriptors
│   │
│   ├── screening/                   # Rule-based evaluation
│   │   └── rules.py                 # - Lipinski rules + scoring
│   │
│   ├── factories/                   # Object creation layer (required pattern)
│   │   ├── agent_factory.py         # - Creates agents
│   │   └── tool_factory.py          # - Creates tools
│   │
│   ├── runner/                      # Pipeline orchestration
│   │   └── pipeline.py              # - Multi-round agentic loop
│   │
│   ├── api/                         # REST endpoints
│   │   └── runs.py                  # - POST /runs, GET /status, /results, /trace
│   │
│   ├── db/                          # Persistence layer
│   │   ├── models.py                # - Run, Molecule, TraceEvent models
│   │   └── session.py               # - SQLAlchemy session management
│   │
│   ├── trace/                       # Observability
│   │   └── tracer.py                # - Structured event logging
│   │
│   └── schemas/                     # API contracts
│       └── api.py                   # - Pydantic request/response models
│
├── requirements.txt                 # Python dependencies
├── setup.sh                         # One-time environment setup
├── run.sh                           # Start server
└── demo.sh                          # Full API demo
```

## 📡 API Endpoints

### Create Run
```bash
curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{
    "rounds": 3,
    "candidates_per_round": 50,
    "top_k": 5
  }'
```

**Parameters:**
- `rounds` (1-10, default: 3) - Number of generation rounds
- `candidates_per_round` (10-200, default: 50) - Molecules per round
- `top_k` (1-20, default: 5) - Top molecules to select
- `max_violations` (0-5, default: 1) - Max rule violations allowed
- `scoring_penalty` (0.0-1.0, default: 0.1) - Penalty per violation

**Response:**
```json
{
  "run_id": "f47ac10b-...",
  "status": "queued",
  "message": "Run created and queued for execution"
}
```

### Check Status
```bash
curl http://localhost:8000/runs/{run_id}/status
```

### Get Results
```bash
curl http://localhost:8000/runs/{run_id}/results
```

### View Trace
```bash
curl http://localhost:8000/runs/{run_id}/trace
```

**Sample Trace Event:**
```json
{
  "timestamp": "2025-12-28T11:49:26.322040",
  "actor": "generator",
  "action": "Generated 100 candidates",
  "round": 1
}
```

## 🧪 Chemistry & Screening

### Molecular Properties (RDKit)

| Property | Description | Importance |
|----------|-------------|------------|
| **MW** | Molecular Weight | Oral bioavailability |
| **LogP** | Lipophilicity | Membrane permeability |
| **HBD** | H-Bond Donors | Absorption |
| **HBA** | H-Bond Acceptors | Absorption |
| **TPSA** | Polar Surface Area | Cell permeability |
| **QED** | Drug-likeness (0-1) | Overall quality |

### Screening Rules (Lipinski Rule of Five)

```python
rules = {
    'MW': {'max': 500},      # Molecular Weight ≤ 500 Da
    'LogP': {'max': 5},      # LogP ≤ 5
    'HBD': {'max': 5},       # H-Bond Donors ≤ 5
    'HBA': {'max': 10},      # H-Bond Acceptors ≤ 10
    'TPSA': {'max': 140}     # Polar Surface Area ≤ 140 Ų
}
```

**Scoring:** `score = QED - (penalty × violations)`

## 🛠️ Development

### Prerequisites
- Python 3.9+
- 4GB RAM minimum

### Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload --port 8000
```

### Testing
```bash
# Quick API test
./test_api.sh

# Full demo with results
./demo.sh
```

## 🔧 Troubleshooting

### RDKit Installation Issues
```bash
# Option 1: Use conda (recommended)
conda install -c conda-forge rdkit

# Option 2: Use rdkit-pypi
pip install rdkit-pypi
```

### Port Already in Use
```bash
# Find and kill process
kill $(lsof -ti:8000)

# Or change port
uvicorn app.main:app --port 8080
```
