import tkinter as tk
from tkinter import Toplevel, Listbox
class RoundedButton(tk.Canvas):
    def __init__(self, master=None, text:str="", font=("Times", 14), radius=25, btnforeground="#000000", btnbackground="#ffffff", clicked=None, *args, **kwargs):
        super(RoundedButton, self).__init__(master, *args, **kwargs)
        self.config(bg=self.master["bg"], highlightthickness=0)  # Remove the highlight border
        self.btnbackground = btnbackground
        self.clicked = clicked

        self.radius = radius        
        self.text = self.create_text(0, 0, text=text, tags="button", fill=btnforeground, font=font, justify="center")
        self.rect = self.round_rectangle(0, 0, 0, 0, tags="button", radius=radius, fill=btnbackground)

        self.tag_bind("button", "<ButtonPress>", self.border)
        self.tag_bind("button", "<ButtonRelease>", self.border)
        self.bind("<Configure>", self.resize)

        text_rect = self.bbox(self.text)
        if int(self["width"]) < text_rect[2]-text_rect[0]:
            self["width"] = (text_rect[2]-text_rect[0]) + 10

        if int(self["height"]) < text_rect[3]-text_rect[1]:
            self["height"] = (text_rect[3]-text_rect[1]) + 10

    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def resize(self, event):
        text_bbox = self.bbox(self.text)

        if self.radius > event.width or self.radius > event.height:
            radius = min((event.width, event.height))
        else:
            radius = self.radius

        bg = self.itemcget(self.rect, "fill")

        width, height = event.width, event.height

        if event.width < text_bbox[2]-text_bbox[0]:
            width = text_bbox[2]-text_bbox[0] + 30

        if event.height < text_bbox[3]-text_bbox[1]:  
            height = text_bbox[3]-text_bbox[1] + 30

        self.delete(self.rect)
        self.rect = self.round_rectangle(0, 0, width, height, radius=radius, fill=bg, tags="button")

        bbox = self.bbox(self.rect)

        x = ((bbox[2]-bbox[0])/2) - ((text_bbox[2]-text_bbox[0])/2)
        y = ((bbox[3]-bbox[1])/2) - ((text_bbox[3]-text_bbox[1])/2)

        self.moveto(self.text, x, y)
        self.tag_raise(self.text)

    def border(self, event):
        if event.type == "4":
            self.itemconfig(self.rect, fill="#C5E99B")
            if self.clicked is not None:
                self.clicked()
        else:
            self.itemconfig(self.rect, fill=self.btnbackground)
class RoundedDropdown(tk.Canvas):
    def __init__(self, master=None, options=[],text = "", font=("Times", 14), radius=25, btnforeground="#000000", btnbackground="#ffffff", selected=None, *args, **kwargs):
        super(RoundedDropdown, self).__init__(master, *args, **kwargs)
        self.config(bg=self.master["bg"], highlightthickness=0)
        self.btnbackground = btnbackground
        self.selected = selected
        self.options = options

        self.radius = radius
        self.text = self.create_text(0, 0, text=text, tags="dropdown", fill=btnforeground, font=font, justify="center")
        self.rect = self.round_rectangle(0, 0, 0, 0, tags="dropdown", radius=radius, fill=btnbackground)

        self.tag_bind("dropdown", "<ButtonPress>", self.show_options)
        self.bind("<Configure>", self.resize)

        text_rect = self.bbox(self.text)
        if int(self["width"]) < text_rect[2] - text_rect[0]:
            self["width"] = (text_rect[2] - text_rect[0]) + 10

        if int(self["height"]) < text_rect[3] - text_rect[1]:
            self["height"] = (text_rect[3] - text_rect[1]) + 10

    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def resize(self, event):
        text_bbox = self.bbox(self.text)

        if self.radius > event.width or self.radius > event.height:
            radius = min((event.width, event.height))
        else:
            radius = self.radius

        bg = self.itemcget(self.rect, "fill")

        width, height = event.width, event.height

        if event.width < text_bbox[2] - text_bbox[0]:
            width = text_bbox[2] - text_bbox[0] + 30

        if event.height < text_bbox[3] - text_bbox[1]:
            height = text_bbox[3] - text_bbox[1] + 30

        self.delete(self.rect)
        self.rect = self.round_rectangle(0, 0, width, height, radius=radius, fill=bg, tags="dropdown")

        bbox = self.bbox(self.rect)

        x = ((bbox[2] - bbox[0]) / 2) - ((text_bbox[2] - text_bbox[0]) / 2)
        y = ((bbox[3] - bbox[1]) / 2) - ((text_bbox[3] - text_bbox[1]) / 2)

        self.moveto(self.text, x, y)
        self.tag_raise(self.text)

    def show_options(self, event):
        self.options_win = Toplevel(self)
        self.options_win.overrideredirect(True)
        self.options_win.geometry(f"{self.winfo_width()}x{len(self.options)*20}+{self.winfo_rootx()}+{self.winfo_rooty()+self.winfo_height()}")
        self.options_win.bind("<FocusOut>", lambda e: self.options_win.destroy())

        lb = Listbox(self.options_win, selectmode="single")
        lb.pack(fill="both", expand=True)

        for option in self.options:
            lb.insert("end", option)

        lb.bind("<<ListboxSelect>>", self.on_select)

    def on_select(self, event):
        lb = event.widget
        index = int(lb.curselection()[0])
        selected_option = lb.get(index)
        self.itemconfig(self.text, text=selected_option)
        if self.selected:
            self.selected(selected_option)
        self.options_win.destroy()
if __name__ == "__main__":
    def func():
        print("Button clicked")
    def func_selected(option = None):
        print(f"Selected {option}")
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.configure(bg="#519D9E")
    root.rowconfigure((0, 1, 2), weight=1)
    
    RoundedButton(text="Button1", radius=45, btnbackground="#029510", btnforeground="#ffffff", clicked=func, width=250, height=50).pack(side="left")
    RoundedButton(text="Button2", radius=45, btnbackground="#ea4335", btnforeground="#ffffff", clicked=func, width=250, height=50).pack(side="left")
    RoundedButton(text="Button3", radius=45, btnbackground="#0078ff", btnforeground="#ffffff", clicked=func, width=250, height=50).pack(side="left")
    options = ["Option1", "Option2", "Option3"]

    RoundedDropdown(options=options, radius=25, btnbackground="#029510", btnforeground="#ffffff", selected=func_selected, width=150, height=50).pack(pady=10)
    RoundedDropdown(options=options, radius=25, btnbackground="#ea4335", btnforeground="#ffffff", selected=func(), width=150, height=50).pack(pady=10)
    RoundedDropdown(options=options, radius=25, btnbackground="#0078ff", btnforeground="#ffffff", selected=func(), width=150, height=50).pack(pady=10)
    root.mainloop()
