# folder_analyzer_gui.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from PasteFlow_core import FolderAnalyzer
import os
import pyperclip  # クリップボード操作用

class FolderAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PasteFlow - フォルダ分析ツール")
        self.root.geometry("800x600")
        
        # メインフレーム
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # フォルダ選択部分
        self.folder_frame = ttk.LabelFrame(self.main_frame, text="フォルダ選択", padding="5")
        self.folder_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(self.folder_frame, textvariable=self.folder_path)
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        self.browse_button = ttk.Button(self.folder_frame, text="参照...", command=self.browse_folder)
        self.browse_button.grid(row=0, column=1, padx=5)

        # ファイル選択ツリー
        self.tree_frame = ttk.LabelFrame(self.main_frame, text="分析対象ファイル", padding="5")
        self.tree_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # ボタンフレーム
        self.button_frame = ttk.Frame(self.tree_frame)
        self.button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        self.select_all_button = ttk.Button(
            self.button_frame,
            text="全選択",
            command=lambda: self.toggle_all_files(True)
        )
        self.select_all_button.grid(row=0, column=0, padx=2)
        
        self.deselect_all_button = ttk.Button(
            self.button_frame,
            text="全解除",
            command=lambda: self.toggle_all_files(False)
        )
        self.deselect_all_button.grid(row=0, column=1, padx=2)

        # ファイルツリー
        self.tree = ttk.Treeview(self.tree_frame, height=20, selectmode="extended")
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # ツリーのスクロールバー
        self.tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

        # ツリーの列設定
        self.tree["columns"] = ("select",)
        self.tree.column("#0", width=400, stretch=tk.YES)  # ファイルパス用
        self.tree.column("select", width=50, anchor=tk.CENTER)  # チェックボックス用
        
        self.tree.heading("#0", text="ファイルパス")
        self.tree.heading("select", text="選択")

        # ファイル選択状態を保存する辞書
        self.file_selections = {}

        # その他のオプション
        self.option_frame = ttk.LabelFrame(self.main_frame, text="オプション", padding="5")
        self.option_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.show_content = tk.BooleanVar(value=True)
        self.content_check = ttk.Checkbutton(
            self.option_frame, 
            text="ファイル内容を表示",
            variable=self.show_content
        )
        self.content_check.grid(row=0, column=0, padx=5)
        
        # 分析実行ボタン
        self.analyze_button = ttk.Button(
            self.main_frame,
            text="フォルダを分析してクリップボードにコピー",
            command=self.analyze_folder
        )
        self.analyze_button.grid(row=3, column=0, columnspan=2, pady=5)
        
        # 進捗バー
        self.progress = ttk.Progressbar(
            self.main_frame,
            mode='determinate',
            length=300
        )
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # グリッド設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.folder_frame.columnconfigure(0, weight=1)
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(1, weight=1)

        # ツリーのクリックイベントを設定
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        self.tree.bind('<Button-1>', self.on_tree_click)
        self.tree.bind('<ButtonRelease-1>', self.on_tree_release)
        self.tree.bind('<space>', self.on_space_key)  # スペースキーのバインド
        self.clicked_item = None  # クリックされたアイテムを追跡

        # Enterキーのバインド
        self.root.bind('<Return>', self.analyze_folder)

    def browse_folder(self):
        """フォルダ選択ダイアログを表示"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path.set(folder_path)
            self.update_file_tree()

    def update_file_tree(self):
        """ファイルツリーを更新"""
        # ツリーをクリア
        self.tree.delete(*self.tree.get_children())
        self.file_selections.clear()

        folder_path = self.folder_path.get()
        if not folder_path:
            return

        # デフォルトの除外パターン
        default_ignore = {
            "__pycache__",
            ".git",
            "venv",
            ".venv",
            "node_modules",
            "dist",
            "build"
        }

        try:
            # フォルダ構造を再帰的に追加
            for root_dir, dirs, files in os.walk(folder_path):
                # 除外フォルダをスキップ
                dirs[:] = [d for d in dirs if d not in default_ignore]
                
                # ルートフォルダからの相対パスを取得
                rel_path = os.path.relpath(root_dir, folder_path)
                if rel_path == ".":
                    rel_path = ""

                # フォルダをツリーに追加
                if rel_path:
                    folder_parts = rel_path.split(os.sep)
                    parent = ""
                    for i, part in enumerate(folder_parts):
                        current_path = os.sep.join(folder_parts[:i+1])
                        parent_path = os.sep.join(folder_parts[:i]) if i > 0 else ""
                        if not self.tree.exists(current_path):
                            self.tree.insert(parent_path, 'end', current_path, text=part, values=(""))

                # ファイルを追加
                parent_path = rel_path if rel_path else ""
                for file in sorted(files):
                    if any(ignore in file for ignore in default_ignore):
                        continue
                    file_path = os.sep.join([rel_path, file]) if rel_path else file
                    self.file_selections[file_path] = tk.BooleanVar(value=True)
                    self.tree.insert(parent_path, 'end', file_path, text=file, 
                                   values=("☑" if self.file_selections[file_path].get() else "☐"))

        except Exception as e:
            messagebox.showerror("エラー", f"ファイルツリーの更新中にエラーが発生しました：\n{str(e)}")

    def on_tree_click(self, event):
        """クリック開始時のイベントを処理"""
        x, y = event.x, event.y
        self.clicked_item = None

        # クリックされた場所を特定
        item = self.tree.identify('item', x, y)
        column = self.tree.identify_column(x)
        
        if item and item in self.file_selections and column == "#1":
            self.clicked_item = item

    def on_tree_release(self, event):
        """クリック解放時のイベントを処理"""
        if not self.clicked_item:
            return

        x, y = event.x, event.y
        item = self.tree.identify('item', x, y)
        column = self.tree.identify_column(x)
        
        # 同じアイテムの同じ列でリリースされた場合のみ処理
        if item == self.clicked_item and column == "#1":
            current_state = self.file_selections[item].get()
            self.file_selections[item].set(not current_state)
            self.tree.set(item, "select", "☑" if not current_state else "☐")

    def on_tree_double_click(self, event):
        """ダブルクリック時のイベントを処理"""
        x, y = event.x, event.y
        item = self.tree.identify('item', x, y)
        column = self.tree.identify_column(x)
        
        if item and item in self.file_selections and column == "#1":
            current_state = self.file_selections[item].get()
            self.file_selections[item].set(not current_state)
            self.tree.set(item, "select", "☑" if not current_state else "☐")

    def on_space_key(self, event):
        """スペースキーが押されたときに選択アイテムのチェックボックスをトグル"""
        selected_items = self.tree.selection()
        for item in selected_items:
            if item in self.file_selections:
                current_state = self.file_selections[item].get()
                self.file_selections[item].set(not current_state)
                self.tree.set(item, "select", "☑" if not current_state else "☐")
        return "break"  # デフォルトのスペースキー動作をキャンセル

    def analyze_folder(self, event=None):
        """フォルダ分析を実行"""
        folder_path = self.folder_path.get()
        if not folder_path:
            messagebox.showerror("エラー", "フォルダを選択してください")
            return

        selected_files = self.get_selected_files()
        if not selected_files:
            messagebox.showerror("エラー", "分析対象のファイルを選択してください")
            return

        # UI更新
        self.analyze_button.state(['disabled'])
        self.progress["value"] = 0

        # 別スレッドで分析を実行
        thread = threading.Thread(target=self._analyze_thread, args=(selected_files,))
        thread.start()

    def _analyze_thread(self, selected_files):
        """分析処理を別スレッドで実行"""
        try:
            analyzer = FolderAnalyzer(self.folder_path.get(), selected_files)
            stats = analyzer.analyze()
            
            # プログレスバーの更新（全体100%）
            self.root.after(0, self._update_progress, 100)
            
            # レポート生成
            report = analyzer.generate_report(show_content=self.show_content.get())
            
            # クリップボードにコピー
            self.root.after(0, self._copy_to_clipboard, report)
            
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, self._cleanup)

    def _update_progress(self, value):
        """プログレスバーを更新"""
        self.progress["value"] = value

    def _copy_to_clipboard(self, text):
        """結果をクリップボードにコピー"""
        pyperclip.copy(text)
        messagebox.showinfo("成功", "分析結果をクリップボードにコピーしました")

    def _show_error(self, error_msg):
        """エラーメッセージを表示"""
        messagebox.showerror("エラー", f"分析中にエラーが発生しました：\n{error_msg}")

    def _cleanup(self):
        """UI要素を元に戻す"""
        self.analyze_button.state(['!disabled'])
        self.progress["value"] = 0

    def toggle_all_files(self, state: bool):
        """全てのファイルの選択状態を切り替え"""
        for file_path, var in self.file_selections.items():
            var.set(state)
            self.tree.set(file_path, "select", "☑" if state else "☐")

    def get_selected_files(self):
        """選択されているファイルのパスを取得"""
        return [path for path, var in self.file_selections.items() if var.get()]

def main():
    root = tk.Tk()
    app = FolderAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
