# GitHub Issue Creation Feature

## Overview
CompliantByDefault now automatically creates GitHub issues for SOC 2 compliance findings with intelligent assignment based on control expertise.

## Features

### 1. Automatic Issue Creation
- Click "Create Issue" button next to any finding in the report
- Issues are automatically created in the scanned GitHub repository
- Each issue includes:
  - **SOC 2 Control**: Specific control violated (e.g., CC1, CC2)
  - **Summary of Risk**: Detailed description of the compliance issue
  - **Risk Level**: Severity (Critical, High, Medium, Low)
  - **Recommended Remediation**: Actionable steps to fix the issue
  - **Direct GitHub Link**: Link to exact file and line number

### 2. Expert Assignment
Issues are automatically assigned to the appropriate expert based on SOC 2 control:

| Control Range | Expert | Controls |
|--------------|---------|----------|
| CC1-CC3 | RachitMalik12 | Control Environment, Communication, Risk Assessment |
| CC4-CC5 | AdilFayyaz | Monitoring Activities, Control Activities |
| CC6-CC9 | swassingh | Access Controls, System Operations, Change Management, Risk Mitigation |

### 3. Issue Format

Each created issue follows this structure:

```markdown
## 🔴 SOC 2 Compliance Issue Detected

### Issue Details
**Control:** CC9 - Risk Mitigation
**Type:** Hardcoded Password
**Severity:** CRITICAL

### Summary of Risk
Potential hardcoded password detected in the codebase.

### Risk Level
**CRITICAL** - Immediate action required. This issue poses a severe security risk and violates SOC 2 requirements.

### Location
**File:** [config.py](https://github.com/owner/repo/blob/main/src/config.py#L42)
**Line:** 42

### Recommended Remediation
Use environment variables or a secure secrets management service instead of hardcoding credentials.

### Additional Information
- **SOC 2 Trust Service Criteria:** CC9
- **Priority:** Immediate
```

## Configuration

### Backend Setup

1. **Environment Variable**:
   ```bash
   GITHUB_TOKEN=ghp_your_github_token_here
   ```
   
   The GitHub token needs the following permissions:
   - `repo` - Full control of private repositories
   - `public_repo` - Access to public repositories

2. **Expertise Mapping**:
   Edit `backend/src/config/expertise_mapping.py` to customize expert assignments:
   
   ```python
   CONTROL_EXPERTISE_MAPPING = {
       "CC1": "RachitMalik12",
       "CC2": "RachitMalik12",
       # ... add more mappings
   }
   ```

### API Endpoint

**POST** `/issue/create`

Request:
```json
{
  "repo_url": "https://github.com/owner/repo",
  "finding": {
    "type": "hardcoded_password",
    "severity": "critical",
    "file": "https://github.com/owner/repo/blob/main/src/config.py#L42",
    "line": 42,
    "message": "Hardcoded password detected",
    "control": "CC9",
    "recommendation": "Use environment variables"
  },
  "token": "ghp_optional_token" // Optional, uses GITHUB_TOKEN env var if not provided
}
```

Response:
```json
{
  "success": true,
  "issue_number": 123,
  "issue_url": "https://github.com/owner/repo/issues/123",
  "assignee": "swassingh",
  "message": "Successfully created issue #123"
}
```

## Usage

### From the Web Interface

1. Scan a GitHub repository
2. View the compliance report
3. Find an issue you want to track in the Findings Table
4. Click the "Create Issue" button next to the finding
5. The issue is created and assigned automatically
6. A success message appears with the issue number and link
7. The issue opens in a new tab

### Button States

- **Create Issue** (Blue): Ready to create issue
- **Creating...** (Gray): Currently creating the issue
- **✓ Created** (Green): Issue already created

## Files Modified/Created

### Backend
- `backend/src/config/expertise_mapping.py` - NEW: Expert assignment mapping
- `backend/src/integrations/github_issues.py` - NEW: GitHub issue creation logic
- `backend/src/api.py` - Added `/issue/create` endpoint
- `backend/requirements.txt` - Added `requests` library

### Frontend
- `frontend/src/lib/api.ts` - Added `createGitHubIssue()` function
- `frontend/src/components/FindingsTable.tsx` - Added "Create Issue" button
- `frontend/src/pages/report/[id].tsx` - Pass repo URL to FindingsTable

## Benefits

1. **Streamlined Workflow**: Developers can immediately track compliance issues without manual effort
2. **Proper Assignment**: Issues automatically go to the right expert
3. **Complete Context**: Each issue includes all necessary information for remediation
4. **Direct Links**: Jump straight to the problematic code
5. **Professional Format**: Consistent, well-formatted issues that are easy to understand

## Example

When a critical hardcoded password is detected in `src/config.py` at line 42:

1. Issue is created in the repository
2. Assigned to `swassingh` (owner of CC9 controls)
3. Labeled with:
   - `security`
   - `soc2-compliance`
   - `severity-critical`
   - `control-cc9`
4. Contains direct link to https://github.com/owner/repo/blob/main/src/config.py#L42
5. Includes remediation steps

## Future Enhancements

- [ ] Batch issue creation (create all critical/high issues at once)
- [ ] Custom templates per control type
- [ ] Integration with project boards
- [ ] Auto-close issues when fixed and re-scanned
- [ ] Slack/email notifications when issues are created
