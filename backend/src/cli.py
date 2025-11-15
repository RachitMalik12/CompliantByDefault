#!/usr/bin/env python3
"""
CompliantByDefault CLI - SOC 2 Readiness Agent
"""
import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional
import json
from dotenv import load_dotenv

from .main import ScanEngine
from .utils.logger import logger

# Load environment variables
load_dotenv()

class CLI:
    """Command-line interface for CompliantByDefault."""
    
    def __init__(self):
        self.scan_engine = ScanEngine()
    
    async def scan_local(self, path: str, output: Optional[str] = None):
        """Scan a local directory."""
        print(f"🔍 Scanning local directory: {path}\n")
        
        # Validate path
        if not Path(path).exists():
            print(f"❌ Error: Path does not exist: {path}")
            sys.exit(1)
        
        try:
            job_id = await self.scan_engine.scan_local(path)
            print(f"✅ Scan started with job ID: {job_id}")
            print("⏳ Running scanners...\n")
            
            # Wait for scan to complete (in CLI, we wait synchronously)
            await asyncio.sleep(2)  # Give it a moment to start
            
            # Poll for completion
            max_attempts = 60  # 60 seconds max
            for i in range(max_attempts):
                report = self.scan_engine.get_report(job_id)
                if report:
                    self._display_report(report)
                    
                    if output:
                        self._save_output(report, output)
                    
                    return
                
                await asyncio.sleep(1)
                if i % 5 == 0:
                    print(f"⏳ Still scanning... ({i}s)")
            
            print("⏰ Scan timed out. Check reports later with: cli.py report <job_id>")
        
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    async def scan_github(self, repo_url: str, token: Optional[str] = None, 
                         output: Optional[str] = None):
        """Scan a GitHub repository."""
        print(f"🔍 Scanning GitHub repository: {repo_url}\n")
        
        try:
            job_id = await self.scan_engine.scan_github(repo_url, token)
            print(f"✅ Scan started with job ID: {job_id}")
            print("📥 Cloning repository...")
            print("⏳ Running scanners...\n")
            
            # Wait for scan to complete
            await asyncio.sleep(5)  # Give it time to clone and scan
            
            # Poll for completion
            max_attempts = 120  # 2 minutes max
            for i in range(max_attempts):
                report = self.scan_engine.get_report(job_id)
                if report:
                    self._display_report(report)
                    
                    if output:
                        self._save_output(report, output)
                    
                    return
                
                await asyncio.sleep(1)
                if i % 10 == 0 and i > 0:
                    print(f"⏳ Still scanning... ({i}s)")
            
            print("⏰ Scan timed out. Check reports later with: cli.py report <job_id>")
        
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def get_report(self, job_id: str, output: Optional[str] = None):
        """Get an existing report."""
        report = self.scan_engine.get_report(job_id)
        
        if not report:
            print(f"❌ Report not found: {job_id}")
            sys.exit(1)
        
        self._display_report(report)
        
        if output:
            self._save_output(report, output)
    
    def list_reports(self):
        """List all reports."""
        reports = self.scan_engine.list_reports()
        
        if not reports:
            print("📭 No reports found.")
            return
        
        print(f"📊 Found {len(reports)} report(s):\n")
        print(f"{'Job ID':<40} {'Score':<8} {'Findings':<10} {'Generated At':<20}")
        print("-" * 80)
        
        for report in reports:
            job_id = report.get('id', 'N/A')
            score = report.get('score', 'N/A')
            findings = report.get('findings', 'N/A')
            generated = report.get('generated_at', 'N/A')[:19]  # Truncate timestamp
            
            print(f"{job_id:<40} {score:<8} {findings:<10} {generated:<20}")
    
    def _display_report(self, report: dict):
        """Display report summary in terminal."""
        summary = report.get('summary', {})
        score = report.get('score', {})
        analysis = report.get('analysis', {})
        
        print("\n" + "="*80)
        print("📊 SOC 2 COMPLIANCE REPORT")
        print("="*80 + "\n")
        
        # Summary
        print(f"🎯 Overall Score: {summary.get('readiness_score', 0)}/100 (Grade: {summary.get('grade', 'N/A')})")
        print(f"⚠️  Total Findings: {summary.get('total_findings', 0)}")
        print(f"🔐 Risk Level: {summary.get('risk_level', 'Unknown')}")
        print(f"✅ Controls Compliant: {score.get('controls_compliant', 0)}/{score.get('controls_total', 0)}")
        print()
        
        # Severity breakdown
        severity_counts = score.get('severity_impact', {}).get('counts', {})
        print("📈 Severity Distribution:")
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                print(f"   {severity.upper()}: {count}")
        print()
        
        # LLM insights
        if analysis:
            posture = analysis.get('posture', '')
            if posture:
                print("🤖 AI Analysis:")
                print(f"   {posture[:200]}...")
                print()
        
        # Top recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            print("💡 Top Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"   {i}. [{rec.get('priority', 'medium').upper()}] {rec.get('issue', 'N/A')}")
                print(f"      → {rec.get('action', 'Review and remediate')}")
            print()
        
        # Report files
        report_files = report.get('report_files', {})
        if report_files:
            print("📄 Report Files:")
            if report_files.get('json'):
                print(f"   JSON: {report_files['json']}")
            if report_files.get('markdown'):
                print(f"   Markdown: {report_files['markdown']}")
        
        print("\n" + "="*80 + "\n")
    
    def _save_output(self, report: dict, output_path: str):
        """Save report to specified output file."""
        output = Path(output_path)
        
        try:
            with open(output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"💾 Report saved to: {output}")
        except Exception as e:
            print(f"❌ Error saving output: {e}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CompliantByDefault - SOC 2 Readiness Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Scan local command
    scan_local_parser = subparsers.add_parser('scan-local', help='Scan a local directory')
    scan_local_parser.add_argument('path', help='Path to directory to scan')
    scan_local_parser.add_argument('-o', '--output', help='Output file for JSON report')
    
    # Scan GitHub command
    scan_github_parser = subparsers.add_parser('scan-github', help='Scan a GitHub repository')
    scan_github_parser.add_argument('repo_url', help='GitHub repository URL')
    scan_github_parser.add_argument('-t', '--token', help='GitHub personal access token')
    scan_github_parser.add_argument('-o', '--output', help='Output file for JSON report')
    
    # Get report command
    report_parser = subparsers.add_parser('report', help='Get an existing report')
    report_parser.add_argument('job_id', help='Job ID of the scan')
    report_parser.add_argument('-o', '--output', help='Output file for JSON report')
    
    # List reports command
    subparsers.add_parser('list', help='List all reports')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = CLI()
    
    try:
        if args.command == 'scan-local':
            asyncio.run(cli.scan_local(args.path, args.output))
        elif args.command == 'scan-github':
            asyncio.run(cli.scan_github(args.repo_url, args.token, args.output))
        elif args.command == 'report':
            cli.get_report(args.job_id, args.output)
        elif args.command == 'list':
            cli.list_reports()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)

if __name__ == '__main__':
    main()
