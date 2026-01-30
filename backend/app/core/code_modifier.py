import os
import re
from typing import Dict, List, Optional
from pathlib import Path

class CodeModifier:
    """代码修改协议实现"""
    
    def __init__(self, base_path: str = "./data/uploads"):
        self.base_path = Path(base_path)
    
    def apply_modification(self, modification: Dict[str, any]) -> Dict[str, any]:
        """应用代码修改"""
        file_path = self.base_path / modification["file_path"]
        mod_type = modification["modification_type"].upper()
        content = modification["content"]
        
        result = {
            "success": False,
            "file_path": str(file_path),
            "modification_type": mod_type,
            "message": ""
        }
        
        try:
            if mod_type == "ADD":
                result = self._add_file(file_path, content)
            elif mod_type == "MODIFY":
                result = self._modify_file(file_path, content)
            elif mod_type == "DELETE":
                result = self._delete_file(file_path)
            else:
                result["message"] = f"Unknown modification type: {mod_type}"
                
        except Exception as e:
            result["message"] = f"Error: {str(e)}"
        
        return result
    
    def _add_file(self, file_path: Path, content: str) -> Dict[str, any]:
        """添加新文件"""
        if file_path.exists():
            return {
                "success": False,
                "file_path": str(file_path),
                "modification_type": "ADD",
                "message": "File already exists"
            }
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        
        return {
            "success": True,
            "file_path": str(file_path),
            "modification_type": "ADD",
            "message": "File created successfully"
        }
    
    def _modify_file(self, file_path: Path, content: str) -> Dict[str, any]:
        """修改现有文件"""
        if not file_path.exists():
            return {
                "success": False,
                "file_path": str(file_path),
                "modification_type": "MODIFY",
                "message": "File does not exist"
            }
        
        original_match = re.search(
            '# --- ORIGINAL SNIPPET START ---\n(.*?)\n# --- ORIGINAL SNIPPET END ---',
            content,
            re.DOTALL
        )
        updated_match = re.search(
            '# --- UPDATED SNIPPET START ---\n(.*?)\n# --- UPDATED SNIPPET END ---',
            content,
            re.DOTALL
        )
        
        if not (original_match and updated_match):
            file_path.write_text(content, encoding="utf-8")
            return {
                "success": True,
                "file_path": str(file_path),
                "modification_type": "MODIFY",
                "message": "File overwritten"
            }
        
        original_snippet = original_match.group(1)
        updated_snippet = updated_match.group(1)
        current_content = file_path.read_text(encoding="utf-8")
        
        if original_snippet in current_content:
            new_content = current_content.replace(original_snippet, updated_snippet)
            file_path.write_text(new_content, encoding="utf-8")
            return {
                "success": True,
                "file_path": str(file_path),
                "modification_type": "MODIFY",
                "message": "File modified successfully"
            }
        else:
            return {
                "success": False,
                "file_path": str(file_path),
                "modification_type": "MODIFY",
                "message": "Original snippet not found in file"
            }
    
    def _delete_file(self, file_path: Path) -> Dict[str, any]:
        """删除文件"""
        if not file_path.exists():
            return {
                "success": False,
                "file_path": str(file_path),
                "modification_type": "DELETE",
                "message": "File does not exist"
            }
        
        file_path.unlink()
        
        return {
            "success": True,
            "file_path": str(file_path),
            "modification_type": "DELETE",
            "message": "File deleted successfully"
        }
