# CompliantByDefault - Architecture Documentation

## System Overview

CompliantByDefault is a full-stack application that automatically analyzes codebases for SOC 2 compliance gaps using static analysis and AI-powered insights.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────────────┐ │
│  │  Pages   │  │Components │  │  API Client (axios)       │ │
│  │ - Home   │  │- Navbar   │  │  - scanLocal()            │ │
│  │ - Scan   │  │- Selector │  │  - scanGithub()           │ │
│  │ - Report │  │- Progress │  │  - getReport()            │ │
│  └──────────┘  └───────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Layer (api.py)                      │   │
│  │  - POST /scan/local                                  │   │
│  │  - POST /scan/github                                 │   │
│  │  - GET  /report/{id}                                 │   │
│  │  - GET  /reports                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Orchestration (main.py - ScanEngine)         │   │
│  │  - Coordinates all scanners                          │   │
│  │  - Manages scan lifecycle                            │   │
│  │  - Aggregates results                                │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│         ┌─────────────────┼─────────────────┐               │
│         ▼                 ▼                 ▼               │
│  ┌────────────┐  ┌────────────┐  ┌────────────────┐        │
│  │  Scanners  │  │ Analyzers  │  │ Integrations   │        │
│  │- Secret    │  │- LLM (AI)  │  │- GitHub Loader │        │
│  │- Static    │  │- Scoring   │  └────────────────┘        │
│  │- Deps      │  └────────────┘                             │
│  │- IaC       │         │                                   │
│  └────────────┘         ▼                                   │
│                 ┌────────────────┐                          │
│                 │ Report Gen     │                          │
│                 │ - JSON output  │                          │
│                 │ - MD output    │                          │
│                 └────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌─────────────────┐
                  │  Gemini API     │
                  │  (Google AI)    │
                  └─────────────────┘
```

## Component Details

### Frontend Layer

**Technology**: Next.js 14, React 18, TypeScript, Tailwind CSS

**Responsibilities**:
- User interface rendering
- Form handling and validation
- Real-time scan progress polling
- Report visualization
- Client-side routing

**Key Files**:
- `pages/` - Route components (index, scan, report/[id])
- `components/` - Reusable UI components
- `lib/api.ts` - API client with typed requests
- `types/index.ts` - TypeScript type definitions

### Backend Layer

**Technology**: Python 3.9+, FastAPI, Pydantic, asyncio

**Responsibilities**:
- RESTful API endpoints
- Request validation
- Asynchronous scan orchestration
- Data persistence (JSON files)
- CORS handling

**Key Files**:
- `api.py` - FastAPI application and routes
- `main.py` - ScanEngine orchestration
- `cli.py` - Command-line interface

### Scanning Layer

**Components**:

1. **SecretScanner**
   - Regex-based pattern matching
   - Detects hardcoded credentials, API keys, tokens
   - File-type aware (flags .env, .pem, etc.)

2. **StaticScanner**
   - Security anti-pattern detection
   - SQL injection, weak crypto, insecure configurations
   - Language-agnostic patterns

3. **DependencyScanner**
   - Package manifest parsing
   - Version constraint analysis
   - Known vulnerability checking (simplified CVE database)

4. **IaCScanner**
   - Infrastructure as Code analysis
   - Terraform, Docker, Kubernetes manifest scanning
   - Cloud misconfigurations (public S3, unencrypted storage)

### Analysis Layer

**Components**:

1. **LLMAnalyzer**
   - Uses Google Gemini 1.5 Flash model
   - Maps findings to SOC 2 controls
   - Generates narrative insights
   - Prioritizes remediation
   - Structured JSON output

2. **ScoringEngine**
   - Calculates readiness score (0-100)
   - Assigns letter grade (A-F)
   - Weights severity impact
   - Computes control coverage
   - Risk level assessment

### Integration Layer

**GitHubLoader**:
- Repository cloning via GitPython
- Supports HTTPS and token authentication
- Metadata extraction
- Temporary file management

### Report Generation

**ReportGenerator**:
- Dual-format output (JSON + Markdown)
- Comprehensive scan results
- Finding details with recommendations
- Control-by-control breakdown
- Downloadable reports

## Data Flow

### Scan Workflow

```
1. User initiates scan via UI or CLI
   │
2. API receives request → validate input
   │
3. Generate unique job_id (UUID)
   │
4. Return job_id immediately (async processing)
   │
5. Background task:
   ├─ Load files (GitHub clone or local read)
   ├─ Run all scanners in parallel
   ├─ Aggregate findings
   ├─ Send to LLM analyzer
   ├─ Calculate scores
   └─ Generate report (JSON + MD)
   │
6. Save report to disk
   │
7. User polls GET /report/{job_id}
   │
8. Return full report when ready
```

### Report Structure

```json
{
  "id": "uuid",
  "generated_at": "ISO timestamp",
  "metadata": {
    "job_id": "...",
    "scan_type": "local|github",
    "repository": "...",
    "timestamp": "..."
  },
  "summary": {
    "total_findings": 42,
    "readiness_score": 73,
    "grade": "C",
    "risk_level": "Medium"
  },
  "score": {
    "overall_score": 73,
    "severity_impact": {...},
    "control_scores": {...}
  },
  "controls": {
    "CC1": {
      "name": "...",
      "status": "compliant|partial|non_compliant",
      "score": 85,
      "findings_count": 2
    }
  },
  "findings": [
    {
      "type": "hardcoded_password",
      "severity": "critical",
      "file": "app.py",
      "line": 42,
      "message": "...",
      "control": "CC9",
      "recommendation": "..."
    }
  ],
  "analysis": {
    "posture": "AI-generated assessment",
    "critical_risks": [...],
    "top_actions": [...]
  },
  "recommendations": [...]
}
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109
- **Runtime**: Python 3.9+
- **AI**: Google Generative AI (Gemini 1.5)
- **Validation**: Pydantic 2.5
- **Git**: GitPython 3.1
- **Config**: PyYAML 6.0
- **Testing**: pytest, httpx

### Frontend
- **Framework**: Next.js 14
- **Language**: TypeScript 5.3
- **UI**: React 18, Tailwind CSS 3.4
- **HTTP**: Axios 1.6
- **Rendering**: Markdown support (react-markdown)

### Infrastructure
- **API Server**: Uvicorn (ASGI)
- **CORS**: Enabled for localhost:3000
- **Storage**: File-based (JSON reports)
- **Deployment**: Docker-ready, Vercel-compatible

## Security Considerations

1. **API Key Management**
   - Gemini API key stored in environment variables
   - Never committed to version control
   - .env.example provided for setup

2. **GitHub Token Handling**
   - Optional token for private repos
   - Not logged or persisted
   - Used only for clone operation

3. **Input Validation**
   - Pydantic models for request validation
   - Path traversal prevention
   - File size limits (10MB per file)

4. **Scan Isolation**
   - Each scan uses isolated directory
   - Cleanup after completion
   - No shared state between scans

## Scalability Considerations

### Current Limitations
- File-based report storage (not database)
- Synchronous LLM calls
- Single-server deployment
- In-memory scan state

### Future Enhancements
- PostgreSQL for report persistence
- Redis for job queue and caching
- Distributed scanning (Celery workers)
- Webhook notifications for completion
- Multi-tenant support
- Historical trend analysis

## Performance Optimizations

1. **Shallow Git Clones** (`depth=1`)
2. **File Filtering** (excludes node_modules, binaries)
3. **Parallel Scanner Execution** (async/await)
4. **Pagination** (frontend findings table)
5. **Pattern Compilation** (regex caching)

## Error Handling

- **API**: HTTP status codes (400, 404, 500)
- **Graceful Degradation**: LLM failures don't block reports
- **User Feedback**: Clear error messages at each layer
- **Logging**: Structured logs with context
- **Retries**: Frontend auto-retries report polling

## Extensibility

### Adding New Scanners
1. Create scanner class in `backend/src/scanners/`
2. Implement `scan_file()` and `scan_directory()` methods
3. Return findings in standard format
4. Add to `ScanEngine` orchestration
5. Update SOC2 controls YAML if needed

### Adding New Controls
1. Edit `backend/src/config/soc2_controls.yaml`
2. Add control metadata (name, description, checks)
3. Define patterns if applicable
4. Update frontend types if new fields added

### Custom LLM Prompts
Modify `llm_analyzer.py` `_get_llm_analysis()` method to customize AI behavior.

## Deployment Options

1. **Docker Compose** - Backend + Frontend containers
2. **Separate Hosting** - Vercel (frontend) + Cloud Run (backend)
3. **Kubernetes** - Scalable microservices
4. **Serverless** - Functions for scanners, static frontend

## Monitoring & Observability

**Recommended Additions**:
- Application Performance Monitoring (APM)
- Error tracking (Sentry)
- Analytics (Posthog, Google Analytics)
- Log aggregation (ELK stack)
- Uptime monitoring

## License & Compliance

- **Code**: MIT License
- **Dependencies**: Check individual package licenses
- **AI**: Google Gemini API Terms of Service apply
