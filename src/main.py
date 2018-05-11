from Tkinter import *
from urllib2 import urlopen
from urllib2 import HTTPError
from io import BytesIO

# Tkinter only displays GIF, PNG images
import time
from PIL import Image, ImageTk

import ImageNetRetrieval
from COCORetrieval import COCORetrievalJSON, COCORetrievalSQLite

IMAGE_SOURCES = [
    "ImageNet",
    "COCO"
]

IMAGE_DATASET_PATH = "../data/val2014/"

# creating class Window inheriting from Frame class
class Window(Frame):

    NUM_DISPLAYED_IMG = 5
    # screen height to display image
    SCREEN_HEIGHT = 768

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

    # update image source when user changes the image source in the drop down list
    def change_source_list(self, value):
        self.img_source = value

    def query_btn_click(self):

        print("Searching for images...")

        query = str(self.query_entry.get()).lower().strip()

        # measure time
        start_time = time.time()

        # coco_retrieval = COCORetrievalJSON()
        # im_name_list = coco_retrieval.get_im_file_list(query)

        # get top 10 images
        coco_retrieval = COCORetrievalSQLite()
        im_name_list = coco_retrieval.query(query, 10)

        print('Execution time: %r' % (time.time() - start_time))

        ims = []
        for im_name in im_name_list:
            im_path = IMAGE_DATASET_PATH + im_name
            ims.append(self.load_image_from_file(im_path))

        #self.show_multi_images(ims)
        self.show_single_image(ims)

        # url_list = ImageNetRetrieval.getUrlFromQuery(query)
        #
        # for url in url_list:
        #     print(url)
        #     # skip dead urls until reaching an available image
        #     if (self.show_image_from_url(url)):
        #         break

    def load_image_from_url(self, img_url):

        # read and decode the image
        # if image url is not available, return False
        try:
            raw_img = urlopen(img_url).read()
        except HTTPError:
            return False

        # catch image format error
        try:
            im = Image.open(BytesIO(raw_img))
        except:
            return False

        #img = ImageTk.PhotoImage(im)
        #print("image size:", img.width(), img.height())

        return im

    def load_image_from_file(self, path):
        return Image.open(path)

    def show_multi_images(self, ims):
        # initializing a child window
        img_window = Toplevel()
        img_window.title("Retrieved image")

        num_im = self.NUM_DISPLAYED_IMG

        if len(ims) < self.NUM_DISPLAYED_IMG:
            num_im = len(ims)

        for i in range(0, num_im):

            resized_im = ims[i].resize((self.SCREEN_HEIGHT/(num_im/1), self.SCREEN_HEIGHT/(num_im/1)), Image.ANTIALIAS)

            img = ImageTk.PhotoImage(resized_im)
            # put image inside a label to display
            img_lb = Label(img_window, image=img)
            # !important: set reference for image
            img_lb.image = img
            img_lb.grid(row=i/5, column = i%5)
            #img_lb.pack()

    def show_single_image(self, ims):
        # initializing a child window
        img_window = Toplevel()
        img_window.title("Retrieved image")

        img = ImageTk.PhotoImage(ims[0])

        # put image inside a label to display
        img_lb = Label(img_window, image=img)

        # !important: set reference for image
        img_lb.image = img
        img_lb.grid(row=0, column=0)

root = Tk()

# set size of window
root.geometry("250x100")

app = Window(root)

root.mainloop()