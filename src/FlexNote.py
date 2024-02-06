import tkinter as tk
import tkinter.font as tkFont
from tkinter import scrolledtext, filedialog, messagebox, ttk
import os
import traceback
import webbrowser

class FlexNoteApp:
    def __init__(self, root):
        try:
            self.root = root
            self.root.title("FlexNote")

            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(current_dir, "icon.png")

            self.root.tk.call("wm", "iconphoto", root._w, tk.PhotoImage(file=icon_path))

            self.root.protocol("WM_DELETE_WINDOW", self.on_close)

            self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=25)
            self.text_area.pack(expand=True, fill='both')

            self.text_area.configure(undo=True, autoseparators=True, maxundo=-1, font=("微軟正黑體", 12))
            self.text_area.edit_separator()

            self.text_area.tag_configure("content", font=("微軟正黑體", 12))

            menu_bar = tk.Menu(root)
            root.config(menu=menu_bar)

            file_menu = tk.Menu(menu_bar, tearoff=0)
            edit_menu = tk.Menu(menu_bar, tearoff=0)
            view_menu = tk.Menu(menu_bar, tearoff=0)  
            help_menu = tk.Menu(menu_bar, tearoff=0)
            menu_bar.add_cascade(label="檔案", menu=file_menu)
            menu_bar.add_cascade(label="編輯", menu=edit_menu)
            menu_bar.add_cascade(label="檢視", menu=view_menu)
            menu_bar.add_cascade(label="幫助", menu=help_menu)

            file_menu.add_command(label="新建記事本", command=self.new_note, accelerator="Ctrl+N")
            file_menu.add_command(label="開啟文字檔", command=self.open_note, accelerator="Ctrl+O")
            file_menu.add_command(label="儲存文字檔", command=self.save_note, accelerator="Ctrl+S")
            file_menu.add_separator()
            file_menu.add_command(label="退出", command=self.on_close, accelerator="Alt+F4")

            edit_menu.add_command(label="復原", command=self.undo, accelerator="Ctrl+Z")
            edit_menu.add_command(label="重作", command=self.redo, accelerator="Ctrl+Y")
            edit_menu.add_separator()
            edit_menu.add_command(label="剪下", command=lambda: self.text_area.event_generate("<<Cut>>"), accelerator="Ctrl+X")
            edit_menu.add_command(label="複製", command=lambda: self.text_area.event_generate("<<Copy>>"), accelerator="Ctrl+C")
            edit_menu.add_command(label="貼上", command=lambda: self.text_area.event_generate("<<Paste>>"), accelerator="Ctrl+V")
            edit_menu.add_command(label="刪除", command=lambda: self.text_area.event_generate("<Delete>"), accelerator="Del")
            edit_menu.add_separator()
            edit_menu.add_command(label="全選", command=lambda: self.text_area.event_generate("<<SelectAll>>"), accelerator="Ctrl+A")

            help_menu.add_command(label="幫助", command=self.help)
            help_menu.add_command(label="GitHub", command=self.open_github)
            help_menu.add_separator()
            help_menu.add_command(label="關於", command=self.about)

            view_menu_zoom = tk.Menu(view_menu, tearoff=0)
            view_menu.add_cascade(label="縮放", menu=view_menu_zoom)
            view_menu_zoom.add_command(label="放大", command=lambda: self.zoom(event=None, direction="in"), accelerator="Ctrl+加號")
            view_menu_zoom.add_command(label="縮小", command=lambda: self.zoom(event=None, direction="out"), accelerator="Ctrl+減號")
            view_menu_zoom.add_command(label="重設縮放", command=lambda: self.reset_zoom(), accelerator="Ctrl+0")

            self.available_fonts = ["微軟正黑體", "標楷體", "新細明體", "Arial", "TkDefaultFont"]
            self.selected_font = tk.StringVar(value="微軟正黑體")

            view_menu_font = tk.Menu(view_menu, tearoff=0)
            view_menu.add_cascade(label="字體", menu=view_menu_font)

            for font_name in self.available_fonts:
                view_menu_font.add_radiobutton(label=font_name, variable=self.selected_font, command=self.change_font)

            view_menu_font.add_separator()

            system_fonts_menu = tk.Menu(view_menu_font, tearoff=0)
            view_menu_font.add_cascade(label="系統字體", menu=system_fonts_menu)

            system_fonts = tkFont.families()
            for font_name in system_fonts:
                system_fonts_menu.add_radiobutton(label=font_name, variable=self.selected_font, command=self.change_font)

            self.show_status_bar = tk.BooleanVar(value=True)
            view_menu.add_checkbutton(label="顯示狀態列", variable=self.show_status_bar, command=self.toggle_status_bar)

            root.bind("<Control-n>", lambda event=None: self.new_note())
            root.bind("<Control-o>", lambda event=None: self.open_note())
            root.bind("<Control-s>", lambda event=None: self.save_note())
            root.bind("<Control-MouseWheel>", lambda event=None: self.zoom(event))
            root.bind("<Control-plus>", lambda event=None: self.zoom(event, direction="in"))
            root.bind("<Control-minus>", lambda event=None: self.zoom(event, direction="out"))
            root.bind("<Control-0>", lambda event=None: self.reset_zoom())

            self.text_area.bind("<KeyRelease>", self.update_character_count)

            self.sizegrip = ttk.Sizegrip(root)
            self.sizegrip.pack(side=tk.RIGHT, anchor=tk.SE)
            self.update_sizegrip_visibility()

            self.product_label = tk.Label(root, text=" FlexNote V 1.0 ", bd=1, relief=tk.SUNKEN, anchor=tk.E)
            self.product_label.pack(side=tk.RIGHT)

            self.status_bar = tk.Label(root, text="字元數: 0 | 縮放比例: 100%", bd=1, relief=tk.SUNKEN, anchor=tk.W)
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            self.update_status_bar_visibility()

            self.file_name = None

        except Exception as e:
            messagebox.showerror("錯誤", f"初始化過程中發生錯誤，將在按下確定後自動退出程式。\n\n發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")
            self.root.destroy()

    def undo(self, event=None):
        try:
            self.text_area.edit_undo()
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試復原時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")

    def redo(self, event=None):
        try:
            self.text_area.edit_redo()
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試重做時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")

    def update_character_count(self, event):
        try:
            content = self.text_area.get("1.0", "end-1c")
            character_count = len(content.replace('\n', ''))
            current_level = int(self.text_area.tag_cget("content", "font").split()[1])
            zoom_level = int((current_level / 12) * 100)
            self.status_bar.config(text=f"字元數: {character_count} | 縮放比例: {zoom_level}%")
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試更新字元數時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")
    
    def new_note(self):
        try:
            unsaved_changes = self.text_area.edit_modified()

            if unsaved_changes:
                response = messagebox.askyesnocancel("未儲存的變更!", "你沒有存你的記事本!\n想在開新記事本前儲存嗎?", icon='warning')

                if response == True:
                    self.save_note()
                    self.text_area.delete(1.0, tk.END)
                    self.file_name = None
                elif response == False:
                    self.text_area.delete(1.0, tk.END)
                    self.file_name = None
                else:
                    pass
            else:
                self.text_area.delete(1.0, tk.END)
                self.file_name = None

            self.update_title()
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試新建記事本時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")
    
    def open_note(self):
        try:
            unsaved_changes = self.text_area.edit_modified()

            if unsaved_changes:
                response = messagebox.askyesnocancel("未儲存的變更!", "你沒有存你的記事本!\n想在開啟其他記事本前儲存嗎?", icon='warning')

                if response == True:
                    self.save_note()
                    file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])

                    if file_path:
                        with open(file_path, 'r') as file:
                            content = file.read()
                            self.text_area.delete(1.0, tk.END)
                            self.text_area.insert(tk.END, content)
                            self.text_area.edit_modified(False)
                            self.file_name = file_path  
                elif response == False:
                    file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])

                    if file_path:
                        with open(file_path, 'r') as file:
                            content = file.read()
                            self.text_area.delete(1.0, tk.END)
                            self.text_area.insert(tk.END, content)
                            self.text_area.edit_modified(False)
                            self.file_name = file_path  
                else:
                    pass
            else:
                file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])

                if file_path:
                    with open(file_path, 'r') as file:
                        content = file.read()
                        self.text_area.delete(1.0, tk.END)
                        self.text_area.insert(tk.END, content)
                        self.text_area.edit_modified(False)
                        self.file_name = file_path  

            self.update_title()  
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試開啟文字檔時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")

    def save_note(self):
        try:
            if self.file_name:
                file_path = self.file_name
            else:
                file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                with open(file_path, 'w') as file:
                    content = self.text_area.get(1.0, tk.END)
                    file.write(content)
                    self.text_area.edit_modified(False)
                    self.file_name = file_path

            self.update_title()
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試儲存文字檔時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")

    def on_close(self):
        try:
            unsaved_changes = self.text_area.edit_modified()

            if unsaved_changes:
                response = messagebox.askyesnocancel("未儲存的變更!", "你沒有存你的記事本!\n想在退出程式前儲存嗎?", icon='warning')

                if response == True:
                    self.save_note()
                    self.root.destroy()
                elif response == False:
                    self.root.destroy()
                else:
                    pass
            else:
                self.root.destroy()
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試退出程式時發生錯誤，將在按下確定後自動退出程式。\n\n發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")
            self.root.destroy()

    def help(self):
        messagebox.showinfo("幫助", "這是一個簡單的記事本程式，你可以使用它來寫一些簡單的文字檔。\n\n以下為快捷鍵的介紹，可用於提升使用便捷性:\n1.   新建記事本: Ctrl+N\n2.   開啟文字檔: Ctrl+O\n3.   儲存文字檔: Ctrl+S\n4.   放大: Ctrl+加號 / 滑鼠滾輪往前\n5.   縮小: Ctrl+減號 / 滑鼠滾輪往後\n6.   重設縮放比例: Ctrl+0\n7.   剪下: Ctrl+X\n8.   複製: Ctrl+C\n9.   貼上: Ctrl+V\n10. 刪除: Del\n11. 全選: Ctrl+A\n12. 復原: Ctrl+Z\n13. 重作: Ctrl+Y\n\n您也可以透過檢視選單裡面的字體選項自訂您要顯示的字體!")

    def open_github(self):
        try:
            webbrowser.open("https://www.github.com/york9675/flexnote-app")
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試開啟GitHub頁面時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")

    def about(self):
        messagebox.showinfo("關於FlexNote", "一個非常簡單的記事本程式，簡單易使用，沒有其他複雜功能。\n\nFlexNote Free\n版本: 1.0\n最後更新: 2024/02/06\n\n作者: York\n\n使用上有任何問題請至GitHub的issue頁面回報:\nhttps://github.com/york9675/flexnote-app/issues\n\n也可透過以下方式聯繫作者:\nDiscord: york0524")

    def zoom(self, event, direction=None):
        try:
            if direction == "in" or (event and event.delta > 0):
                current_size = int(self.text_area.tag_cget("content", "font").split()[1])
                new_size = current_size + 1
                self.text_area.tag_configure("content", font=(self.selected_font.get(), new_size))
            elif direction == "out" or (event and event.delta < 0):
                current_size = int(self.text_area.tag_cget("content", "font").split()[1])
                new_size = max(1, current_size - 1)
                self.text_area.tag_configure("content", font=(self.selected_font.get(), new_size))
            else:
                return

            self.text_area.tag_add("content", "1.0", tk.END)

            zoom_level = int((new_size / 12) * 100)

            content = self.text_area.get("1.0", "end-1c")
            character_count = len(content.replace('\n', ''))

            self.status_bar.config(text=f"字元數: {character_count} | 縮放比例: {zoom_level}%")
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試縮放時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")

    def reset_zoom(self):
        try:
            self.text_area.tag_configure("content", font=(self.selected_font.get(), 12))
            self.text_area.tag_add("content", "1.0", tk.END)
            content = self.text_area.get("1.0", "end-1c")
            character_count = len(content.replace('\n', ''))

            self.status_bar.config(text=f"字元數: {character_count} | 縮放比例: 100%")
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試重設縮放時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")

    def toggle_status_bar(self):
        try:
            self.show_status_bar = not self.show_status_bar
            self.update_sizegrip_visibility()
            self.update_product_label_visibility()
            self.update_status_bar_visibility()
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試切換狀態列時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")

    def update_sizegrip_visibility(self):
        try:
            if self.show_status_bar:
                self.sizegrip.pack(side=tk.RIGHT, anchor=tk.SE)
            else:
                self.sizegrip.pack_forget()
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試更新Sizegrip可見性時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")

    def update_product_label_visibility(self):
        try:
            if self.show_status_bar:
                self.product_label.pack(side=tk.RIGHT)
            else:
                self.product_label.pack_forget()
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試更新產品名稱時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")

    def update_status_bar_visibility(self):
        try:
            if self.show_status_bar:
                self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            else:
                self.status_bar.pack_forget()
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試更新狀態列時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")

    def update_title(self):
        try:
            if self.file_name:
                full_path = os.path.abspath(self.file_name)
                title = f"FlexNote [{full_path}]"
            else:
                title = "FlexNote"
            self.root.title(title)
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試更新標題時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")

    def change_font(self):
        try:
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()

            selected_font = self.selected_font.get()
            self.text_area.configure(font=(selected_font, 12))
            self.text_area.tag_configure("content", font=(selected_font, 12))
            self.text_area.tag_add("content", "1.0", tk.END)

            self.root.geometry(f"{window_width}x{window_height}")
        except Exception as e:
            messagebox.showerror("錯誤", f"在嘗試更改字體時發生以下錯誤:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = FlexNoteApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("錯誤", f"發生以下錯誤，將在按下確定後自動退出程式:\n{str(e)}\n\n詳細資料:\n{traceback.format_exc()}")
        root.destroy()
