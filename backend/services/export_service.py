"""
Export Service - Generate TXT/Markdown files from a script
"""
import os
import uuid
from typing import Dict, Any

from fastapi import HTTPException


class ExportService:
    """Service for exporting scripts to files"""

    def __init__(self):
        self.downloads_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "downloads"
        )
        os.makedirs(self.downloads_dir, exist_ok=True)

    def export_script(self, script: Dict[str, Any], format: str) -> Dict[str, Any]:
        """
        Export one script to file
        """
        try:
            if format not in ["txt", "md"]:
                raise HTTPException(status_code=400, detail="Format must be 'txt' or 'md'")

            filename = f"script_{uuid.uuid4().hex[:8]}.{format}"
            filepath = os.path.join(self.downloads_dir, filename)

            if format == "md":
                content = self._generate_markdown(script)
            else:
                content = self._generate_txt(script)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            return {"download_url": f"/static/downloads/{filename}"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

    def _generate_markdown(self, script: Dict[str, Any]) -> str:
        """Generate Markdown content"""
        lines = []
        lines.append("# 直播带货话术\n\n")
        lines.append(self._format_script_markdown(script))
        return "".join(lines)

    def _format_script_markdown(self, script: Dict[str, Any]) -> str:
        """Format single script as markdown"""
        lines = []
        lines.append(f"**开头吸引**: {script.get('opening_hook', '')}\n\n")
        lines.append(f"**痛点**: {script.get('pain_point', '')}\n\n")
        lines.append(f"**解决方案**: {script.get('solution', '')}\n\n")
        lines.append(f"**证明**: {script.get('proof', '')}\n\n")
        lines.append(f"**促单**: {script.get('offer', '')}\n")
        return "".join(lines)

    def _generate_txt(self, script: Dict[str, Any]) -> str:
        """Generate TXT content"""
        lines = []
        lines.append("=" * 50)
        lines.append("直播带货话术")
        lines.append("=" * 50)
        lines.append("")
        lines.append(self._format_script_txt(script))
        lines.append("")
        return "\n".join(lines)

    def _format_script_txt(self, script: Dict[str, Any]) -> str:
        """Format single script as TXT"""
        lines = []
        lines.append(f"【开头吸引】{script.get('opening_hook', '')}")
        lines.append(f"【痛点】{script.get('pain_point', '')}")
        lines.append(f"【解决方案】{script.get('solution', '')}")
        lines.append(f"【证明】{script.get('proof', '')}")
        lines.append(f"【促单】{script.get('offer', '')}")
        return "\n".join(lines)
