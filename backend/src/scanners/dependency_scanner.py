import json
from pathlib import Path
from typing import List, Dict, Set, Optional
import re
from ..utils.logger import logger
from ..utils.file_loader import FileLoader
from ..utils.github_url import GitHubURLConverter

class DependencyScanner:
    """Scanner for analyzing dependencies and detecting vulnerable packages."""
    
    DEPENDENCY_FILES = {
        'requirements.txt': 'python',
        'Pipfile': 'python',
        'setup.py': 'python',
        'package.json': 'javascript',
        'package-lock.json': 'javascript',
        'yarn.lock': 'javascript',
        'pom.xml': 'java',
        'build.gradle': 'java',
        'Gemfile': 'ruby',
        'go.mod': 'go',
        'Cargo.toml': 'rust'
    }
    
    # Known vulnerable patterns (simplified - in production use CVE databases)
    KNOWN_VULNERABILITIES = {
        'python': {
            'django': {'<2.2.28': 'CVE-2022-28346', '<3.2.13': 'CVE-2022-28347'},
            'flask': {'<2.0.0': 'Multiple security issues'},
            'requests': {'<2.20.0': 'CVE-2018-18074'},
            'pillow': {'<9.0.0': 'Multiple CVEs'},
            'pyyaml': {'<5.4': 'CVE-2020-14343'}
        },
        'javascript': {
            'lodash': {'<4.17.21': 'Multiple CVEs'},
            'axios': {'<0.21.1': 'CVE-2020-28168'},
            'next': {'<12.0.0': 'Multiple security issues'},
            'react-dom': {'<16.14.0': 'XSS vulnerabilities'}
        }
    }
    
    def scan_file(self, file_path: Path, content: str) -> List[Dict]:
        """
        Scan a dependency file for security issues.
        
        Args:
            file_path: Path to the dependency file
            content: File content
            
        Returns:
            List of findings
        """
        findings = []
        file_type = self.DEPENDENCY_FILES.get(file_path.name)
        
        if not file_type:
            return findings
        
        logger.info(f"Scanning dependency file: {file_path}")
        
        if file_path.name == 'requirements.txt':
            findings.extend(self._scan_requirements_txt(file_path, content))
        elif file_path.name == 'package.json':
            findings.extend(self._scan_package_json(file_path, content))
        elif file_path.name == 'Pipfile':
            findings.extend(self._scan_pipfile(file_path, content))
        
        return findings
    
    def _scan_requirements_txt(self, file_path: Path, content: str) -> List[Dict]:
        """Scan Python requirements.txt file."""
        findings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse package and version
            match = re.match(r'([a-zA-Z0-9_-]+)([=<>!]+)?(.*)', line)
            if match:
                package = match.group(1).lower()
                operator = match.group(2) or ''
                version = match.group(3).strip()
                
                # Check for pinned versions
                if not operator or operator != '==':
                    findings.append({
                        'type': 'unpinned_dependency',
                        'severity': 'medium',
                        'file': str(file_path),
                        'line': line_num,
                        'message': f'Dependency {package} is not pinned to a specific version',
                        'control': 'CC3',
                        'package': package,
                        'recommendation': 'Pin dependencies to specific versions for reproducible builds'
                    })
                
                # Check for known vulnerabilities
                if package in self.KNOWN_VULNERABILITIES.get('python', {}):
                    vuln_info = self.KNOWN_VULNERABILITIES['python'][package]
                    findings.append({
                        'type': 'vulnerable_dependency',
                        'severity': 'high',
                        'file': str(file_path),
                        'line': line_num,
                        'message': f'Package {package} has known vulnerabilities',
                        'control': 'CC3',
                        'package': package,
                        'version': version,
                        'vulnerability': str(vuln_info),
                        'recommendation': 'Update to the latest secure version'
                    })
        
        return findings
    
    def _scan_package_json(self, file_path: Path, content: str) -> List[Dict]:
        """Scan Node.js package.json file."""
        findings = []
        
        try:
            data = json.loads(content)
            dependencies = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            
            for package, version in dependencies.items():
                package_lower = package.lower()
                
                # Check for loose version constraints
                if version.startswith('^') or version.startswith('~') or version == '*':
                    findings.append({
                        'type': 'loose_version_constraint',
                        'severity': 'medium',
                        'file': str(file_path),
                        'line': 0,
                        'message': f'Package {package} uses loose version constraint: {version}',
                        'control': 'CC3',
                        'package': package,
                        'version': version,
                        'recommendation': 'Use exact versions or lock files for reproducibility'
                    })
                
                # Check for known vulnerabilities
                if package_lower in self.KNOWN_VULNERABILITIES.get('javascript', {}):
                    vuln_info = self.KNOWN_VULNERABILITIES['javascript'][package_lower]
                    findings.append({
                        'type': 'vulnerable_dependency',
                        'severity': 'high',
                        'file': str(file_path),
                        'line': 0,
                        'message': f'Package {package} has known vulnerabilities',
                        'control': 'CC3',
                        'package': package,
                        'version': version,
                        'vulnerability': str(vuln_info),
                        'recommendation': 'Update to the latest secure version'
                    })
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing {file_path}: {e}")
        
        return findings
    
    def _scan_pipfile(self, file_path: Path, content: str) -> List[Dict]:
        """Scan Python Pipfile."""
        findings = []
        # Simplified - would use toml parser in production
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if '=' in line and not line.strip().startswith('#'):
                findings.append({
                    'type': 'dependency_check',
                    'severity': 'info',
                    'file': str(file_path),
                    'line': line_num,
                    'message': 'Review dependency for security updates',
                    'control': 'CC3',
                    'recommendation': 'Regularly update and audit dependencies'
                })
        
        return findings
    
    def scan_directory(self, root_path: str, repo_url: Optional[str] = None, local_base_path: Optional[str] = None) -> List[Dict]:
        """
        Scan directory for dependency files and analyze them.
        
        Args:
            root_path: Root directory to scan
            repo_url: GitHub repository URL (optional)
            local_base_path: Base path of cloned repository (optional)
            
        Returns:
            List of all findings
        """
        logger.info("Starting dependency scan...")
        all_findings = []
        
        files = FileLoader.get_all_files(root_path)
        
        for file_path in files:
            if file_path.name in self.DEPENDENCY_FILES:
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
        
        logger.info(f"Dependency scan complete. Found {len(all_findings)} issues")
        return all_findings
