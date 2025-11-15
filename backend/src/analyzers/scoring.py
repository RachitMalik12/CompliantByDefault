from typing import List, Dict
import yaml
from pathlib import Path
from ..utils.logger import logger

class ScoringEngine:
    """Calculate compliance scores and metrics."""
    
    def __init__(self, config_path: str = None):
        """Initialize scoring engine with SOC2 controls config."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "soc2_controls.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.severity_weights = self.config.get('severity_weights', {
            'critical': 10,
            'high': 7,
            'medium': 4,
            'low': 2,
            'info': 1
        })
        
        self.controls = self.config.get('controls', {})
    
    def calculate_readiness_score(self, findings: List[Dict], 
                                  control_coverage: Dict) -> Dict:
        """
        Calculate overall SOC 2 readiness score.
        
        Args:
            findings: List of all findings
            control_coverage: Control coverage data from analyzer
            
        Returns:
            Scoring metrics and breakdown
        """
        if not findings:
            return {
                'overall_score': 100,
                'grade': 'A',
                'severity_impact': {},
                'control_scores': {},
                'total_issues': 0
            }
        
        # Calculate severity impact
        severity_counts = {}
        total_severity_score = 0
        
        for finding in findings:
            severity = finding.get('severity', 'info')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            total_severity_score += self.severity_weights.get(severity, 1)
        
        # Calculate base score (100 - severity impact)
        # Max possible deduction is 100 points
        max_score = 100
        severity_deduction = min(total_severity_score, max_score)
        base_score = max_score - severity_deduction
        
        # Calculate control coverage score
        control_scores = {}
        total_controls = len(self.controls)
        compliant_controls = 0
        
        for control_id, coverage in control_coverage.items():
            control_score = coverage.get('score', 0)
            control_scores[control_id] = {
                'score': control_score,
                'status': coverage.get('status', 'unknown'),
                'name': coverage.get('name', ''),
                'findings': coverage.get('findings_count', 0)
            }
            
            if coverage.get('status') == 'compliant':
                compliant_controls += 1
        
        coverage_percentage = (compliant_controls / total_controls * 100) if total_controls > 0 else 0
        
        # Weighted final score (70% severity, 30% coverage)
        final_score = (base_score * 0.7) + (coverage_percentage * 0.3)
        final_score = max(0, min(100, round(final_score)))
        
        # Determine grade
        grade = self._calculate_grade(final_score)
        
        logger.info(f"Calculated readiness score: {final_score} (Grade: {grade})")
        
        return {
            'overall_score': final_score,
            'grade': grade,
            'base_score': round(base_score, 1),
            'coverage_score': round(coverage_percentage, 1),
            'severity_impact': {
                'counts': severity_counts,
                'total_weight': total_severity_score,
                'deduction': severity_deduction
            },
            'control_scores': control_scores,
            'total_issues': len(findings),
            'controls_compliant': compliant_controls,
            'controls_total': total_controls
        }
    
    def _calculate_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def calculate_risk_score(self, findings: List[Dict]) -> Dict:
        """
        Calculate risk metrics.
        
        Args:
            findings: List of findings
            
        Returns:
            Risk assessment metrics
        """
        critical_count = sum(1 for f in findings if f.get('severity') == 'critical')
        high_count = sum(1 for f in findings if f.get('severity') == 'high')
        medium_count = sum(1 for f in findings if f.get('severity') == 'medium')
        low_count = sum(1 for f in findings if f.get('severity') == 'low')
        
        # Calculate risk score (0-100, higher is worse)
        risk_score = (
            critical_count * self.severity_weights['critical'] +
            high_count * self.severity_weights['high'] +
            medium_count * self.severity_weights['medium'] +
            low_count * self.severity_weights['low']
        )
        
        # Normalize to 0-100 scale (assuming max realistic is 200)
        normalized_risk = min(100, (risk_score / 200) * 100)
        
        # Determine risk level
        if normalized_risk >= 75:
            risk_level = 'Critical'
        elif normalized_risk >= 50:
            risk_level = 'High'
        elif normalized_risk >= 25:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        return {
            'risk_score': round(normalized_risk, 1),
            'risk_level': risk_level,
            'severity_breakdown': {
                'critical': critical_count,
                'high': high_count,
                'medium': medium_count,
                'low': low_count
            }
        }
    
    def get_priority_findings(self, findings: List[Dict], limit: int = 10) -> List[Dict]:
        """
        Get top priority findings to fix.
        
        Args:
            findings: List of all findings
            limit: Maximum number to return
            
        Returns:
            Prioritized list of findings
        """
        # Sort by severity weight (descending)
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        
        sorted_findings = sorted(
            findings,
            key=lambda x: (
                severity_order.get(x.get('severity', 'info'), 5),
                x.get('file', '')
            )
        )
        
        return sorted_findings[:limit]
    
    def calculate_control_impact(self, findings: List[Dict]) -> Dict[str, int]:
        """
        Calculate which controls are most impacted.
        
        Args:
            findings: List of findings
            
        Returns:
            Dictionary of control IDs to impact scores
        """
        control_impact = {}
        
        for finding in findings:
            control = finding.get('control', 'Unknown')
            severity = finding.get('severity', 'info')
            weight = self.severity_weights.get(severity, 1)
            
            control_impact[control] = control_impact.get(control, 0) + weight
        
        return dict(sorted(control_impact.items(), key=lambda x: x[1], reverse=True))
