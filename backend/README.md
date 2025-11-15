# CompliantByDefault Backend

SOC 2 Readiness Agent - Python backend for analyzing repositories for compliance gaps.

## Features

- 🔍 **Multi-Scanner Analysis**: Secrets, static code, dependencies, and IaC scanning
- 🤖 **AI-Powered Insights**: Gemini LLM for intelligent compliance mapping
- 📊 **SOC 2 Control Mapping**: Automatic mapping to SOC 2 controls (CC1-CC9)
- 📈 **Readiness Scoring**: Calculate compliance scores and grades
- 🔌 **Multiple Interfaces**: REST API, CLI tool, and Python library
- 📄 **Rich Reports**: JSON and Markdown report generation

## Installation

### Prerequisites

- Python 3.9+
- pip or pipenv

### Setup

```bash
# Clone the repository
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_optional
```

## Usage

### 1. As a REST API

Start the FastAPI server:

```bash
# From the backend directory
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation (Swagger): `http://localhost:8000/docs`

#### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /scan/local` - Scan a local directory
- `POST /scan/github` - Scan a GitHub repository
- `GET /report/{job_id}` - Get scan report
- `GET /reports` - List all reports
- `GET /controls` - Get SOC 2 controls info

#### Example API Calls

**Scan a local directory:**

```bash
curl -X POST http://localhost:8000/scan/local \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/your/project"}'
```

**Scan a GitHub repository:**

```bash
curl -X POST http://localhost:8000/scan/github \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo"}'
```

**Get report:**

```bash
curl http://localhost:8000/report/<job-id>
```

### 2. As a CLI Tool

```bash
# Scan a local directory
python -m src.cli scan-local /path/to/project

# Scan a GitHub repository
python -m src.cli scan-github https://github.com/user/repo

# With GitHub token
python -m src.cli scan-github https://github.com/user/repo -t your_token

# Get a specific report
python -m src.cli report <job-id>

# List all reports
python -m src.cli list

# Save output to file
python -m src.cli scan-local /path/to/project -o report.json
```

### 3. As a Python Library

```python
from src.main import ScanEngine

# Initialize
engine = ScanEngine()

# Scan local directory
job_id = await engine.scan_local("/path/to/project")

# Scan GitHub repository
job_id = await engine.scan_github("https://github.com/user/repo")

# Get report
report = engine.get_report(job_id)

print(f"Score: {report['summary']['readiness_score']}/100")
```

## Project Structure

```
backend/
├── src/
│   ├── main.py              # Main scan orchestration engine
│   ├── api.py               # FastAPI REST API
│   ├── cli.py               # Command-line interface
│   ├── config/
│   │   └── soc2_controls.yaml  # SOC 2 controls and patterns
│   ├── scanners/
│   │   ├── secret_scanner.py    # Detect hardcoded secrets
│   │   ├── static_scanner.py    # Static code analysis
│   │   ├── dependency_scanner.py # Dependency vulnerabilities
│   │   └── iac_scanner.py       # Infrastructure as Code
│   ├── analyzers/
│   │   ├── llm_analyzer.py      # Gemini-based analysis
│   │   └── scoring.py           # Scoring engine
│   ├── integrations/
│   │   └── github_loader.py     # GitHub integration
│   ├── utils/
│   │   ├── logger.py            # Logging utility
│   │   └── file_loader.py       # File operations
│   └── reports/
│       └── report_generator.py  # Report generation
├── tests/
│   ├── test_secret_scanner.py
│   ├── test_static_scanner.py
│   └── test_api.py
├── requirements.txt
└── README.md
```

## How It Works

1. **Scan**: Multiple scanners analyze the codebase
   - Secret Scanner: Detects hardcoded credentials, API keys, tokens
   - Static Scanner: Finds security anti-patterns (SQL injection, weak crypto)
   - Dependency Scanner: Checks for vulnerable packages
   - IaC Scanner: Analyzes Terraform, Docker, Kubernetes configs

2. **Analyze**: Gemini LLM processes findings
   - Maps findings to SOC 2 controls
   - Assesses compliance gaps
   - Generates recommendations

3. **Score**: Calculate readiness metrics
   - Overall compliance score (0-100)
   - Control-by-control assessment
   - Risk level determination

4. **Report**: Generate comprehensive reports
   - JSON format for programmatic access
   - Markdown for human readability
   - Detailed findings and remediation steps

## SOC 2 Controls Covered

- **CC1**: Control Environment
- **CC2**: Communication and Information
- **CC3**: Risk Assessment
- **CC4**: Monitoring Activities
- **CC5**: Control Activities
- **CC6**: Logical and Physical Access Controls
- **CC7**: System Operations
- **CC8**: Change Management
- **CC9**: Risk Mitigation

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_api.py

# Verbose output
pytest -v
```

## Development

### Adding New Scanners

1. Create a new scanner in `src/scanners/`
2. Implement `scan_file()` and `scan_directory()` methods
3. Add to `main.py` orchestration
4. Update tests

### Configuring Patterns

Edit `src/config/soc2_controls.yaml` to add or modify:
- Security patterns
- Control mappings
- Severity weights

## Troubleshooting

**"GEMINI_API_KEY not found"**
- Make sure you've set the API key in `.env` file
- Get API key from: https://makersuite.google.com/app/apikey

**"Failed to clone repository"**
- Check repository URL is correct
- For private repos, provide a GitHub token
- Ensure you have network connectivity

**Slow scans**
- Large repositories take longer
- Consider excluding directories in `file_loader.py`
- IaC and dependency scans are fastest

## License

MIT

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/CompliantByDefault/issues)
- Documentation: See `/docs` folder
