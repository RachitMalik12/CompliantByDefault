import re
from pathlib import Path
from typing import List, Dict, Optional
import yaml
import os
import google.generativeai as genai
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
        
        # Initialize Gemini for second-pass validation
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not found - second-pass validation disabled")
    
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
        
        logger.info(f"Static analysis complete. Found {len(all_findings)} potential issues")
        
        # Second pass: validate findings to reduce false positives
        if all_findings and self.model:
            logger.info("Running second-pass validation to filter false positives...")
            all_findings = self._validate_findings(all_findings, root_path)
            logger.info(f"After validation: {len(all_findings)} confirmed issues")
        
        return all_findings
    
    def _validate_findings(self, findings: List[Dict], root_path: str) -> List[Dict]:
        """
        Second pass: validate findings using LLM to reduce false positives.
        Groups findings by file and analyzes context efficiently.
        
        Args:
            findings: Initial findings from pattern matching
            root_path: Root directory path for reading full context
            
        Returns:
            Filtered list of validated findings
        """
        if not findings:
            return findings
        
        # Group findings by file for efficient batch analysis
        findings_by_file = {}
        for finding in findings:
            file_path = finding.get('file', '')
            if file_path not in findings_by_file:
                findings_by_file[file_path] = []
            findings_by_file[file_path].append(finding)
        
        validated_findings = []
        
        # Process each file's findings in a single LLM call
        for file_path, file_findings in findings_by_file.items():
            # Read file content for context
            try:
                # Handle both GitHub URLs and local paths
                if file_path.startswith('https://github.com/'):
                    # Extract local path from GitHub URL
                    match = re.search(r'/blob/[^/]+/(.+?)(?:#|$)', file_path)
                    if match:
                        local_file = Path(root_path) / match.group(1)
                    else:
                        continue
                else:
                    local_file = Path(file_path)
                
                if not local_file.exists():
                    # If file doesn't exist, keep findings (better safe than sorry)
                    validated_findings.extend(file_findings)
                    continue
                
                content = local_file.read_text(encoding='utf-8', errors='ignore')
                
                # Validate this batch of findings
                valid_findings = self._validate_file_findings(file_findings, content, str(local_file))
                validated_findings.extend(valid_findings)
                
            except Exception as e:
                logger.warning(f"Error validating findings for {file_path}: {e}")
                # On error, keep findings to avoid missing real issues
                validated_findings.extend(file_findings)
        
        return validated_findings
    
    def _validate_file_findings(self, findings: List[Dict], file_content: str, file_path: str) -> List[Dict]:
        """
        Validate findings for a single file using LLM context analysis.
        
        Args:
            findings: Findings for this file
            file_content: Full file content
            file_path: Path to the file
            
        Returns:
            List of validated findings (false positives removed)
        """
        if not findings or not self.model:
            return findings
        
        # Prepare concise summary of findings for LLM
        findings_summary = []
        for idx, finding in enumerate(findings):
            line_num = finding.get('line', 0)
            findings_summary.append({
                'id': idx,
                'type': finding.get('type', ''),
                'line': line_num,
                'message': finding.get('message', ''),
                'control': finding.get('control', ''),
                'snippet': finding.get('snippet', '')
            })
        
        # Extract relevant code context (lines around findings)
        lines = file_content.split('\n')
        context_snippets = []
        for finding in findings:
            line_num = finding.get('line', 0)
            start = max(0, line_num - 3)
            end = min(len(lines), line_num + 2)
            snippet = '\n'.join(f"{i+1}: {lines[i]}" for i in range(start, end))
            context_snippets.append(snippet)
        
        prompt = f"""You are a security expert analyzing code for false positives in SOC 2 compliance scanning.

File: {Path(file_path).name}

Potential Issues Found ({len(findings)}):
{chr(10).join([f"{i+1}. {f['type']} at line {f['line']}: {f['message']}" for i, f in enumerate(findings_summary)])}

Code Context:
{chr(10).join([f"Finding {i+1} context:\n{snippet}\n" for i, snippet in enumerate(context_snippets)])}

Task: Analyze each finding and determine if it's a TRUE POSITIVE or FALSE POSITIVE.

Common false positive patterns to filter out:
- Test files or mock implementations (unless they demonstrate actual vulnerabilities)
- Comments or documentation mentioning security issues
- Already-mitigated code (e.g., SQL injection in parameterized queries)
- Configuration for development/testing environments clearly marked as such
- Code that appears vulnerable but has proper validation elsewhere

Respond with a JSON array of finding IDs (0-based) that are TRUE POSITIVES only.
Format: {{"valid_findings": [0, 2, 4]}}

Be conservative - if unsure, mark as true positive. Only filter obvious false positives."""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse response
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            import json
            result = json.loads(response_text)
            valid_ids = result.get('valid_findings', [])
            
            # Return only validated findings
            validated = [findings[i] for i in valid_ids if i < len(findings)]
            
            filtered_count = len(findings) - len(validated)
            if filtered_count > 0:
                logger.info(f"Filtered {filtered_count} false positive(s) from {Path(file_path).name}")
            
            return validated
            
        except Exception as e:
            logger.warning(f"Validation failed for {file_path}: {e}. Keeping all findings.")
            # On error, keep all findings (fail-safe)
            return findings
