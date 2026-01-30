import re
from typing import List, Dict, Any

class SecurityReviewer:
    """安全审查系统"""
    
    DANGEROUS_PATTERNS = [
        (r'eval\s*\(', "Use of eval() is dangerous - allows arbitrary code execution"),
        (r'exec\s*\(', "Use of exec() is dangerous - allows arbitrary code execution"),
        (r'__import__\s*\(', "Dynamic imports can be exploited"),
        (r'os\.system\s*\(', "os.system() can lead to command injection"),
        (r'subprocess\.(call|run|Popen).*shell=True', "Shell=True in subprocess is dangerous"),
        (r'pickle\.loads?\s*\(', "Pickle deserialization can execute arbitrary code"),
        (r'PASSWORD\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
        (r'API_KEY\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
        (r'SECRET\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
        (r'\.\./', "Path traversal pattern detected"),
        (r'SELECT.*FROM.*WHERE.*=.*\+', "Potential SQL injection via string concatenation"),
        (r'innerHTML\s*=', "innerHTML assignment can lead to XSS"),
        (r'dangerouslySetInnerHTML', "dangerouslySetInnerHTML can lead to XSS"),
    ]
    
    @classmethod
    def review_code(cls, code: str, language: str = "python") -> List[Dict[str, Any]]:
        """审查代码安全性"""
        issues = []
        
        for pattern, description in cls.DANGEROUS_PATTERNS:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append({
                    "severity": "HIGH",
                    "type": "dangerous_pattern",
                    "line": line_num,
                    "pattern": pattern,
                    "description": description,
                    "snippet": cls._get_code_snippet(code, match.start(), match.end())
                })
        
        return issues
    
    @classmethod
    def _get_code_snippet(cls, code: str, start: int, end: int, context_lines: int = 2) -> str:
        """获取代码片段上下文"""
        lines = code.split('\n')
        start_line = max(0, code[:start].count('\n') - context_lines)
        end_line = min(len(lines), code[:end].count('\n') + context_lines + 1)
        
        return '\n'.join(lines[start_line:end_line])
    
    @classmethod
    def generate_security_report(cls, issues: List[Dict[str, Any]]) -> str:
        """生成安全报告"""
        if not issues:
            return "✅ No security issues detected."
        
        report_parts = [f"⚠️ Found {len(issues)} security issue(s):\n"]
        
        critical = [i for i in issues if i.get("severity") == "CRITICAL"]
        high = [i for i in issues if i.get("severity") == "HIGH"]
        medium = [i for i in issues if i.get("severity") == "MEDIUM"]
        
        if critical:
            report_parts.append(f"\n🔴 CRITICAL ({len(critical)}):")
            for issue in critical:
                report_parts.append(f"  - Line {issue['line']}: {issue['description']}")
        
        if high:
            report_parts.append(f"\n🟠 HIGH ({len(high)}):")
            for issue in high:
                report_parts.append(f"  - Line {issue['line']}: {issue['description']}")
        
        if medium:
            report_parts.append(f"\n🟡 MEDIUM ({len(medium)}):")
            for issue in medium:
                report_parts.append(f"  - Line {issue['line']}: {issue['description']}")
        
        return '\n'.join(report_parts)