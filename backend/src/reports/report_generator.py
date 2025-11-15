import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from ..utils.logger import logger

class ReportGenerator:
    """Generate compliance reports in JSON and Markdown formats."""
    
    def __init__(self, output_dir: str = "./reports"):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, 
                       job_id: str,
                       findings: List[Dict],
                       analysis: Dict,
                       scoring: Dict,
                       metadata: Dict) -> Dict:
        """
        Generate comprehensive compliance report.
        
        Args:
            job_id: Unique identifier for the scan
            findings: All findings from scanners
            analysis: LLM analysis results
            scoring: Scoring metrics
            metadata: Scan metadata (repo, timestamp, etc.)
            
        Returns:
            Report data dictionary
        """
        logger.info(f"Generating report for job {job_id}")
        
        report = {
            'id': job_id,
            'generated_at': datetime.now().isoformat(),
            'metadata': metadata,
            'summary': {
                'total_findings': len(findings),
                'readiness_score': scoring.get('overall_score', 0),
                'grade': scoring.get('grade', 'N/A'),
                'risk_level': analysis.get('risk_assessment', 'Unknown')
            },
            'score': scoring,
            'controls': analysis.get('control_coverage', {}),
            'findings': findings,
            'analysis': analysis.get('llm_insights', {}),
            'recommendations': analysis.get('recommendations', [])
        }
        
        # Save JSON report
        json_path = self._save_json(job_id, report)
        logger.info(f"JSON report saved: {json_path}")
        
        # Save Markdown report
        md_path = self._save_markdown(job_id, report)
        logger.info(f"Markdown report saved: {md_path}")
        
        report['report_files'] = {
            'json': str(json_path),
            'markdown': str(md_path)
        }
        
        return report
    
    def _save_json(self, job_id: str, report: Dict) -> Path:
        """Save report as JSON."""
        file_path = self.output_dir / f"{job_id}_report.json"
        
        with open(file_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return file_path
    
    def _save_markdown(self, job_id: str, report: Dict) -> Path:
        """Save report as Markdown."""
        file_path = self.output_dir / f"{job_id}_report.md"
        
        md_content = self._generate_markdown(report)
        
        with open(file_path, 'w') as f:
            f.write(md_content)
        
        return file_path
    
    def _generate_markdown(self, report: Dict) -> str:
        """Generate Markdown content for report."""
        summary = report.get('summary', {})
        score = report.get('score', {})
        controls = report.get('controls', {})
        findings = report.get('findings', [])
        analysis = report.get('analysis', {})
        recommendations = report.get('recommendations', [])
        metadata = report.get('metadata', {})
        
        md = f"""# SOC 2 Compliance Report

**Report ID:** {report.get('id', 'N/A')}  
**Generated:** {report.get('generated_at', 'N/A')}  
**Repository:** {metadata.get('repository', metadata.get('path', 'N/A'))}

---

## Executive Summary

### Overall Readiness Score: {summary.get('readiness_score', 0)}/100 (Grade: {summary.get('grade', 'N/A')})

- **Total Findings:** {summary.get('total_findings', 0)}
- **Risk Level:** {summary.get('risk_level', 'Unknown')}
- **Controls Compliant:** {score.get('controls_compliant', 0)}/{score.get('controls_total', 0)}

### Risk Assessment

{analysis.get('posture', 'No assessment available')}

---

## Severity Distribution

"""
        
        severity_impact = score.get('severity_impact', {})
        severity_counts = severity_impact.get('counts', {})
        
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = severity_counts.get(severity, 0)
            md += f"- **{severity.upper()}:** {count}\n"
        
        md += "\n---\n\n## SOC 2 Control Coverage\n\n"
        
        # Control coverage table
        md += "| Control | Name | Status | Score | Findings |\n"
        md += "|---------|------|--------|-------|----------|\n"
        
        for control_id, control_data in sorted(controls.items()):
            status = control_data.get('status', 'unknown')
            status_emoji = {
                'compliant': '✅',
                'partial': '⚠️',
                'non_compliant': '❌',
                'unknown': '❓'
            }.get(status, '❓')
            
            md += f"| {control_id} | {control_data.get('name', '')} | {status_emoji} {status} | {control_data.get('score', 0)} | {control_data.get('findings_count', 0)} |\n"
        
        md += "\n---\n\n## Top Recommendations\n\n"
        
        for i, rec in enumerate(recommendations[:10], 1):
            md += f"### {i}. {rec.get('issue', 'Issue')}\n\n"
            md += f"**Priority:** {rec.get('priority', 'medium').upper()}  \n"
            md += f"**Control:** {rec.get('control', 'N/A')}  \n"
            md += f"**File:** `{rec.get('file', 'N/A')}`  \n\n"
            md += f"**Action:** {rec.get('action', 'Review and remediate')}\n\n"
        
        md += "---\n\n## LLM Analysis\n\n"
        
        # Critical risks
        critical_risks = analysis.get('critical_risks', [])
        if critical_risks and isinstance(critical_risks, list):
            md += "### Critical Risks\n\n"
            for risk in critical_risks:
                md += f"- {risk}\n"
            md += "\n"
        
        # Compliance gaps
        compliance_gaps = analysis.get('compliance_gaps', [])
        if compliance_gaps and isinstance(compliance_gaps, list):
            md += "### Compliance Gaps\n\n"
            for gap in compliance_gaps:
                md += f"- {gap}\n"
            md += "\n"
        
        # Top actions
        top_actions = analysis.get('top_actions', [])
        if top_actions and isinstance(top_actions, list):
            md += "### Recommended Actions\n\n"
            for action in top_actions:
                md += f"1. {action}\n"
            md += "\n"
        
        md += "---\n\n## Detailed Findings\n\n"
        
        # Group findings by severity
        findings_by_severity = {}
        for finding in findings:
            severity = finding.get('severity', 'info')
            if severity not in findings_by_severity:
                findings_by_severity[severity] = []
            findings_by_severity[severity].append(finding)
        
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            if severity in findings_by_severity:
                md += f"### {severity.upper()} Severity\n\n"
                
                for finding in findings_by_severity[severity][:20]:  # Limit to 20 per severity
                    md += f"**{finding.get('type', 'Issue').replace('_', ' ').title()}**  \n"
                    md += f"📁 File: `{finding.get('file', 'N/A')}`  \n"
                    md += f"📍 Line: {finding.get('line', 'N/A')}  \n"
                    md += f"🎯 Control: {finding.get('control', 'N/A')}  \n"
                    md += f"💬 {finding.get('message', 'No message')}  \n"
                    
                    if finding.get('recommendation'):
                        md += f"💡 *Recommendation:* {finding.get('recommendation')}  \n"
                    
                    md += "\n---\n\n"
        
        md += "## Conclusion\n\n"
        md += f"This report analyzed {len(findings)} findings across {score.get('controls_total', 0)} SOC 2 controls. "
        md += f"The repository achieved a readiness score of {summary.get('readiness_score', 0)}/100. "
        md += "Address the critical and high-priority findings first to improve your security posture.\n\n"
        md += "---\n\n"
        md += "*Generated by CompliantByDefault - SOC 2 Readiness Agent*\n"
        
        return md
    
    def load_report(self, job_id: str) -> Optional[Dict]:
        """
        Load an existing report.
        
        Args:
            job_id: Report identifier
            
        Returns:
            Report data or None if not found
        """
        file_path = self.output_dir / f"{job_id}_report.json"
        
        if not file_path.exists():
            logger.warning(f"Report not found: {job_id}")
            return None
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading report: {e}")
            return None
    
    def list_reports(self) -> List[Dict]:
        """
        List all available reports.
        
        Returns:
            List of report summaries
        """
        reports = []
        
        for json_file in self.output_dir.glob("*_report.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    reports.append({
                        'id': data.get('id'),
                        'generated_at': data.get('generated_at'),
                        'score': data.get('summary', {}).get('readiness_score'),
                        'findings': data.get('summary', {}).get('total_findings'),
                        'repository': data.get('metadata', {}).get('repository', 'Unknown')
                    })
            except Exception as e:
                logger.error(f"Error reading report {json_file}: {e}")
        
        return sorted(reports, key=lambda x: x.get('generated_at', ''), reverse=True)
