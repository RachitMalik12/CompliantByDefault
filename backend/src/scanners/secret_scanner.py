import re
from pathlib import Path
from typing import List, Dict, Optional
import yaml
from ..utils.logger import logger
from ..utils.file_loader import FileLoader

class SecretScanner:
    """Scanner for detecting secrets and sensitive information in code."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the secret scanner with patterns from config."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "soc2_controls.yaml"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.patterns = config.get('patterns', {}).get('secrets', [])
        self.high_risk_files = config.get('file_patterns', {}).get('high_risk', [])
    
    def scan_file(self, file_path: Path, content: str) -> List[Dict]:
        """
        Scan a single file for secrets.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            List of findings
        """
        findings = []
        
        # Check if file itself is high risk
        if any(file_path.match(pattern) for pattern in self.high_risk_files):
            findings.append({
                'type': 'high_risk_file',
                'severity': 'high',
                'file': str(file_path),
                'line': 0,
                'message': f'High-risk file detected: {file_path.name}',
                'control': 'CC9',
                'pattern': file_path.name
            })
        
        # Scan content for secret patterns
        lines = content.split('\n')
        for pattern_def in self.patterns:
            pattern = pattern_def['pattern']
            try:
                regex = re.compile(pattern)
                for line_num, line in enumerate(lines, 1):
                    matches = regex.finditer(line)
                    for match in matches:
                        findings.append({
                            'type': pattern_def['name'],
                            'severity': pattern_def['severity'],
                            'file': str(file_path),
                            'line': line_num,
                            'message': f"Potential {pattern_def['name'].replace('_', ' ')} detected",
                            'control': pattern_def['control'],
                            'snippet': line.strip()[:100],
                            'matched_text': match.group(0)[:50]  # Truncate for safety
                        })
            except re.error as e:
                logger.error(f"Invalid regex pattern {pattern}: {e}")
        
        return findings
    
    def scan_directory(self, root_path: str) -> List[Dict]:
        """
        Scan entire directory for secrets.
        
        Args:
            root_path: Root directory to scan
            
        Returns:
            List of all findings
        """
        logger.info("Starting secret scan...")
        all_findings = []
        
        files = FileLoader.get_all_files(root_path)
        
        for file_path in files:
            content = FileLoader.read_file(file_path)
            if content:
                findings = self.scan_file(file_path, content)
                all_findings.extend(findings)
        
        logger.info(f"Secret scan complete. Found {len(all_findings)} issues")
        return all_findings
