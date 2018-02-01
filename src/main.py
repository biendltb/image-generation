from Tkinter import *

import WnidRetrieval

IMAGE_SOURCES = [
    "ImageNet",
    "COCO"
]

# creating class Window inheriting from Frame class
class Window(Frame):

    def __init__(self, master=None):
        # parameters that send through Frame class
        Frame.__init__(self, master)

        # reference to master widget, which is the TK window
        self.master = master

        self.init_window()


    def init_window(self):

        # changing the title of the master widget
        self.master.title("-")

        # creating menu
        # set default value
        variable = StringVar(self.master)
        variable.set(IMAGE_SOURCES[0])

        self.img_source = IMAGE_SOURCES[0]

        self.source_list = OptionMenu(self.master, variable, *IMAGE_SOURCES,
                                      command=self.change_source_list)
        self.source_list.pack()

        # allowing widget to take the full space of the root
        self.pack(fill=BOTH, expand=1)

        Label(self, text="Query:").grid(row=0)

        # creating an entry
        self.query_entry = Entry(self)

        # creating a button instance
        show_btn = Button(self, text="Show", command=self.query_btn_click)

        # placing widgets
        self.query_entry.grid(row=0, column=1)
        show_btn.grid(row=1, column = 1)

    def change_source_list(self, value):
        self.img_source = value

    def query_btn_click(self):
        query = str(self.query_entry.get()).lower().strip()
        wnid_list = WnidRetrieval.getWnid(query)
        for id in wnid_list:
            print(id)

root = Tk()

# set size of window
root.geometry("250x100")

app = Window(root)

root.mainloop()