import tkinter as tk
import gettext
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(_("Welcome to our application"))

        self.label = tk.Label(root, text=_("Hello"))
        self.label.pack()

        self.exit_button = tk.Button(root, text=_("Exit"), command=root.quit)
        self.exit_button.pack()

        self.lang_button = tk.Button(root, text=_("Switch Language"), command=self.switch_language)
        self.lang_button.pack()

        self.current_lang = 'en'

    def switch_language(self):
        if self.current_lang == 'en':
            self.current_lang = 'zh_CN'
        else:
            self.current_lang = 'en'

        gettext.bindtextdomain('messages', 'lang')
        gettext.textdomain('messages')
        _ = gettext.translation('messages', 'lang', languages=[self.current_lang]).gettext

        self.label.config(text=_("Hello"))
        self.exit_button.config(text=_("Exit"))
        self.lang_button.config(text=_("Switch Language"))
        self.root.title(_("Welcome to our application"))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()