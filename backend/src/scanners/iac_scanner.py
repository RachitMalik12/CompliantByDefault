import re
import yaml
from pathlib import Path
from typing import List, Dict, Optional
from ..utils.logger import logger
from ..utils.file_loader import FileLoader

class IaCScanner:
    """Scanner for Infrastructure as Code security issues."""
    
    IAC_FILES = {
        '.tf': 'terraform',
        '.tfvars': 'terraform',
        'docker-compose.yml': 'docker',
        'docker-compose.yaml': 'docker',
        'Dockerfile': 'docker',
        '.yaml': 'kubernetes',
        '.yml': 'kubernetes'
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize IaC scanner."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "soc2_controls.yaml"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.config = config
    
    def scan_file(self, file_path: Path, content: str) -> List[Dict]:
        """
        Scan an IaC file for security issues.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            List of findings
        """
        findings = []
        
        # Determine file type
        file_type = None
        if file_path.suffix in ['.tf', '.tfvars']:
            file_type = 'terraform'
        elif 'Dockerfile' in file_path.name:
            file_type = 'docker'
        elif 'docker-compose' in file_path.name:
            file_type = 'docker_compose'
        elif file_path.suffix in ['.yaml', '.yml']:
            # Check if it's Kubernetes
            if 'apiVersion' in content or 'kind:' in content:
                file_type = 'kubernetes'
        
        if file_type == 'terraform':
            findings.extend(self._scan_terraform(file_path, content))
        elif file_type == 'docker':
            findings.extend(self._scan_dockerfile(file_path, content))
        elif file_type == 'docker_compose':
            findings.extend(self._scan_docker_compose(file_path, content))
        elif file_type == 'kubernetes':
            findings.extend(self._scan_kubernetes(file_path, content))
        
        return findings
    
    def _scan_terraform(self, file_path: Path, content: str) -> List[Dict]:
        """Scan Terraform files for security issues."""
        findings = []
        lines = content.split('\n')
        
        # Check for hardcoded credentials
        if re.search(r'(access_key|secret_key|password)\s*=\s*"[^"]{8,}"', content):
            findings.append({
                'type': 'hardcoded_credentials',
                'severity': 'critical',
                'file': str(file_path),
                'line': 0,
                'message': 'Hardcoded credentials detected in Terraform file',
                'control': 'CC9',
                'recommendation': 'Use variables or secret management services'
            })
        
        # Check for public S3 buckets
        if 'acl' in content and 'public-read' in content:
            findings.append({
                'type': 'public_s3_bucket',
                'severity': 'high',
                'file': str(file_path),
                'line': 0,
                'message': 'S3 bucket with public read access detected',
                'control': 'CC6',
                'recommendation': 'Restrict bucket access and use IAM policies'
            })
        
        # Check for unencrypted storage
        if 'aws_db_instance' in content or 'aws_ebs_volume' in content:
            if not re.search(r'encrypted\s*=\s*true', content):
                findings.append({
                    'type': 'unencrypted_storage',
                    'severity': 'high',
                    'file': str(file_path),
                    'line': 0,
                    'message': 'Storage resource without encryption enabled',
                    'control': 'CC9',
                    'recommendation': 'Enable encryption at rest for all storage'
                })
        
        # Check for open security groups
        if re.search(r'cidr_blocks\s*=\s*\["0\.0\.0\.0/0"\]', content):
            findings.append({
                'type': 'open_security_group',
                'severity': 'high',
                'file': str(file_path),
                'line': 0,
                'message': 'Security group allows traffic from all IPs (0.0.0.0/0)',
                'control': 'CC6',
                'recommendation': 'Restrict access to specific IP ranges'
            })
        
        return findings
    
    def _scan_dockerfile(self, file_path: Path, content: str) -> List[Dict]:
        """Scan Dockerfile for security issues."""
        findings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for running as root
            if line_stripped.upper().startswith('USER') and 'root' in line_stripped:
                findings.append({
                    'type': 'running_as_root',
                    'severity': 'high',
                    'file': str(file_path),
                    'line': line_num,
                    'message': 'Container configured to run as root user',
                    'control': 'CC6',
                    'recommendation': 'Create and use a non-root user'
                })
            
            # Check for latest tag
            if 'FROM' in line_stripped.upper() and ':latest' in line_stripped:
                findings.append({
                    'type': 'latest_tag',
                    'severity': 'medium',
                    'file': str(file_path),
                    'line': line_num,
                    'message': 'Using :latest tag instead of specific version',
                    'control': 'CC8',
                    'recommendation': 'Use specific image versions for reproducibility'
                })
            
            # Check for secrets in build
            if re.search(r'(ARG|ENV)\s+(PASSWORD|SECRET|KEY|TOKEN)', line_stripped, re.IGNORECASE):
                findings.append({
                    'type': 'secret_in_dockerfile',
                    'severity': 'high',
                    'file': str(file_path),
                    'line': line_num,
                    'message': 'Potential secret in Dockerfile ARG/ENV',
                    'control': 'CC9',
                    'recommendation': 'Use Docker secrets or build-time secrets'
                })
        
        # Check if USER directive exists
        if not any('USER' in line for line in lines):
            findings.append({
                'type': 'no_user_directive',
                'severity': 'high',
                'file': str(file_path),
                'line': 0,
                'message': 'No USER directive found - container will run as root',
                'control': 'CC6',
                'recommendation': 'Add USER directive to run as non-root'
            })
        
        return findings
    
    def _scan_docker_compose(self, file_path: Path, content: str) -> List[Dict]:
        """Scan docker-compose files."""
        findings = []
        
        try:
            data = yaml.safe_load(content)
            services = data.get('services', {})
            
            for service_name, service_config in services.items():
                # Check for privileged mode
                if service_config.get('privileged'):
                    findings.append({
                        'type': 'privileged_container',
                        'severity': 'critical',
                        'file': str(file_path),
                        'line': 0,
                        'message': f'Service {service_name} runs in privileged mode',
                        'control': 'CC6',
                        'recommendation': 'Avoid privileged mode unless absolutely necessary'
                    })
                
                # Check for exposed ports
                ports = service_config.get('ports', [])
                if ports:
                    findings.append({
                        'type': 'exposed_ports',
                        'severity': 'medium',
                        'file': str(file_path),
                        'line': 0,
                        'message': f'Service {service_name} exposes ports: {ports}',
                        'control': 'CC6',
                        'recommendation': 'Ensure only necessary ports are exposed'
                    })
        
        except yaml.YAMLError as e:
            logger.error(f"Error parsing {file_path}: {e}")
        
        return findings
    
    def _scan_kubernetes(self, file_path: Path, content: str) -> List[Dict]:
        """Scan Kubernetes manifests."""
        findings = []
        
        try:
            # K8s files can have multiple documents
            docs = yaml.safe_load_all(content)
            
            for doc in docs:
                if not doc:
                    continue
                
                kind = doc.get('kind', '')
                
                # Check for privileged containers
                if kind in ['Pod', 'Deployment', 'StatefulSet', 'DaemonSet']:
                    containers = []
                    if kind == 'Pod':
                        containers = doc.get('spec', {}).get('containers', [])
                    else:
                        containers = doc.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
                    
                    for container in containers:
                        security_context = container.get('securityContext', {})
                        if security_context.get('privileged'):
                            findings.append({
                                'type': 'privileged_container',
                                'severity': 'critical',
                                'file': str(file_path),
                                'line': 0,
                                'message': f'Container runs with privileged flag',
                                'control': 'CC6',
                                'recommendation': 'Remove privileged flag'
                            })
                        
                        if security_context.get('runAsUser') == 0:
                            findings.append({
                                'type': 'running_as_root',
                                'severity': 'high',
                                'file': str(file_path),
                                'line': 0,
                                'message': 'Container runs as root (UID 0)',
                                'control': 'CC6',
                                'recommendation': 'Run as non-root user'
                            })
        
        except yaml.YAMLError as e:
            logger.error(f"Error parsing {file_path}: {e}")
        
        return findings
    
    def scan_directory(self, root_path: str) -> List[Dict]:
        """
        Scan directory for IaC files.
        
        Args:
            root_path: Root directory to scan
            
        Returns:
            List of all findings
        """
        logger.info("Starting IaC scan...")
        all_findings = []
        
        files = FileLoader.get_all_files(root_path)
        
        for file_path in files:
            # Check if it's an IaC file
            is_iac = (
                file_path.suffix in ['.tf', '.tfvars'] or
                'Dockerfile' in file_path.name or
                'docker-compose' in file_path.name or
                (file_path.suffix in ['.yaml', '.yml'] and 
                 ('k8s' in str(file_path) or 'kubernetes' in str(file_path)))
            )
            
            if is_iac:
                content = FileLoader.read_file(file_path)
                if content:
                    findings = self.scan_file(file_path, content)
                    all_findings.extend(findings)
        
        logger.info(f"IaC scan complete. Found {len(all_findings)} issues")
        return all_findings
