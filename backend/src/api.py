from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv

from .main import ScanEngine
from .utils.logger import logger
from .reports.pdf_generator import generate_pdf_report
from .integrations.github_issues import GitHubIssueCreator

# Load environment variables
load_dotenv()

app = FastAPI(
    title="CompliantByDefault API",
    description="SOC 2 Readiness Agent - Analyze repositories for compliance gaps",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scan engine
scan_engine = ScanEngine()

# Request/Response Models
class LocalScanRequest(BaseModel):
    path: str = Field(..., description="Absolute path to local directory")

class GitHubScanRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL")
    token: Optional[str] = Field(None, description="GitHub personal access token")

class ScanResponse(BaseModel):
    job_id: str
    status: str = "started"
    message: str

class ReportSummary(BaseModel):
    id: str
    generated_at: str
    score: Optional[int]
    findings: Optional[int]
    repository: str

class CreateIssueRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL")
    finding: Dict = Field(..., description="Finding object to create issue for")
    token: Optional[str] = Field(None, description="GitHub personal access token")

class CreateIssueResponse(BaseModel):
    success: bool
    issue_number: Optional[int] = None
    issue_url: Optional[str] = None
    assignee: Optional[str] = None
    message: str

# Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "CompliantByDefault API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "gemini_configured": scan_engine.llm_analyzer is not None
    }

@app.post("/scan/local", response_model=ScanResponse)
async def scan_local(request: LocalScanRequest):
    """
    Scan a local directory.
    
    Args:
        request: Local scan request with path
        
    Returns:
        Job ID and status
    """
    try:
        # Validate path exists
        if not os.path.exists(request.path):
            raise HTTPException(status_code=400, detail="Path does not exist")
        
        if not os.path.isdir(request.path):
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        job_id = await scan_engine.scan_local(request.path)
        
        return ScanResponse(
            job_id=job_id,
            status="started",
            message=f"Scan initiated for {request.path}"
        )
    
    except Exception as e:
        logger.error(f"Error starting local scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scan/github", response_model=ScanResponse)
async def scan_github(request: GitHubScanRequest):
    """
    Scan a GitHub repository.
    
    Args:
        request: GitHub scan request with repo URL and optional token
        
    Returns:
        Job ID and status
    """
    try:
        job_id = await scan_engine.scan_github(
            request.repo_url,
            request.token
        )
        
        return ScanResponse(
            job_id=job_id,
            status="started",
            message=f"Scan initiated for {request.repo_url}"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting GitHub scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report/{job_id}")
async def get_report(job_id: str):
    """
    Get scan report by job ID.
    
    Args:
        job_id: Scan job identifier
        
    Returns:
        Full report data
    """
    report = scan_engine.get_report(job_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report

@app.get("/reports", response_model=List[ReportSummary])
async def list_reports():
    """
    List all available reports.
    
    Returns:
        List of report summaries
    """
    try:
        reports = scan_engine.list_reports()
        return reports
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/controls")
async def get_controls():
    """
    Get SOC 2 controls information.
    
    Returns:
        SOC 2 controls configuration
    """
    import yaml
    from pathlib import Path
    
    config_path = Path(__file__).parent / "config" / "soc2_controls.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config.get('controls', {})

@app.get("/report/{job_id}/pdf")
async def download_pdf_report(job_id: str):
    """
    Download report as PDF.
    
    Args:
        job_id: Report job identifier
        
    Returns:
        PDF file
    """
    try:
        # Get report data
        report = scan_engine.get_report(job_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Generate PDF
        pdf_path = generate_pdf_report(job_id, report)
        
        if not pdf_path.exists():
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
        
        return FileResponse(
            path=str(pdf_path),
            media_type='application/pdf',
            filename=f"compliance_report_{job_id}.pdf"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
@app.post("/issue/create", response_model=CreateIssueResponse)
async def create_github_issue(request: CreateIssueRequest):
    """
    Create a GitHub issue for a compliance finding.
    
    Args:
        request: Issue creation request with repo URL, finding, and token
        
    Returns:
        Issue creation result with issue number and URL
    """
    try:
        # Get token from request or environment
        token = request.token or os.getenv('GITHUB_TOKEN')
        
        if not token:
            raise HTTPException(
                status_code=400, 
                detail="GitHub token is required. Provide in request or set GITHUB_TOKEN environment variable."
            )
        
        # Create issue creator
        issue_creator = GitHubIssueCreator(token=token)
        
        # Create the issue
        result = issue_creator.create_issue(request.repo_url, request.finding)
        
        if result:
            return CreateIssueResponse(
                success=True,
                issue_number=result['number'],
                issue_url=result['url'],
                assignee=result['assignee'],
                message=f"Successfully created issue #{result['number']}"
            )
        else:
            return CreateIssueResponse(
                success=False,
                message="Failed to create GitHub issue. Check logs for details."
            )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating GitHub issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
