import os
from pathlib import Path
from typing import List, Dict, Optional
import fnmatch
from .logger import logger

class FileLoader:
    """Utility for loading and traversing files in a repository."""
    
    EXCLUDED_DIRS = {
        'node_modules', '.git', '__pycache__', 'venv', 'env',
        '.venv', 'dist', 'build', '.next', 'coverage', '.pytest_cache',
        'target', 'bin', 'obj', '.terraform', 'vendor'
    }
    
    EXCLUDED_FILES = {
        '.DS_Store', 'Thumbs.db', '*.pyc', '*.pyo', '*.so', '*.dylib',
        '*.dll', '*.exe', '*.o', '*.a', '*.class', '*.jar', '*.war'
    }
    
    BINARY_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
        '.pdf', '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
        '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
        '.woff', '.woff2', '.ttf', '.eot', '.otf'
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    @staticmethod
    def get_all_files(root_path: str, include_patterns: Optional[List[str]] = None) -> List[Path]:
        """
        Get all relevant files from a directory tree.
        
        Args:
            root_path: Root directory to scan
            include_patterns: Optional list of glob patterns to include
            
        Returns:
            List of Path objects for relevant files
        """
        root = Path(root_path)
        if not root.exists():
            logger.error(f"Path does not exist: {root_path}")
            return []
        
        if not root.is_dir():
            logger.error(f"Path is not a directory: {root_path}")
            return []
        
        files = []
        logger.info(f"Scanning directory: {root_path}")
        
        for item in root.rglob('*'):
            # Skip excluded directories
            if any(excluded in item.parts for excluded in FileLoader.EXCLUDED_DIRS):
                continue
            
            # Only process files
            if not item.is_file():
                continue
            
            # Skip excluded files
            if any(fnmatch.fnmatch(item.name, pattern) for pattern in FileLoader.EXCLUDED_FILES):
                continue
            
            # Skip binary files
            if item.suffix.lower() in FileLoader.BINARY_EXTENSIONS:
                continue
            
            # Skip large files
            try:
                if item.stat().st_size > FileLoader.MAX_FILE_SIZE:
                    logger.warning(f"Skipping large file: {item}")
                    continue
            except OSError:
                continue
            
            # Apply include patterns if specified
            if include_patterns:
                if not any(fnmatch.fnmatch(str(item.relative_to(root)), pattern) 
                          for pattern in include_patterns):
                    continue
            
            files.append(item)
        
        logger.info(f"Found {len(files)} files to scan")
        return files
    
    @staticmethod
    def read_file(file_path: Path) -> Optional[str]:
        """
        Read file content safely.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string, or None if error
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    @staticmethod
    def get_file_info(file_path: Path, root_path: Path) -> Dict[str, any]:
        """
        Get metadata about a file.
        
        Args:
            file_path: Path to the file
            root_path: Root directory for relative path calculation
            
        Returns:
            Dictionary with file metadata
        """
        try:
            stat = file_path.stat()
            return {
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(root_path)),
                'name': file_path.name,
                'extension': file_path.suffix,
                'size': stat.st_size,
                'modified': stat.st_mtime,
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return {}
    
    @staticmethod
    def get_directory_tree(root_path: str) -> Dict[str, any]:
        """
        Get a tree structure of the directory.
        
        Args:
            root_path: Root directory
            
        Returns:
            Nested dictionary representing directory structure
        """
        root = Path(root_path)
        if not root.exists() or not root.is_dir():
            return {}
        
        tree = {
            'name': root.name,
            'path': str(root),
            'type': 'directory',
            'children': []
        }
        
        try:
            for item in sorted(root.iterdir()):
                # Skip excluded directories
                if item.name in FileLoader.EXCLUDED_DIRS:
                    continue
                
                if item.is_dir():
                    tree['children'].append(FileLoader.get_directory_tree(str(item)))
                elif item.is_file():
                    tree['children'].append({
                        'name': item.name,
                        'path': str(item),
                        'type': 'file',
                        'size': item.stat().st_size
                    })
        except PermissionError:
            logger.warning(f"Permission denied: {root}")
        
        return tree
