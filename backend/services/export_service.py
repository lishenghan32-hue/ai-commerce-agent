"""
Export Service - Generate TXT/Markdown files from scripts
"""
import os
import uuid
from typing import Dict, Any, List

from fastapi import HTTPException


class ExportService:
    """Service for exporting scripts to files"""

    def __init__(self):
        # 创建 downloads 目录
        self.downloads_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "downloads"
        )
        os.makedirs(self.downloads_dir, exist_ok=True)

    def export_scripts(
        self,
        best_script: Dict[str, Any],
        scripts: List[Dict[str, Any]],
        format: str
    ) -> Dict[str, Any]:
        """
        Export scripts to file

        Args:
            best_script: The recommended best script
            scripts: List of all scripts
            format: "txt" or "md"

        Returns:
            Dict with download_url

        Raises:
            HTTPException: If export fails
        """
        try:
            if format not in ["txt", "md"]:
                raise HTTPException(status_code=400, detail="Format must be 'txt' or 'md'")

            # 生成文件名
            filename = f"script_{uuid.uuid4().hex[:8]}.{format}"
            filepath = os.path.join(self.downloads_dir, filename)

            # 生成内容
            if format == "md":
                content = self._generate_markdown(best_script, scripts)
            else:
                content = self._generate_txt(best_script, scripts)

            # 写入文件
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            return {
                "download_url": f"/static/downloads/{filename}"
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

    def _generate_markdown(
        self,
        best_script: Dict[str, Any],
        scripts: List[Dict[str, Any]]
    ) -> str:
        """Generate Markdown content"""
        lines = []

        # 标题
        lines.append("# 直播带货话术\n")
        lines.append(f"> 生成时间\n\n---\n")

        # 推荐最佳脚本
        if best_script:
            lines.append("## 推荐最佳脚本\n")
            lines.append(f"**风格**: {best_script.get('style', '')}  |  **评分**: {best_script.get('score', 0)}分\n")
            if best_script.get('reason'):
                lines.append(f"> **{best_script['reason']}**\n")
            lines.append(self._format_script_markdown(best_script))
            lines.append("\n---\n")

        # 所有脚本
        lines.append("## 所有脚本\n")
        for i, script in enumerate(scripts, 1):
            lines.append(f"### {i}. {script.get('style', '')} ({script.get('score', 0)}分)\n")
            lines.append(self._format_script_markdown(script))
            lines.append("\n")

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

    def _generate_txt(
        self,
        best_script: Dict[str, Any],
        scripts: List[Dict[str, Any]]
    ) -> str:
        """Generate TXT content"""
        lines = []

        # 标题
        lines.append("=" * 50)
        lines.append("直播带货话术")
        lines.append("=" * 50)
        lines.append("")

        # 推荐最佳脚本
        if best_script:
            lines.append("【推荐最佳脚本】")
            lines.append(f"风格: {best_script.get('style', '')}  |  评分: {best_script.get('score', 0)}分")
            if best_script.get('reason'):
                lines.append(f"推荐理由: {best_script['reason']}")
            lines.append("")
            lines.append(self._format_script_txt(best_script))
            lines.append("")
            lines.append("=" * 50)
            lines.append("")

        # 所有脚本
        lines.append("【所有脚本】")
        lines.append("")
        for i, script in enumerate(scripts, 1):
            lines.append(f"--- {i}. {script.get('style', '')} ({script.get('score', 0)}分) ---")
            lines.append(self._format_script_txt(script))
            lines.append("")

        return "".join(lines)

    def _format_script_txt(self, script: Dict[str, Any]) -> str:
        """Format single script as TXT"""
        lines = []
        lines.append(f"【开头吸引】{script.get('opening_hook', '')}")
        lines.append(f"【痛点】{script.get('pain_point', '')}")
        lines.append(f"【解决方案】{script.get('solution', '')}")
        lines.append(f"【证明】{script.get('proof', '')}")
        lines.append(f"【促单】{script.get('offer', '')}")
        return "\n".join(lines)
