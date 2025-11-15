import uuid
import asyncio
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from .scanners.secret_scanner import SecretScanner
from .scanners.static_scanner import StaticScanner
from .scanners.dependency_scanner import DependencyScanner
from .scanners.iac_scanner import IaCScanner
from .analyzers.llm_analyzer import LLMAnalyzer
from .analyzers.scoring import ScoringEngine
from .reports.report_generator import ReportGenerator
from .integrations.github_loader import GitHubLoader
from .utils.logger import logger

class ScanEngine:
    """Main orchestration engine for running scans."""
    
    def __init__(self):
        """Initialize scan engine with all components."""
        self.secret_scanner = SecretScanner()
        self.static_scanner = StaticScanner()
        self.dependency_scanner = DependencyScanner()
        self.iac_scanner = IaCScanner()
        self.scoring_engine = ScoringEngine()
        self.report_generator = ReportGenerator()
        self.github_loader = GitHubLoader()
        
        # Initialize LLM analyzer (may raise if API key missing)
        try:
            self.llm_analyzer = LLMAnalyzer()
        except ValueError as e:
            logger.warning(f"LLM Analyzer not initialized: {e}")
            self.llm_analyzer = None
    
    async def scan_local(self, path: str) -> str:
        """
        Scan a local directory.
        
        Args:
            path: Path to local directory
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        logger.info(f"Starting local scan {job_id} for: {path}")
        
        # Run scan in background
        asyncio.create_task(self._execute_scan(job_id, path, 'local'))
        
        return job_id
    
    async def scan_github(self, repo_url: str, token: Optional[str] = None) -> str:
        """
        Scan a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            token: Optional GitHub token
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        logger.info(f"Starting GitHub scan {job_id} for: {repo_url}")
        
        # Validate URL
        if not self.github_loader.validate_url(repo_url):
            raise ValueError("Invalid GitHub repository URL")
        
        # Clone repository
        try:
            local_path = self.github_loader.clone_repository(repo_url, token)
        except Exception as e:
            logger.error(f"Failed to clone repository: {e}")
            raise
        
        # Run scan in background
        asyncio.create_task(
            self._execute_scan(job_id, local_path, 'github', repo_url)
        )
        
        return job_id
    
    async def _execute_scan(self, 
                           job_id: str, 
                           path: str, 
                           scan_type: str,
                           repo_url: Optional[str] = None):
        """
        Execute the actual scan.
        
        Args:
            job_id: Scan job identifier
            path: Path to scan
            scan_type: 'local' or 'github'
            repo_url: Original repository URL (for GitHub scans)
        """
        try:
            logger.info(f"Executing scan {job_id}")
            
            # Run all scanners
            logger.info("Running scanners...")
            
            secret_findings = self.secret_scanner.scan_directory(path, repo_url=repo_url, local_base_path=path)
            static_findings = self.static_scanner.scan_directory(path, repo_url=repo_url, local_base_path=path)
            dependency_findings = self.dependency_scanner.scan_directory(path, repo_url=repo_url, local_base_path=path)
            iac_findings = self.iac_scanner.scan_directory(path, repo_url=repo_url, local_base_path=path)
            
            # Combine all findings
            all_findings = (
                secret_findings + 
                static_findings + 
                dependency_findings + 
                iac_findings
            )
            
            logger.info(f"Scanners complete. Total findings: {len(all_findings)}")
            
            # Analyze with LLM
            if self.llm_analyzer:
                logger.info("Running LLM analysis...")
                analysis = self.llm_analyzer.analyze_findings(all_findings)
            else:
                logger.warning("Skipping LLM analysis (not configured)")
                analysis = {
                    'control_coverage': {},
                    'recommendations': [],
                    'risk_assessment': 'LLM analysis not available'
                }
            
            # Calculate scores
            logger.info("Calculating scores...")
            scoring = self.scoring_engine.calculate_readiness_score(
                all_findings,
                analysis.get('control_coverage', {})
            )
            
            # Generate metadata
            metadata = {
                'job_id': job_id,
                'scan_type': scan_type,
                'path': path,
                'repository': repo_url or path,
                'timestamp': datetime.now().isoformat(),
                'scanner_versions': {
                    'secret': '1.0',
                    'static': '1.0',
                    'dependency': '1.0',
                    'iac': '1.0'
                }
            }
            
            # Generate report
            logger.info("Generating report...")
            report = self.report_generator.generate_report(
                job_id,
                all_findings,
                analysis,
                scoring,
                metadata
            )
            
            logger.info(f"Scan {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error executing scan {job_id}: {e}")
            raise
    
    def get_report(self, job_id: str) -> Optional[Dict]:
        """
        Get report for a completed scan.
        
        Args:
            job_id: Scan job identifier
            
        Returns:
            Report data or None
        """
        return self.report_generator.load_report(job_id)
    
    def list_reports(self) -> List[Dict]:
        """
        List all available reports.
        
        Returns:
            List of report summaries
        """
        return self.report_generator.list_reports()
