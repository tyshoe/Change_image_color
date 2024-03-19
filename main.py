import customtkinter as ctk
from tkinter import StringVar, IntVar, DoubleVar
from PIL import Image, ImageTk
from canvas import *
from menu import Menu
from settings import *

# Global variables
image = None
modified_image = None


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # setup
        ctk.set_appearance_mode('dark')
        self.geometry('1000x600')
        self.title('Color Substitution')
        self.minsize(800, 500)
        self.init_parameters()

        # layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=2, uniform='a')
        self.columnconfigure(1, weight=6, uniform='a')

        # canvas
        self.image_width = 0
        self.image_height = 0
        self.canvas_width = 0
        self.canvas_height = 0

        self.menu = Menu(self, self.channels_var, self.r_var, self.g_var, self.b_var, self.a_var, self.manipulate_image, import_image=self.import_image)
        # print(self.alpha_var.get())
        
        # run
        self.mainloop()

    def init_parameters(self):
        self.r_var = IntVar(value=0)
        self.g_var = IntVar(value=0)
        self.b_var = IntVar(value=0)
        self.a_var = DoubleVar(value=0.0)

        self.channels_var = StringVar(value = CHANNELS[0])

    def import_image(self, path):
        self.original = Image.open(path)
        self.image = self.original
        self.image_ratio = self.image.size[0] / self.image.size[1]
        self.image_tk = ImageTk.PhotoImage(self.image)

        self.image_output = ImageOutput(self, self.resize_image)
        self.menu = Menu(self, self.channels_var, self.r_var, self.g_var, self.b_var, self.a_var, self.manipulate_image, import_image=self.import_image, export_image=self.export_image)

    def manipulate_image(self, *args):
        self.image = self.original

        def within_range(pixel, r_range, g_range, b_range):
            r, g, b, _ = pixel
            return r_range[0] <= r <= r_range[1] and g_range[0] <= g <= g_range[1] and b_range[0] <= b <= b_range[1]

        def identify_channels(image):
            if image:
                if image.mode == "RGBA":
                    return True
                elif image.mode == "RGB":
                    return False
        
        if self.image:
            r_min_val, r_max_val = 0, 255 #TODO: set this up
            g_min_val, g_max_val = 0, 255
            b_min_val, b_max_val = 0, 255

            # Function to convert a pixel to a new pixel
            def convert_pixel(pixel):
                nonlocal r_min_val, r_max_val, g_min_val, g_max_val, b_min_val, b_max_val
                # print(r_min_val, r_max_val)
                if within_range(pixel, (r_min_val, r_max_val), (g_min_val, g_max_val), (b_min_val, b_max_val)):
                    # Add the specified values to the R, G, B, and A channels
                    r, g, b, a = pixel
                    r = self.r_var.get()
                    g = self.g_var.get()
                    b = self.b_var.get()
                    a += self.a_var.get()

                    # Limit the values to be in the range of 0 to 255 and 0.0 to 1.0
                    r = max(0, min(255, int(r)))
                    g = max(0, min(255, int(g)))
                    b = max(0, min(255, int(b)))
                    a = max(0, min(255, int(a * 255)))  # Scale float alpha to integer range (0-255)


                    # Check the choice of channel order
                    if self.channels_var.get() == "RGBA":
                        return (r, g, b, a)
                    elif self.channels_var.get() == "RBGA":
                        return (r, b, g, a)
                    elif self.channels_var.get() == "BGRA":
                        return (b, g, r, a)
                    elif self.channels_var.get() == "BRGA":
                        return (b, r, g, a)
                    elif self.channels_var.get() == "GRBA":
                        return (g, r, b, a)
                    elif self.channels_var.get() == "GBRA":
                        return (g, b, r, a)
                return pixel

            # Apply color substitution to the image
            self.image = self.image.convert("RGBA" if identify_channels(self.image) else "RGB")
            self.image.putdata(list(map(convert_pixel, self.image.getdata())))

            # Display the modified image
            # self.image.save(r'C:\Users\tyler.shoemake\Downloads\test.png')

        self.place_image()

    def resize_image(self, event):
        # get canvas ratio
        canvas_ratio = event.width / event.height

        # update canvas attributes
        self.canvas_width = event.width
        self.canvas_height = event.height

        # resize image
        if canvas_ratio > self.image_ratio:  # canvas wider than image
            self.image_height = int(event.height)
            self.image_width = int(self.image_height * self.image_ratio)
        else:  # canvas taller than image
            self.image_width = int(event.width)
            self.image_height = int(self.image_width / self.image_ratio)
        
        self.place_image()
    
    def place_image(self):
        self.image_output.delete('all')
        resized_image = self.image.resize((self.image_width, self.image_height))
        self.image_tk = ImageTk.PhotoImage(resized_image)
        self.image_output.create_image(
            self.canvas_width/2, self.canvas_height/2, image=self.image_tk)

    def export_image(self, name, file, path):
        export_string = f'{path}/{name}.{file}'
        self.image.save(export_string)


app = App()