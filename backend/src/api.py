from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv

from .main import ScanEngine
from .utils.logger import logger

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
