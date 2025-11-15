import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict
from git import Repo, GitCommandError
from ..utils.logger import logger

class GitHubLoader:
    """Load and manage repositories from GitHub."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize GitHub loader.
        
        Args:
            cache_dir: Directory to cache cloned repos (defaults to temp)
        """
        self.cache_dir = cache_dir or tempfile.mkdtemp(prefix='compliant_')
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"GitHub cache directory: {self.cache_dir}")
    
    def clone_repository(self, repo_url: str, token: Optional[str] = None) -> str:
        """
        Clone a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            token: Optional GitHub personal access token
            
        Returns:
            Local path to cloned repository
        """
        # Parse repo name from URL
        repo_name = self._parse_repo_name(repo_url)
        local_path = Path(self.cache_dir) / repo_name
        
        # Remove if exists
        if local_path.exists():
            logger.info(f"Removing existing clone: {local_path}")
            shutil.rmtree(local_path)
        
        # Prepare URL with token if provided
        clone_url = repo_url
        if token:
            # Convert https://github.com/user/repo to https://token@github.com/user/repo
            if 'github.com' in repo_url:
                clone_url = repo_url.replace('https://', f'https://{token}@')
        
        logger.info(f"Cloning repository: {repo_url}")
        
        try:
            Repo.clone_from(clone_url, local_path, depth=1)  # Shallow clone
            logger.info(f"Successfully cloned to: {local_path}")
            return str(local_path)
        
        except GitCommandError as e:
            logger.error(f"Failed to clone repository: {e}")
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def _parse_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL."""
        # Remove .git suffix if present
        url = repo_url.rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        # Extract last two parts (owner/repo)
        parts = url.split('/')
        if len(parts) >= 2:
            return f"{parts[-2]}_{parts[-1]}"
        
        return 'repository'
    
    def get_repo_metadata(self, local_path: str) -> Dict:
        """
        Get metadata about a cloned repository.
        
        Args:
            local_path: Path to local repository
            
        Returns:
            Dictionary with repository metadata
        """
        try:
            repo = Repo(local_path)
            
            # Get basic info
            metadata = {
                'path': local_path,
                'remote_url': repo.remotes.origin.url if repo.remotes else None,
                'branch': repo.active_branch.name if not repo.head.is_detached else 'detached',
                'commit': str(repo.head.commit),
                'commit_message': repo.head.commit.message.strip(),
                'commit_date': repo.head.commit.committed_datetime.isoformat(),
                'is_dirty': repo.is_dirty()
            }
            
            logger.info(f"Repository metadata: {metadata['remote_url']}")
            return metadata
        
        except Exception as e:
            logger.error(f"Error getting repository metadata: {e}")
            return {'path': local_path, 'error': str(e)}
    
    def cleanup(self, local_path: Optional[str] = None):
        """
        Clean up cloned repositories.
        
        Args:
            local_path: Specific path to clean, or None for all
        """
        if local_path:
            if Path(local_path).exists():
                logger.info(f"Cleaning up: {local_path}")
                shutil.rmtree(local_path)
        else:
            if Path(self.cache_dir).exists():
                logger.info(f"Cleaning up cache directory: {self.cache_dir}")
                shutil.rmtree(self.cache_dir)
    
    def validate_url(self, repo_url: str) -> bool:
        """
        Validate if URL is a valid GitHub repository URL.
        
        Args:
            repo_url: Repository URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation
        if not repo_url:
            return False
        
        # Check for GitHub domain
        valid_patterns = [
            'github.com/',
            'https://github.com/',
            'http://github.com/',
            'git@github.com:'
        ]
        
        return any(pattern in repo_url for pattern in valid_patterns)
    
    def get_file_tree(self, local_path: str) -> Dict:
        """
        Get file tree structure of repository.
        
        Args:
            local_path: Path to repository
            
        Returns:
            Nested dictionary representing file structure
        """
        from ..utils.file_loader import FileLoader
        return FileLoader.get_directory_tree(local_path)
