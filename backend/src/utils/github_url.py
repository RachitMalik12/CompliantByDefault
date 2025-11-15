"""Utility for converting local file paths to GitHub URLs."""
from pathlib import Path
from typing import Optional
import re


class GitHubURLConverter:
    """Convert local file paths to GitHub URLs with line numbers."""
    
    @staticmethod
    def extract_repo_info(repo_url: str) -> Optional[dict]:
        """
        Extract owner and repo name from GitHub URL.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dict with 'owner' and 'repo' keys, or None if invalid
        """
        # Match various GitHub URL formats:
        # https://github.com/owner/repo
        # https://github.com/owner/repo.git
        # git@github.com:owner/repo.git
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
    
    @staticmethod
    def convert_to_github_url(
        file_path: str,
        line_number: Optional[int],
        repo_url: Optional[str],
        local_base_path: Optional[str]
    ) -> str:
        """
        Convert a local file path to a GitHub URL.
        
        Args:
            file_path: Local file path
            line_number: Line number in the file (optional)
            repo_url: GitHub repository URL
            local_base_path: Base path of the cloned repository
            
        Returns:
            GitHub URL if repo_url is provided, otherwise original file_path
        """
        # If no repo URL, return original path
        if not repo_url or not local_base_path:
            return file_path
        
        # Extract repo info
        repo_info = GitHubURLConverter.extract_repo_info(repo_url)
        if not repo_info:
            return file_path
        
        # Calculate relative path
        try:
            file_path_obj = Path(file_path)
            base_path_obj = Path(local_base_path)
            
            # Get relative path from base
            relative_path = file_path_obj.relative_to(base_path_obj)
            
            # Convert to forward slashes for URL
            relative_path_str = str(relative_path).replace('\\', '/')
            
            # Construct GitHub URL
            github_url = (
                f"https://github.com/{repo_info['owner']}/{repo_info['repo']}"
                f"/blob/main/{relative_path_str}"
            )
            
            # Add line number if provided
            if line_number is not None and line_number > 0:
                github_url += f"#L{line_number}"
            
            return github_url
            
        except (ValueError, Exception):
            # If we can't calculate relative path, return original
            return file_path
    
    @staticmethod
    def update_finding_with_github_url(
        finding: dict,
        repo_url: Optional[str],
        local_base_path: Optional[str]
    ) -> dict:
        """
        Update a finding dict with GitHub URL.
        
        Args:
            finding: Finding dictionary with 'file' and optionally 'line' keys
            repo_url: GitHub repository URL
            local_base_path: Base path of the cloned repository
            
        Returns:
            Updated finding dict
        """
        if 'file' in finding:
            github_url = GitHubURLConverter.convert_to_github_url(
                finding['file'],
                finding.get('line'),
                repo_url,
                local_base_path
            )
            
            # Store original file path and add GitHub URL
            finding['local_file'] = finding['file']
            finding['file'] = github_url
        
        return finding
