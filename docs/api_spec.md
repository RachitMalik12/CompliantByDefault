# API Specification

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required. All endpoints are publicly accessible.

---

## Endpoints

### 1. Health Check

Check API health and configuration status.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "gemini_configured": true
}
```

**Status Codes**:
- `200 OK` - API is healthy

---

### 2. Get API Information

Get basic API information.

**Endpoint**: `GET /`

**Response**:
```json
{
  "name": "CompliantByDefault API",
  "version": "1.0.0",
  "status": "running"
}
```

---

### 3. Scan Local Directory

Initiate a scan of a local directory.

**Endpoint**: `POST /scan/local`

**Request Body**:
```json
{
  "path": "/absolute/path/to/directory"
}
```

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started",
  "message": "Scan initiated for /absolute/path/to/directory"
}
```

**Status Codes**:
- `200 OK` - Scan started successfully
- `400 Bad Request` - Invalid path or path doesn't exist
- `500 Internal Server Error` - Server error

**Errors**:
```json
{
  "detail": "Path does not exist"
}
```

---

### 4. Scan GitHub Repository

Initiate a scan of a GitHub repository.

**Endpoint**: `POST /scan/github`

**Request Body**:
```json
{
  "repo_url": "https://github.com/username/repository",
  "token": "ghp_xxxxxxxxxxxxxxxxxxxx"  // optional
}
```

**Parameters**:
- `repo_url` (string, required) - Full GitHub repository URL
- `token` (string, optional) - GitHub personal access token for private repos

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started",
  "message": "Scan initiated for https://github.com/username/repository"
}
```

**Status Codes**:
- `200 OK` - Scan started successfully
- `400 Bad Request` - Invalid URL
- `500 Internal Server Error` - Clone failed or server error

**Errors**:
```json
{
  "detail": "Invalid GitHub repository URL"
}
```

---

### 5. Get Scan Report

Retrieve a completed scan report by job ID.

**Endpoint**: `GET /report/{job_id}`

**Parameters**:
- `job_id` (string, path) - UUID of the scan job

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "generated_at": "2025-11-15T12:34:56.789Z",
  "metadata": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "scan_type": "github",
    "path": "/tmp/repo_clone",
    "repository": "https://github.com/username/repository",
    "timestamp": "2025-11-15T12:34:56.789Z",
    "scanner_versions": {
      "secret": "1.0",
      "static": "1.0",
      "dependency": "1.0",
      "iac": "1.0"
    }
  },
  "summary": {
    "total_findings": 42,
    "readiness_score": 73,
    "grade": "C",
    "risk_level": "Medium - 5 high-severity issues to address"
  },
  "score": {
    "overall_score": 73,
    "grade": "C",
    "base_score": 68.5,
    "coverage_score": 77.8,
    "severity_impact": {
      "counts": {
        "critical": 2,
        "high": 5,
        "medium": 15,
        "low": 20,
        "info": 0
      },
      "total_weight": 105,
      "deduction": 31.5
    },
    "control_scores": {
      "CC1": {
        "score": 100,
        "status": "compliant",
        "name": "Control Environment",
        "findings": 0
      }
      // ... other controls
    },
    "total_issues": 42,
    "controls_compliant": 7,
    "controls_total": 9
  },
  "controls": {
    "CC1": {
      "name": "Control Environment",
      "description": "Organization demonstrates commitment to integrity",
      "findings_count": 0,
      "severity_score": 0,
      "status": "compliant",
      "score": 100
    }
    // ... other controls
  },
  "findings": [
    {
      "type": "hardcoded_password",
      "severity": "critical",
      "file": "/path/to/file.py",
      "line": 42,
      "message": "Potential hardcoded password detected",
      "control": "CC9",
      "snippet": "password = \"mysecret123\"",
      "recommendation": "Use environment variables or secret management"
    }
    // ... more findings
  ],
  "analysis": {
    "posture": "The codebase shows moderate security practices with several critical gaps...",
    "critical_risks": [
      "Hardcoded credentials in production code",
      "Missing authentication on sensitive endpoints"
    ],
    "compliance_gaps": [
      "Insufficient access controls (CC6)",
      "Weak encryption practices (CC9)"
    ],
    "top_actions": [
      "Remove all hardcoded credentials immediately",
      "Implement authentication middleware",
      "Enable encryption for sensitive data storage"
    ],
    "long_term_improvements": [
      "Implement automated secret scanning in CI/CD",
      "Establish regular security audits"
    ]
  },
  "recommendations": [
    {
      "priority": "critical",
      "control": "CC9",
      "issue": "Hardcoded password detected",
      "action": "Use environment variables or secret management",
      "file": "/path/to/file.py"
    }
    // ... more recommendations
  ],
  "report_files": {
    "json": "/path/to/report.json",
    "markdown": "/path/to/report.md"
  }
}
```

**Status Codes**:
- `200 OK` - Report found
- `404 Not Found` - Report not found (scan may still be running)

---

### 6. List All Reports

List summaries of all available reports.

**Endpoint**: `GET /reports`

**Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "generated_at": "2025-11-15T12:34:56.789Z",
    "score": 73,
    "findings": 42,
    "repository": "https://github.com/username/repository"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "generated_at": "2025-11-14T10:20:30.000Z",
    "score": 85,
    "findings": 12,
    "repository": "/local/path/project"
  }
]
```

**Status Codes**:
- `200 OK` - List returned (may be empty)

---

### 7. Get SOC 2 Controls

Get information about SOC 2 controls and patterns.

**Endpoint**: `GET /controls`

**Response**:
```json
{
  "CC1": {
    "name": "Control Environment",
    "description": "Organization demonstrates commitment to integrity and ethical values",
    "checks": [
      "code_of_conduct",
      "security_policies",
      "access_controls"
    ]
  },
  "CC2": {
    "name": "Communication and Information",
    "description": "Organization obtains and communicates information necessary for security",
    "checks": [
      "logging",
      "monitoring",
      "audit_trails"
    ]
  }
  // ... all controls
}
```

**Status Codes**:
- `200 OK` - Controls information returned

---

## Data Models

### ScanResponse

```typescript
{
  job_id: string;         // UUID
  status: string;         // "started"
  message: string;        // Human-readable message
}
```

### Finding

```typescript
{
  type: string;           // Finding type (e.g., "hardcoded_password")
  severity: "critical" | "high" | "medium" | "low" | "info";
  file: string;           // File path
  line: number;           // Line number
  message: string;        // Description
  control: string;        // SOC 2 control ID
  snippet?: string;       // Code snippet
  recommendation?: string;// Fix suggestion
}
```

### Control Coverage

```typescript
{
  name: string;
  description: string;
  findings_count: number;
  severity_score: number;
  status: "compliant" | "partial" | "non_compliant";
  score: number;          // 0-100
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error scenarios:
- `400` - Invalid input (path doesn't exist, invalid URL)
- `404` - Resource not found (report doesn't exist yet)
- `500` - Server error (scan failure, LLM error)

---

## Rate Limiting

Currently no rate limiting implemented. Consider adding in production.

---

## CORS

CORS is enabled for:
- `http://localhost:3000` (frontend dev server)
- `http://localhost:3001` (alternative port)

All methods and headers are allowed.

---

## Polling Recommendations

When scanning, poll `GET /report/{job_id}` every 2-3 seconds until:
- Report is returned (scan complete)
- Timeout reached (2 minutes recommended)

**Example polling logic**:
```typescript
async function waitForReport(jobId: string) {
  const maxAttempts = 60;
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const report = await getReport(jobId);
      return report; // Success
    } catch (err) {
      if (err.response?.status === 404) {
        // Not ready yet, wait and retry
        await sleep(2000);
        continue;
      }
      throw err; // Actual error
    }
  }
  throw new Error('Scan timed out');
}
```

---

## WebSocket Support

Not currently implemented. Future enhancement for real-time progress updates.

---

## Versioning

API version is returned in the root endpoint. Currently at `1.0.0`.

Future versions should be namespaced: `/v2/scan/local`
