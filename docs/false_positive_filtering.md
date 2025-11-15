# False Positive Filtering in Static Analysis

## Overview

The static scanner now includes a two-pass analysis system to significantly reduce false positives while maintaining high detection accuracy for real security issues.

## How It Works

### Pass 1: Pattern Matching
The initial scan uses regex patterns to detect potential security issues:
- SQL injection risks
- Weak cryptography
- Insecure random number generation
- Disabled SSL verification
- Missing authentication
- Sensitive data logging
- And more...

### Pass 2: AI-Powered Validation
After initial detection, findings are validated using Gemini AI to filter false positives:

1. **Batch Processing**: Groups findings by file for efficient analysis
2. **Context Analysis**: Examines surrounding code to understand intent
3. **Pattern Recognition**: Identifies common false positive patterns:
   - Test files and mock implementations
   - Comments/documentation mentioning security issues
   - Already-mitigated code (e.g., parameterized queries)
   - Development/testing configurations clearly marked as such
   - Code that appears vulnerable but has validation elsewhere

## Example

**Code that triggers initial detection:**
```python
# This comment mentions SQL injection - but it's just a comment
def safe_query(user_id):
    # Using parameterized query - SAFE
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

**Result:**
- Pass 1: Flags potential SQL injection (pattern match on "SQL injection")
- Pass 2: Validates this is a false positive (it's in a comment, actual code uses parameterized queries)
- **Final Result**: Finding is filtered out, reducing noise

## Benefits

1. **Reduced Noise**: Filters obvious false positives to focus on real issues
2. **Better Context**: Understands code patterns beyond simple regex matching
3. **Conservative Approach**: When uncertain, keeps the finding (fail-safe)
4. **Efficient**: Batches analysis by file to minimize API calls and tokens
5. **Transparent**: Logs how many false positives were filtered per file

## Performance

- **Token Efficiency**: Groups findings by file in single LLM calls
- **Timeout Prevention**: Processes files independently with error handling
- **Fail-Safe**: On validation errors, keeps all findings to avoid missing real issues
- **Scalable**: Can be disabled if GEMINI_API_KEY is not available

## Configuration

The feature is automatically enabled when `GEMINI_API_KEY` is set in your environment. No additional configuration needed.

To disable (use pattern matching only):
- Remove or comment out `GEMINI_API_KEY` from `.env` file
- The scanner will log: "GEMINI_API_KEY not found - second-pass validation disabled"

## Metrics

When enabled, you'll see logs like:
```
INFO - Starting static code analysis...
INFO - Static analysis complete. Found 15 potential issues
INFO - Running second-pass validation to filter false positives...
INFO - Filtered 3 false positive(s) from vulnerable.py
INFO - Filtered 1 false positive(s) from utils.py
INFO - After validation: 11 confirmed issues
```

## Future Enhancements

Potential improvements for future versions:
- Custom validation rules per project
- Learning from user feedback on false positives
- Integration with static analysis tools like Semgrep
- Caching validation results for unchanged code
