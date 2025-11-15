import os
from typing import List, Dict, Optional
import google.generativeai as genai
from pathlib import Path
import yaml
import json
from ..utils.logger import logger

class LLMAnalyzer:
    """Uses Gemini to analyze security findings and map to SOC 2 controls."""
    
    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the LLM analyzer.
        
        Args:
            api_key: Gemini API key (defaults to env var)
            config_path: Path to SOC2 controls config
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Load SOC2 controls
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "soc2_controls.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.controls = self.config.get('controls', {})
    
    def analyze_findings(self, findings: List[Dict]) -> Dict:
        """
        Analyze all findings and generate comprehensive SOC 2 compliance report.
        
        Args:
            findings: List of findings from all scanners
            
        Returns:
            Analysis results with control mappings and recommendations
        """
        if not findings:
            logger.info("No findings to analyze")
            return {
                'control_coverage': {},
                'recommendations': [],
                'risk_assessment': 'Low - No security issues detected'
            }
        
        logger.info(f"Analyzing {len(findings)} findings with Gemini...")
        
        # Group findings by control
        control_findings = self._group_by_control(findings)
        
        # Prepare summary for LLM
        summary = self._prepare_summary(findings, control_findings)
        
        # Get LLM analysis
        llm_analysis = self._get_llm_analysis(summary)
        
        # Map findings to controls
        control_coverage = self._calculate_control_coverage(control_findings)
        
        return {
            'control_coverage': control_coverage,
            'llm_insights': llm_analysis,
            'recommendations': self._generate_recommendations(control_findings),
            'risk_assessment': self._assess_risk(findings)
        }
    
    def _group_by_control(self, findings: List[Dict]) -> Dict[str, List[Dict]]:
        """Group findings by SOC 2 control."""
        grouped = {}
        
        for finding in findings:
            control = finding.get('control', 'Unknown')
            if control not in grouped:
                grouped[control] = []
            grouped[control].append(finding)
        
        return grouped
    
    def _prepare_summary(self, findings: List[Dict], control_findings: Dict) -> str:
        """Prepare a summary of findings for LLM analysis."""
        severity_counts = {}
        for finding in findings:
            severity = finding.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        summary = f"""
Security Scan Results Summary:
Total Findings: {len(findings)}

Severity Distribution:
{json.dumps(severity_counts, indent=2)}

Findings by SOC 2 Control:
"""
        
        for control_id, control_items in sorted(control_findings.items()):
            control_info = self.controls.get(control_id, {})
            control_name = control_info.get('name', control_id)
            summary += f"\n{control_id} - {control_name}: {len(control_items)} findings\n"
            
            # Add sample findings
            for finding in control_items[:3]:  # First 3 as examples
                summary += f"  - {finding.get('type', 'unknown')}: {finding.get('message', '')}\n"
        
        return summary
    
    def _get_llm_analysis(self, summary: str) -> Dict:
        """Get analysis from Gemini."""
        prompt = f"""
You are a SOC 2 compliance expert analyzing security scan results.

{summary}

Provide a comprehensive analysis covering:
1. Overall security posture assessment
2. Critical risks that need immediate attention
3. SOC 2 compliance gaps
4. Top 5 recommended actions prioritized by impact
5. Long-term security improvements

Format your response as JSON with keys: posture, critical_risks, compliance_gaps, top_actions, long_term_improvements
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text
            
            # Try to parse as JSON
            try:
                # Remove markdown code blocks if present
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0].strip()
                elif '```' in response_text:
                    response_text = response_text.split('```')[1].split('```')[0].strip()
                
                analysis = json.loads(response_text)
            except json.JSONDecodeError:
                # If not valid JSON, structure the response
                analysis = {
                    'posture': response_text[:500],
                    'critical_risks': ['Parse LLM response for detailed analysis'],
                    'compliance_gaps': ['Review findings by control'],
                    'top_actions': ['Address critical and high severity issues first'],
                    'long_term_improvements': ['Implement continuous security monitoring']
                }
            
            logger.info("LLM analysis completed successfully")
            return analysis
        
        except Exception as e:
            logger.error(f"Error getting LLM analysis: {e}")
            return {
                'posture': 'Analysis unavailable',
                'critical_risks': [],
                'compliance_gaps': [],
                'top_actions': [],
                'long_term_improvements': [],
                'error': str(e)
            }
    
    def _calculate_control_coverage(self, control_findings: Dict) -> Dict:
        """Calculate coverage and compliance for each control."""
        coverage = {}
        
        for control_id, control_info in self.controls.items():
            findings_count = len(control_findings.get(control_id, []))
            
            # Calculate severity score for this control
            severity_score = 0
            findings_list = control_findings.get(control_id, [])
            for finding in findings_list:
                severity = finding.get('severity', 'info')
                severity_score += self.config.get('severity_weights', {}).get(severity, 1)
            
            # Determine status
            if findings_count == 0:
                status = 'compliant'
                score = 100
            elif findings_count <= 2 and severity_score < 10:
                status = 'partial'
                score = 70
            else:
                status = 'non_compliant'
                score = max(0, 100 - (findings_count * 10) - severity_score)
            
            coverage[control_id] = {
                'name': control_info.get('name', ''),
                'description': control_info.get('description', ''),
                'findings_count': findings_count,
                'severity_score': severity_score,
                'status': status,
                'score': score
            }
        
        return coverage
    
    def _generate_recommendations(self, control_findings: Dict) -> List[Dict]:
        """Generate prioritized recommendations."""
        recommendations = []
        
        # Group by severity
        critical_findings = []
        high_findings = []
        
        for control_id, findings in control_findings.items():
            for finding in findings:
                if finding.get('severity') == 'critical':
                    critical_findings.append((control_id, finding))
                elif finding.get('severity') == 'high':
                    high_findings.append((control_id, finding))
        
        # Add critical recommendations
        for control_id, finding in critical_findings[:5]:  # Top 5 critical
            recommendations.append({
                'priority': 'critical',
                'control': control_id,
                'issue': finding.get('message', ''),
                'action': finding.get('recommendation', 'Review and remediate'),
                'file': finding.get('file', '')
            })
        
        # Add high priority recommendations
        for control_id, finding in high_findings[:5]:  # Top 5 high
            recommendations.append({
                'priority': 'high',
                'control': control_id,
                'issue': finding.get('message', ''),
                'action': finding.get('recommendation', 'Review and remediate'),
                'file': finding.get('file', '')
            })
        
        return recommendations
    
    def _assess_risk(self, findings: List[Dict]) -> str:
        """Assess overall risk level."""
        critical_count = sum(1 for f in findings if f.get('severity') == 'critical')
        high_count = sum(1 for f in findings if f.get('severity') == 'high')
        
        if critical_count > 5:
            return 'Critical - Multiple critical security issues require immediate attention'
        elif critical_count > 0:
            return f'High - {critical_count} critical issue(s) detected'
        elif high_count > 10:
            return f'High - {high_count} high-severity issues detected'
        elif high_count > 0:
            return f'Medium - {high_count} high-severity issue(s) to address'
        else:
            return 'Low - No critical or high-severity issues detected'
    
    def get_control_mapping(self, finding: Dict) -> str:
        """Map a finding to appropriate SOC 2 control."""
        # This could be enhanced with LLM for more accurate mapping
        return finding.get('control', 'Unknown')
