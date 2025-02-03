# folder_analyzer_core.py

import os
from pathlib import Path
from typing import List, Dict, NamedTuple, Optional
from datetime import datetime

class FileInfo(NamedTuple):
    """ファイル情報を格納するクラス"""
    path: str           # ファイルの相対パス
    content: str        # ファイル内容
    char_count: int     # 文字数
    line_count: int     # 行数
    file_type: str      # ファイル拡張子

class FolderAnalyzer:
    def __init__(self, root_dir: str, selected_files: Optional[List[str]] = None):
        self.root_dir = Path(root_dir)
        self.default_ignore = {
            "__pycache__",
            ".git",
            "venv",
            ".venv",
            "node_modules",
            "dist",
            "build"
        }
        self.selected_files = selected_files  # 選択されたファイルのリスト

    def collect_files(self) -> List[FileInfo]:
        """選択されたファイルのみを収集する"""
        files = []
        for file_path in self.root_dir.rglob("*"):
            # 除外判定
            if any(ignore in str(file_path) for ignore in self.default_ignore):
                continue
            if not file_path.is_file():
                continue

            rel_path = str(file_path.relative_to(self.root_dir))
            
            # 選択されたファイルのみを収集
            if self.selected_files and rel_path not in self.selected_files:
                continue

            try:
                # ファイル読み込み
                content = file_path.read_text(encoding='utf-8')
                
                # 拡張子取得
                ext = file_path.suffix[1:] if file_path.suffix else 'no_ext'
                
                # 行数カウント
                lines = content.splitlines()
                
                files.append(FileInfo(
                    path=rel_path,
                    content=content,
                    char_count=len(content),
                    line_count=len(lines),
                    file_type=ext
                ))
            except Exception as e:
                print(f"Warning: スキップしたファイル {file_path}: {e}")

        return sorted(files, key=lambda x: x.path)

    def get_directory_structure(self) -> str:
        """ディレクトリ構造を文字列で取得"""
        lines = []
        for file_path in sorted(self.root_dir.rglob("*")):
            if any(ignore in str(file_path) for ignore in self.default_ignore):
                continue

            rel_path = file_path.relative_to(self.root_dir)
            indent = "  " * len(rel_path.parts[:-1])
            if file_path.is_dir():
                lines.append(f"{indent}{file_path.name}/")
            else:
                lines.append(f"{indent}{file_path.name}")
        return "\n".join(lines)

    def analyze(self) -> Dict:
        """選択されたファイルの分析を実行"""
        files = self.collect_files()
        
        # 統計情報の収集
        stats = {
            'total_files': len(files),
            'total_chars': sum(f.char_count for f in files),
            'total_lines': sum(f.line_count for f in files),
            'file_types': {},
            'largest_files': sorted(files, key=lambda x: x.char_count, reverse=True)[:5],
            'directory_structure': self.get_directory_structure(),
            'files': files
        }

        # ファイルタイプごとの集計
        for file in files:
            stats['file_types'][file.file_type] = stats['file_types'].get(file.file_type, 0) + 1

        return stats

    def generate_report(self, show_content: bool = True) -> str:
        """Markdown形式のレポートを生成"""
        stats = self.analyze()
        
        report = [
            "# フォルダ分析レポート\n",
            f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"対象フォルダ: {self.root_dir.absolute()}\n",
            "## 基本情報",
            f"- 総ファイル数: {stats['total_files']:,}個",
            f"- 総文字数: {stats['total_chars']:,}文字",
            f"- 総行数: {stats['total_lines']:,}行\n",
            "## ファイルタイプ別統計"
        ]

        # ファイルタイプ統計
        for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"- {ext}: {count}ファイル")

        # 最大ファイル
        report.extend([
            "\n## 最も大きいファイル（文字数ベース）"
        ])
        for file in stats['largest_files']:
            report.append(f"- {file.path}: {file.char_count:,}文字 ({file.line_count:,}行)")

        # ディレクトリ構造
        report.extend([
            "\n## ディレクトリ構造",
            "```",
            stats['directory_structure'],
            "```"
        ])

        # ファイル内容（オプション）
        if show_content:
            report.extend([
                "\n## ファイル一覧"
            ])
            for file in stats['files']:
                report.extend([
                    f"\n### {file.path}",
                    f"- 文字数: {file.char_count:,}文字",
                    f"- 行数: {file.line_count:,}行",
                    f"```{file.file_type}",
                    file.content,
                    "```"
                ])

        return "\n".join(report)
