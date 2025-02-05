# PasteFlow

**PasteFlow** is a tool that analyzes files within a specified folder, generating a report with statistics such as the total number of files, characters, lines, file type counts, and directory structure. The generated report is designed to be used as data for AI prompts. In addition to a graphical user interface (GUI) for intuitive folder browsing and report generation, PasteFlow also provides a command-line interface (CLI) for direct execution.

## Features

- **Folder File Analysis**  
  Calculates total file count, total characters, total lines, and provides statistics by file type.

- **Large File Extraction**  
  Lists the largest files based on character count and displays detailed information.

- **Directory Structure Visualization**  
  Outputs the folder’s hierarchy in a text format for easy inspection.

- **Data Generation for AI Prompts**  
  Produces a report that can be directly used as input data for AI prompts.

- **Intuitive GUI**  
  Offers a Tkinter-based graphical interface to select folders, choose specific files, and generate reports with ease.

- **Clipboard Integration**  
  Automatically copies the analysis result to the clipboard for convenient use in other applications.

## File Structure

The table below summarizes the main files included in the project along with their roles:

| File Name           | Description
| ------------------- | --------------------------------------------------------------------------------------------
| `PasteFlow_core.py` | Implements the core functionality for folder analysis, including file data collection, analysis, and report generation.
| `PasteFlow_gui.py`  | Provides a GUI for folder selection, analysis execution, result display, and clipboard copying.
| `requirements.txt`  | Lists the required Python packages.

## System Requirements

- **Python** 3.x  
  *Note:* The GUI version requires Tkinter, which is typically included with standard Python distributions.
- Required libraries (listed in `requirements.txt`):
  - `pyperclip`
  - Standard libraries such as `os`, `pathlib`, `tkinter`, `threading`, etc.

## Installation

1. **Clone the Repository**  
   Open your terminal or command prompt and run the following command:

   ```bash
   git clone https://github.com/monyuonyu/PasteFlow.git
   ```

2. **Install the Required Libraries**  
   Navigate to the cloned directory and run:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Graphical User Interface (GUI) Version

1. **Launching the GUI**  
   Start the GUI application with the following command:

   ```bash
   python PasteFlow_gui.py
   ```

2. **How to Use the GUI**  
   - **Folder Selection:** Click the "Browse..." button to choose the folder you want to analyze.
   - **File Selection:** Use the displayed file tree to individually select or deselect files for analysis.
   - **Options:** Check or uncheck the "Show file content" option to include or exclude file contents in the report.
   - **Run Analysis:** Click the "Analyze Folder and Copy to Clipboard" button to start the analysis. The resulting report will be automatically copied to your clipboard.

### Command-Line Interface (CLI) Usage

`PasteFlow_core.py` also provides an interface for executing folder analysis directly from the command line. (Although direct argument parsing is not built into the current code, the sample below demonstrates how to use the `FolderAnalyzer` class for CLI execution.)

#### Example: Running Folder Analysis from the Command Line

1. **Sample CLI Script**  
   Create a Python script (for example, `sample_cli.py`) with the following content:

   ```python
   # sample_cli.py
   # -*- coding: utf-8 -*-
   # This script parses command-line arguments to analyze a specified folder and file list,
   # then outputs the result to standard output.
   import argparse
   from PasteFlow_core import FolderAnalyzer

   def main():
       # Set up argument parsing
       parser = argparse.ArgumentParser(description="PasteFlow - Folder Analysis Tool (CLI Version)")
       parser.add_argument('-d', '--dir', required=True, help="Path to the folder to be analyzed")
       parser.add_argument('-f', '--files', help="Comma-separated list of files to analyze (if not specified, all files will be analyzed)")
       parser.add_argument('--no-content', action='store_true', help="Exclude file content from the report")
       args = parser.parse_args()

       # Generate the list of selected files (if provided)
       selected_files = args.files.split(",") if args.files else None

       # Use FolderAnalyzer to perform the analysis
       analyzer = FolderAnalyzer(args.dir, selected_files=selected_files)
       report = analyzer.generate_report(show_content=not args.no_content)
       print(report)

   if __name__ == '__main__':
       main()
   ```

2. **Running the Script**  
   After creating the sample CLI script (e.g., `sample_cli.py`), execute it from the command line as follows:

   ```bash
   python sample_cli.py --dir "C:\path\to\folder" --files "PasteFlow_gui.py,PasteFlow_core.py" --no-content
   ```

   - Use the `--dir` (or `-d`) option to specify the path to the folder to be analyzed.
   - Use the `--files` (or `-f`) option to specify a comma-separated list of file names to analyze. If omitted, all files in the folder will be analyzed.
   - The `--no-content` flag excludes file contents from the generated report.

*Note:* The above sample code is a simple example of how to use the `FolderAnalyzer` class for CLI-based analysis. You may customize it further to suit your specific needs.

## License

This project is licensed under the [GPL3.0 License](https://www.gnu.org/licenses/gpl-3.0.html).

---


# PasteFlow (日本語)

**PasteFlow** は、指定したフォルダ内のファイルを解析し、ファイル数、文字数、行数、ファイルタイプ別の統計情報やディレクトリ構造などをレポート形式で出力するツールです。生成されたレポートは、AIプロンプトにまとめて投げるためのデータとして活用できます。GUI（グラフィカルユーザーインターフェイス）による操作も可能なため、直感的にフォルダの内容を確認・加工することができます。

## 特徴

- **フォルダ内ファイルの統計解析**  
  ファイル数、文字数、行数の合計やファイルタイプ別の統計情報を取得します。

- **大きいファイルの抽出**  
  文字数ベースで上位の大きなファイルをリストアップし、詳細情報を表示します。

- **ディレクトリ構造の可視化**  
  フォルダ内の階層構造をテキスト形式で確認できます。

- **AIプロンプト用データ生成**  
  解析結果をAIプロンプトにまとめて投げるためのデータとして出力でき、AIとの連携が容易になります。

- **GUIによる直感的操作**  
  Tkinter を用いたグラフィカルな操作画面で、フォルダの選択、ファイルの選択・解除、レポートの生成などが行えます。

- **クリップボード連携**  
  解析結果をクリップボードに自動コピーするため、他のツールへの貼り付けが容易です。

## ファイル構成

以下の表は、プロジェクトに含まれる主要なファイルとその役割の比較です。

| ファイル名          | 説明                                                     
| ------------------- | --------------------------------------------------------
| `PasteFlow_core.py` | フォルダ解析のコア機能を実装。ファイル情報の収集、解析、レポート生成を行う。
| `PasteFlow_gui.py`  | GUI を用いてフォルダの選択や解析実行、結果の表示・クリップボードへのコピーを実現。 
| `requirements.txt`  | 必要なPythonパッケージ一覧

## システム要件

- **Python** 3.x  
  ※ GUI版の場合、Tkinter が同梱されている必要があります。  
- 必要なライブラリ（`requirements.txt` 内に記載）:
  - `pyperclip`  
  - その他標準ライブラリ（`os`, `pathlib`, `tkinter`, `threading` など）

## インストール方法

1. **リポジトリのクローン**  
   ターミナルやコマンドプロンプトで以下のコマンドを実行してください。

   ```bash
   git clone https://github.com/monyuonyu/PasteFlow.git
   ```

2. **必要なライブラリのインストール**  
   クローンしたディレクトリ内で以下のコマンドを実行してください。

   ```bash
   pip install -r requirements.txt
   ```

## 使い方

### GUI版

1. **起動方法**  
   以下のコマンドで GUI アプリケーションを起動します。

   ```bash
   python PasteFlow_gui.py
   ```

2. **操作手順**  
   - **フォルダの選択**: 「参照...」ボタンをクリックして解析対象のフォルダを選択します。  
   - **ファイルの選択**: 表示されるファイルツリーから、解析対象のファイルを個別に選択・解除できます。  
   - **オプション設定**: 「ファイル内容を表示」のチェックボックスで、レポートにファイルの中身を含めるかどうかを選択します。  
   - **解析実行**: 「フォルダを分析してクリップボードにコピー」ボタンを押すと、解析が開始され、結果がクリップボードにコピーされます。

### コマンドライン（CUI）での利用

`PasteFlow_core.py` は、コマンドラインから直接フォルダ解析を実行するためのインターフェイスも備えています。  
（※ 現在のコードには直接の引数解析は実装されていませんが、FolderAnalyzer クラスを利用した簡易な CLI 実行方法のサンプルとして以下の説明をご参照ください。）

#### 例：コマンドラインからフォルダ解析を実行する方法

1. **実行方法の一例**  
   以下のような Python スクリプトを作成することで、コマンドラインから解析を実行できます。  
   （※ この例は利用者側で任意に作成するためのサンプルコードです。）

   ```python
   # sample_cli.py
   # -*- coding: utf-8 -*-
   # このスクリプトは、コマンドライン引数で指定されたフォルダとファイルを解析し、結果を標準出力に表示します。
   import argparse
   from PasteFlow_core import FolderAnalyzer

   def main():
       # 引数のパース設定
       parser = argparse.ArgumentParser(description="PasteFlow - フォルダ解析ツール (CUI版)")
       parser.add_argument('-d', '--dir', required=True, help="解析対象のフォルダパス")
       parser.add_argument('-f', '--files', help="解析対象のファイル（カンマ区切りで指定、指定しない場合は全ファイル）")
       parser.add_argument('--no-content', action='store_true', help="レポートにファイル内容を含めない")
       args = parser.parse_args()

       # 選択ファイルのリストを生成（ファイルが指定された場合）
       selected_files = args.files.split(",") if args.files else None

       # FolderAnalyzer を用いて解析実行
       analyzer = FolderAnalyzer(args.dir, selected_files=selected_files)
       report = analyzer.generate_report(show_content=not args.no_content)
       print(report)

   if __name__ == '__main__':
       main()
   ```

2. **実行例**  
   上記のスクリプト（例: `sample_cli.py`）を作成後、以下のように実行します。

   ```bash
   python sample_cli.py --dir "C:\path\to\folder" --files "PasteFlow_gui.py,PasteFlow_core.py" --no-content
   ```

   - `--dir`（または `-d`）オプションで解析対象のフォルダパスを指定します。  
   - `--files`（または `-f`）オプションで、カンマ区切りのファイル名を指定できます。省略した場合は、フォルダ内の全ファイルが対象となります。  
   - `--no-content` オプションを指定すると、レポート生成時に各ファイルの内容が含まれなくなります。

※ 上記のサンプルコードは、FolderAnalyzer クラスを用いた簡易な CLI 実行方法の一例です。実際の運用に合わせて適宜カスタマイズしてください。

## ライセンス

このプロジェクトは、[GPL3.0 License](https://www.gnu.org/licenses/gpl-3.0.html) のもとで公開されています。
