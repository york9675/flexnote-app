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

            self.text_area.configure(undo=True, autoseparators=True, maxundo=-1, font=("Arial", 12))
            self.text_area.edit_separator()

            self.text_area.tag_configure("content", font=("Arial", 12))

            menu_bar = tk.Menu(root)
            root.config(menu=menu_bar)

            file_menu = tk.Menu(menu_bar, tearoff=0)
            edit_menu = tk.Menu(menu_bar, tearoff=0)
            view_menu = tk.Menu(menu_bar, tearoff=0)  
            help_menu = tk.Menu(menu_bar, tearoff=0)
            menu_bar.add_cascade(label="File", menu=file_menu)
            menu_bar.add_cascade(label="Edit", menu=edit_menu)
            menu_bar.add_cascade(label="View", menu=view_menu)
            menu_bar.add_cascade(label="Help", menu=help_menu)

            file_menu.add_command(label="New Note", command=self.new_note, accelerator="Ctrl+N")
            file_menu.add_command(label="Open Text File", command=self.open_note, accelerator="Ctrl+O")
            file_menu.add_command(label="Save Text File", command=self.save_note, accelerator="Ctrl+S")
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.on_close, accelerator="Alt+F4")

            edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
            edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
            edit_menu.add_separator()
            edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"), accelerator="Ctrl+X")
            edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"), accelerator="Ctrl+C")
            edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"), accelerator="Ctrl+V")
            edit_menu.add_command(label="Delete", command=lambda: self.text_area.event_generate("<Delete>"), accelerator="Del")
            edit_menu.add_separator()
            edit_menu.add_command(label="Select All", command=lambda: self.text_area.event_generate("<<SelectAll>>"), accelerator="Ctrl+A")

            help_menu.add_command(label="Help", command=self.help)
            help_menu.add_command(label="GitHub", command=self.open_github)
            help_menu.add_separator()
            help_menu.add_command(label="About", command=self.about)

            view_menu_zoom = tk.Menu(view_menu, tearoff=0)
            view_menu.add_cascade(label="Zoom", menu=view_menu_zoom)
            view_menu_zoom.add_command(label="Zoom In", command=lambda: self.zoom(event=None, direction="in"), accelerator="Ctrl+Plus")
            view_menu_zoom.add_command(label="Zoom Out", command=lambda: self.zoom(event=None, direction="out"), accelerator="Ctrl+Minus")
            view_menu_zoom.add_command(label="Reset Zoom", command=lambda: self.reset_zoom(), accelerator="Ctrl+0")

            self.available_fonts = ["Arial", "TkDefaultFont"]
            self.selected_font = tk.StringVar(value="Arial")

            view_menu_font = tk.Menu(view_menu, tearoff=0)
            view_menu.add_cascade(label="Font", menu=view_menu_font)

            for font_name in self.available_fonts:
                view_menu_font.add_radiobutton(label=font_name, variable=self.selected_font, command=self.change_font)

            view_menu_font.add_separator()

            system_fonts_menu = tk.Menu(view_menu_font, tearoff=0)
            view_menu_font.add_cascade(label="System Font", menu=system_fonts_menu)

            system_fonts = tkFont.families()
            for font_name in system_fonts:
                system_fonts_menu.add_radiobutton(label=font_name, variable=self.selected_font, command=self.change_font)

            self.show_status_bar = tk.BooleanVar(value=True)
            view_menu.add_checkbutton(label="Show Ststus Bar", variable=self.show_status_bar, command=self.toggle_status_bar)

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

            self.status_bar = tk.Label(root, text="Character count: 0 | Zoom: 100%", bd=1, relief=tk.SUNKEN, anchor=tk.W)
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            self.update_status_bar_visibility()

            self.file_name = None

        except Exception as e:
            messagebox.showerror("Error", f"An error occurs during the initialization process, and the program will automatically exit after pressing OK.\n\nThe following error occurred:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")
            self.root.destroy()

    def undo(self, event=None):
        try:
            self.text_area.edit_undo()
        except Exception as e:
            messagebox.showerror("Error", f"The following error occurred while trying to undo:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")

    def redo(self, event=None):
        try:
            self.text_area.edit_redo()
        except Exception as e:
            messagebox.showerror("Error", f"The following error occurred while trying to redo:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")

    def update_character_count(self, event):
        try:
            content = self.text_area.get("1.0", "end-1c")
            character_count = len(content.replace('\n', ''))
            current_level = int(self.text_area.tag_cget("content", "font").split()[1])
            zoom_level = int((current_level / 12) * 100)
            self.status_bar.config(text=f"Character count: {character_count} | Zoom: {zoom_level}%")
        except Exception as e:
            messagebox.showerror("Error", f"The following error occurred while trying to update the character count:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")
    
    def new_note(self):
        try:
            unsaved_changes = self.text_area.edit_modified()

            if unsaved_changes:
                response = messagebox.askyesnocancel("Unsaved Changes!", "You didn't save your note!\nWant to save your note before open new note?", icon='warning')

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
            messagebox.showerror("Error", f"The following error occurred while trying to create a new note:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")
    
    def open_note(self):
        try:
            unsaved_changes = self.text_area.edit_modified()

            if unsaved_changes:
                response = messagebox.askyesnocancel("Unsaved Changes!", "You didn't save your note!\nWant to save your note before open other note?", icon='warning')

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
            messagebox.showerror("Error", f"The following error occurred while trying to open a text file:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")

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
            messagebox.showerror("Error", f"The following error occurred while trying to save text file:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")

    def on_close(self):
        try:
            unsaved_changes = self.text_area.edit_modified()

            if unsaved_changes:
                response = messagebox.askyesnocancel("Unsaved Changes!", "You didn't save your note!\nWant to save your note before exit?", icon='warning')

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
            messagebox.showerror("Error", f"The following error occurred while trying to close the program:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")
            self.root.destroy()

    def open_github(self):
        try:
            webbrowser.open("https://www.github.com/york9675/flexnote-app")
        except Exception as e:
            messagebox.showerror("Error", f"The following error occurred while trying to open the GitHub page:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")

    def help(self):
        messagebox.showinfo("Help", "This is a simple notepad program, you can use it to write some simple text files.\n\nThe following is an introduction to shortcut keys, which can be used to improve ease of use:\n1 . Create new notepad: Ctrl+N\n2. Open text file: Ctrl+O\n3. Save text file: Ctrl+S\n4. Zoom in: Ctrl+plus sign/mouse wheel forward\n5. Zoom out: Ctrl+minus sign / Mouse wheel back\n6. Reset zoom: Ctrl+0\n7. Cut: Ctrl+X\n8. Copy: Ctrl+C\n9. Paste: Ctrl+V\n10. Delete: Del\n11. Select all: Ctrl+A\n12. Undo: Ctrl+Z\n13. Redo: Ctrl+Y\n\nYou can also customize the font you want to display through the font options in the view menu!")

    def about(self):
        messagebox.showinfo("About FlexNote", "A very simple notepad program, easy to use with no other complicated features.\n\nFlexNote Free\nVersion: 1.0\nLast update: 2024/02/06\n\nDeveloper: York\nTranslated by: York\n\nIf you have any problems during use, please report it to the GitHub issue page:\nhttps://github.com/york9675/flexnote-app/issues\n\nYou can also contact the author through the following methods:\nDiscord: york0524")

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

            self.status_bar.config(text=f"Character count: {character_count} | Zoom: {zoom_level}%")
        except Exception as e:
            messagebox.showerror("Error", f"The following error occurred while trying to zoom in/out:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")

    def reset_zoom(self):
        try:
            self.text_area.tag_configure("content", font=(self.selected_font.get(), 12))
            self.text_area.tag_add("content", "1.0", tk.END)
            content = self.text_area.get("1.0", "end-1c")
            character_count = len(content.replace('\n', ''))

            self.status_bar.config(text=f"Character count: {character_count} | Zoom: 100%")
        except Exception as e:
            messagebox.showerror("Error", f"The following error occurred while trying to reset zoom:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")

    def toggle_status_bar(self):
        try:
            self.show_status_bar = not self.show_status_bar
            self.update_sizegrip_visibility()
            self.update_product_label_visibility()
            self.update_status_bar_visibility()
        except Exception as e:
            messagebox.showerror("Error", f"The following error occurred while trying to toggle the status bar:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")

    def update_sizegrip_visibility(self):
        try:
            if self.show_status_bar:
                self.sizegrip.pack(side=tk.RIGHT, anchor=tk.SE)
            else:
                self.sizegrip.pack_forget()
        except Exception as e:
            messagebox.showerror("Error", f"The following error occurred while trying to update the sizegrip visibility:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")

    def update_product_label_visibility(self):
        try:
            if self.show_status_bar:
                self.product_label.pack(side=tk.RIGHT)
            else:
                self.product_label.pack_forget()
        except Exception as e:
            messagebox.showerror("Error", f"The following error occurred while trying to update the product label visibility:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")

    def update_status_bar_visibility(self):
        try:
            if self.show_status_bar:
                self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            else:
                self.status_bar.pack_forget()
        except Exception as e:
            messagebox.showerror("Error", f"The following error occurred while trying to update the status bar visibility:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")

    def update_title(self):
        try:
            if self.file_name:
                full_path = os.path.abspath(self.file_name)
                title = f"FlexNote [{full_path}]"
            else:
                title = "FlexNote"
            self.root.title(title)
        except Exception as e:
            messagebox.showerror("Error", f"The following error occurred while trying to update the title bar:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")

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
            messagebox.showerror("Error", f"The following error occurred while trying to change the font:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = FlexNoteApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurs, the program will automatically exit after pressing OK.\n\nThe following error occurred:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}")
        root.destroy()
