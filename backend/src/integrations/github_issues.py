"""
GitHub issue creation utility for SOC 2 compliance findings.
"""
import os
import requests
from typing import Dict, Optional
from ..utils.logger import logger
from ..config.expertise_mapping import get_assignee_for_control


class GitHubIssueCreator:
    """Creates GitHub issues for compliance findings."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub issue creator.
        
        Args:
            token: GitHub personal access token
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable.")
        
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    
    def extract_repo_info(self, repo_url: str) -> Optional[Dict[str, str]]:
        """
        Extract owner and repo name from GitHub URL.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dict with 'owner' and 'repo' keys, or None if invalid
        """
        import re
        patterns = [
            r'github\.com[/:]([^/]+)/([^/\.]+?)(?:\.git)?$',
            r'github\.com[/:]([^/]+)/([^/]+?)/?$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                return {
                    'owner': match.group(1),
                    'repo': match.group(2)
                }
        
        return None
    
    def format_issue_body(self, finding: Dict) -> str:
        """
        Format the issue body with compliance finding details.
        
        Args:
            finding: Finding dictionary with issue details
            
        Returns:
            Formatted markdown body for the issue
        """
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🔵',
            'info': '⚪'
        }
        
        emoji = severity_emoji.get(finding.get('severity', 'medium'), '🟡')
        
        body = f"""## {emoji} SOC 2 Compliance Issue Detected

### Issue Details
**Control:** {finding.get('control', 'N/A')} - {self._get_control_name(finding.get('control', ''))}
**Type:** {finding.get('type', 'Unknown').replace('_', ' ').title()}
**Severity:** {finding.get('severity', 'medium').upper()}
**Assigned to:** @{self._get_assignee_for_display(finding.get('control', ''))}

### Summary of Risk
{finding.get('message', 'Security or compliance issue detected.')}

### Risk Level
**{finding.get('severity', 'medium').upper()}** - {self._get_risk_description(finding.get('severity', 'medium'))}

### Location
"""
        
        if finding.get('file'):
            file_path = finding['file']
            if file_path.startswith('https://github.com/'):
                body += f"**File:** [{file_path.split('/')[-1].split('#')[0]}]({file_path})\n"
            else:
                body += f"**File:** `{file_path}`\n"
        
        if finding.get('line'):
            body += f"**Line:** {finding['line']}\n"
        
        if finding.get('snippet'):
            body += f"\n**Code Snippet:**\n```\n{finding['snippet'][:200]}\n```\n"
        
        body += f"""
### Recommended Remediation
{finding.get('recommendation', 'Please review and address this security issue according to SOC 2 compliance requirements.')}

### Additional Information
- **SOC 2 Trust Service Criteria:** {finding.get('control', 'N/A')}
- **Priority:** {'Immediate' if finding.get('severity') in ['critical', 'high'] else 'High' if finding.get('severity') == 'medium' else 'Normal'}

---
*This issue was automatically created by CompliantByDefault - SOC 2 Readiness Agent*
"""
        
        return body
    
    def _get_control_name(self, control: str) -> str:
        """Get the full name of a SOC 2 control."""
        control_names = {
            'CC1': 'Control Environment',
            'CC2': 'Communication and Information',
            'CC3': 'Risk Assessment',
            'CC4': 'Monitoring Activities',
            'CC5': 'Control Activities',
            'CC6': 'Logical and Physical Access Controls',
            'CC7': 'System Operations',
            'CC8': 'Change Management',
            'CC9': 'Risk Mitigation'
        }
        return control_names.get(control, 'SOC 2 Compliance')
    
    def _get_assignee_for_display(self, control: str) -> str:
        """Get the assignee username for display in issue body."""
        return get_assignee_for_control(control)
    
    def _get_risk_description(self, severity: str) -> str:
        """Get risk level description."""
        descriptions = {
            'critical': 'Immediate action required. This issue poses a severe security risk and violates SOC 2 requirements.',
            'high': 'High priority. This issue significantly impacts security posture and SOC 2 compliance.',
            'medium': 'Medium priority. This issue should be addressed to improve security and compliance.',
            'low': 'Low priority. This issue represents a minor security concern.',
            'info': 'Informational. This is a best practice recommendation.'
        }
        return descriptions.get(severity, 'This issue should be reviewed and addressed.')
    
    def create_issue(self, repo_url: str, finding: Dict) -> Optional[Dict]:
        """
        Create a GitHub issue for a compliance finding.
        
        Args:
            repo_url: GitHub repository URL
            finding: Finding dictionary with issue details
            
        Returns:
            Created issue data or None if failed
        """
        repo_info = self.extract_repo_info(repo_url)
        if not repo_info:
            logger.error(f"Invalid GitHub repository URL: {repo_url}")
            return None
        
        owner = repo_info['owner']
        repo = repo_info['repo']
        
        # Generate issue title
        control = finding.get('control', 'SOC2')
        issue_type = finding.get('type', 'security_issue').replace('_', ' ').title()
        severity = finding.get('severity', 'medium').upper()
        title = f"[{control}] [{severity}] {issue_type}"
        
        # Format issue body
        body = self.format_issue_body(finding)
        
        # Get assignee based on control
        assignee = get_assignee_for_control(finding.get('control', ''))
        
        # Create issue payload (without assignees initially)
        payload = {
            'title': title,
            'body': body
        }
        
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/issues"
            
            # First try with labels and assignees
            payload_full = {
                **payload,
                'labels': [
                    'security',
                    'soc2-compliance',
                    f'severity-{finding.get("severity", "medium")}',
                    f'control-{finding.get("control", "unknown").lower()}'
                ],
                'assignees': [assignee]
            }
            
            response = requests.post(url, json=payload_full, headers=self.headers)
            
            # If label creation fails (403), retry without labels but keep assignees
            if response.status_code == 403 and 'label' in response.text.lower():
                logger.warning("Label creation permission denied, creating issue without labels")
                payload_with_assignee = {
                    **payload,
                    'assignees': [assignee]
                }
                response = requests.post(url, json=payload_with_assignee, headers=self.headers)
            
            if response.status_code == 201:
                issue_data = response.json()
                issue_number = issue_data['number']
                logger.info(f"Created GitHub issue #{issue_number}: {title}")
                
                # If assignee wasn't set in creation, try to add it separately
                if not issue_data.get('assignees') or len(issue_data.get('assignees', [])) == 0:
                    logger.info(f"Attempting to add assignee {assignee} to issue #{issue_number}")
                    assignee_url = f"{self.api_base}/repos/{owner}/{repo}/issues/{issue_number}/assignees"
                    assignee_response = requests.post(
                        assignee_url, 
                        json={'assignees': [assignee]}, 
                        headers=self.headers
                    )
                    
                    if assignee_response.status_code in [200, 201]:
                        logger.info(f"Successfully assigned issue to {assignee}")
                    else:
                        logger.warning(f"Could not assign issue to {assignee}: {assignee_response.status_code} - {assignee_response.text}")
                
                return {
                    'number': issue_number,
                    'url': issue_data['html_url'],
                    'title': title,
                    'assignee': assignee
                }
            else:
                logger.error(f"Failed to create issue: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating GitHub issue: {e}")
            return None
    
    def create_issues_batch(self, repo_url: str, findings: list) -> Dict:
        """
        Create GitHub issues for multiple findings.
        
        Args:
            repo_url: GitHub repository URL
            findings: List of finding dictionaries
            
        Returns:
            Dict with success count and created issues
        """
        created_issues = []
        failed_count = 0
        
        for finding in findings:
            result = self.create_issue(repo_url, finding)
            if result:
                created_issues.append(result)
            else:
                failed_count += 1
        
        return {
            'success_count': len(created_issues),
            'failed_count': failed_count,
            'total': len(findings),
            'issues': created_issues
        }
