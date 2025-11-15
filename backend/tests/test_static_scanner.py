import pytest
from pathlib import Path
from backend.src.scanners.static_scanner import StaticScanner

@pytest.fixture
def static_scanner():
    return StaticScanner()

@pytest.fixture
def sample_vulnerable_code():
    return """
import sqlite3

def get_user(username):
    # SQL Injection vulnerability
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    
def generate_token():
    # Insecure random
    import random
    return random.random()

import requests

def fetch_data():
    # Disabled SSL verification
    response = requests.get("https://api.example.com", verify=False)
    
import hashlib

def hash_password(password):
    # Weak crypto (MD5)
    return hashlib.md5(password.encode()).hexdigest()
"""

def test_static_scanner_detects_sql_injection(static_scanner, sample_vulnerable_code, tmp_path):
    """Test detection of SQL injection risks."""
    test_file = tmp_path / "vulnerable.py"
    test_file.write_text(sample_vulnerable_code)
    
    findings = static_scanner.scan_file(test_file, sample_vulnerable_code)
    
    # Should detect SQL injection pattern
    sql_findings = [f for f in findings if 'sql' in f['type'].lower()]
    assert len(sql_findings) > 0

def test_static_scanner_provides_recommendations(static_scanner, sample_vulnerable_code, tmp_path):
    """Test that scanner provides remediation recommendations."""
    test_file = tmp_path / "test.py"
    test_file.write_text(sample_vulnerable_code)
    
    findings = static_scanner.scan_file(test_file, sample_vulnerable_code)
    
    # All findings should have recommendations
    for finding in findings:
        assert 'recommendation' in finding
        assert len(finding['recommendation']) > 0

def test_static_scanner_safe_code(static_scanner, tmp_path):
    """Test scanner doesn't flag safe code."""
    safe_code = """
def add(a, b):
    return a + b

def greet(name):
    print(f"Hello, {name}!")
"""
    test_file = tmp_path / "safe.py"
    test_file.write_text(safe_code)
    
    findings = static_scanner.scan_file(test_file, safe_code)
    
    # Should have no or very few findings
    assert len(findings) == 0
