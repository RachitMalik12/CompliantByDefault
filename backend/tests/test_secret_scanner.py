import pytest
from pathlib import Path
from backend.src.scanners.secret_scanner import SecretScanner

@pytest.fixture
def secret_scanner():
    return SecretScanner()

@pytest.fixture
def sample_code_with_secrets():
    return """
import os

# Hardcoded API key (test example only - not a real key)
API_KEY = "sk_test_" + "1234567890abcdefghijklmnop"

# Hardcoded password
PASSWORD = "MySecretPassword123!"

# AWS credentials (test example - not real)
AWS_ACCESS_KEY = "AKIA" + "IOSFODNN7EXAMPLE"

def connect_db():
    conn = psycopg2.connect(
        host="localhost",
        database="mydb",
        user="admin",
        password="admin123"
    )
"""

def test_secret_scanner_detects_api_keys(secret_scanner, sample_code_with_secrets, tmp_path):
    """Test that secret scanner detects hardcoded API keys."""
    test_file = tmp_path / "test.py"
    test_file.write_text(sample_code_with_secrets)
    
    findings = secret_scanner.scan_file(test_file, sample_code_with_secrets)
    
    # Should find multiple secrets
    assert len(findings) > 0
    
    # Check for API key finding
    api_key_findings = [f for f in findings if 'api_key' in f['type'].lower()]
    assert len(api_key_findings) > 0

def test_secret_scanner_high_risk_files(secret_scanner, tmp_path):
    """Test that scanner flags high-risk files."""
    env_file = tmp_path / ".env"
    env_file.write_text("SECRET=mysecret")
    
    findings = secret_scanner.scan_file(env_file, "SECRET=mysecret")
    
    # Should flag the .env file itself
    high_risk_findings = [f for f in findings if f['type'] == 'high_risk_file']
    assert len(high_risk_findings) > 0

def test_secret_scanner_empty_file(secret_scanner, tmp_path):
    """Test scanner handles empty files."""
    empty_file = tmp_path / "empty.py"
    empty_file.write_text("")
    
    findings = secret_scanner.scan_file(empty_file, "")
    
    # Should return empty list or no critical findings
    assert isinstance(findings, list)
