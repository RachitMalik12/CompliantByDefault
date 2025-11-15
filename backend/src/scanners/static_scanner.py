import re
from pathlib import Path
from typing import List, Dict, Optional
import yaml
from ..utils.logger import logger
from ..utils.file_loader import FileLoader
from ..utils.github_url import GitHubURLConverter

class StaticScanner:
    """Scanner for static code analysis - security patterns and anti-patterns."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the static scanner with patterns from config."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "soc2_controls.yaml"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.security_patterns = config.get('patterns', {}).get('security', [])
        self.auth_patterns = config.get('patterns', {}).get('authentication', [])
        self.logging_patterns = config.get('patterns', {}).get('logging', [])
    
    def scan_file(self, file_path: Path, content: str) -> List[Dict]:
        """
        Scan a single file for security issues.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            List of findings
        """
        findings = []
        
        # Combine all pattern types
        all_patterns = (
            self.security_patterns + 
            self.auth_patterns + 
            self.logging_patterns
        )
        
        lines = content.split('\n')
        
        for pattern_def in all_patterns:
            pattern = pattern_def['pattern']
            try:
                regex = re.compile(pattern, re.MULTILINE | re.DOTALL)
                
                # Check full content for multi-line patterns
                matches = regex.finditer(content)
                for match in matches:
                    # Find line number
                    line_num = content[:match.start()].count('\n') + 1
                    
                    findings.append({
                        'type': pattern_def['name'],
                        'severity': pattern_def['severity'],
                        'file': str(file_path),
                        'line': line_num,
                        'message': f"Security issue: {pattern_def['name'].replace('_', ' ')}",
                        'control': pattern_def['control'],
                        'snippet': lines[line_num - 1].strip()[:100] if line_num <= len(lines) else '',
                        'recommendation': self._get_recommendation(pattern_def['name'])
                    })
            except re.error as e:
                logger.error(f"Invalid regex pattern {pattern}: {e}")
        
        return findings
    
    def _get_recommendation(self, issue_type: str) -> str:
        """Get remediation recommendation for an issue type."""
        recommendations = {
            'sql_injection_risk': 'Use parameterized queries or ORM instead of string concatenation',
            'insecure_random': 'Use cryptographically secure random generators (e.g., secrets module)',
            'disabled_ssl_verification': 'Enable SSL verification to prevent MITM attacks',
            'weak_crypto': 'Use SHA-256 or stronger hashing algorithms',
            'no_authentication': 'Add authentication decorators to protect endpoints',
            'weak_session': 'Enable permanent sessions with secure configuration',
            'missing_audit_log': 'Add audit logging for sensitive operations',
            'sensitive_data_logging': 'Avoid logging sensitive data like passwords and tokens'
        }
        return recommendations.get(issue_type, 'Review and remediate this security issue')
    
    def scan_directory(self, root_path: str, repo_url: Optional[str] = None, local_base_path: Optional[str] = None) -> List[Dict]:
        """
        Scan entire directory for security issues.
        
        Args:
            root_path: Root directory to scan
            repo_url: GitHub repository URL (optional)
            local_base_path: Base path of cloned repository (optional)
            
        Returns:
            List of all findings
        """
        logger.info("Starting static code analysis...")
        all_findings = []
        
        files = FileLoader.get_all_files(root_path)
        
        for file_path in files:
            # Focus on code files
            if file_path.suffix in ['.py', '.js', '.ts', '.tsx', '.java', '.go', '.rb', '.php']:
                content = FileLoader.read_file(file_path)
                if content:
                    findings = self.scan_file(file_path, content)
                    
                    # Convert file paths to GitHub URLs if applicable
                    if repo_url and local_base_path:
                        findings = [
                            GitHubURLConverter.update_finding_with_github_url(
                                finding, repo_url, local_base_path
                            )
                            for finding in findings
                        ]
                    
                    all_findings.extend(findings)
        
        logger.info(f"Static analysis complete. Found {len(all_findings)} issues")
        return all_findings
