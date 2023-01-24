# Import the required libraries
from tkinter import *
import pystray
from pystray import MenuItem as item
from pystray import Icon
from PIL import Image, ImageGrab, ImageEnhance, ImageOps
from pynput.mouse import Listener
from pynput.keyboard import GlobalHotKeys
from pytesseract import pytesseract
import pyperclip
import time
import os
import threading
import plyer


class App:
    def __init__(self, root):
        self.root = root
        self.hide_window()

        # At first default language is English.
        self.state_eng = True
        self.state_chi_sim = False
        self.state_hin = False
        self.state_spa = False
        self.state_fra = False
        self.state_ara = False
        self.state_rus = False
        self.state_tur = False

    def language_clear(self):
        self.state_eng = False
        self.state_chi_sim = False
        self.state_hin = False
        self.state_spa = False
        self.state_fra = False
        self.state_ara = False
        self.state_rus = False
        self.state_tur = False

    def activate_eng(self, icon, item):
        self.language_clear()
        self.state_eng = not item.checked
        print(self.state_eng)

    def activate_chi_sim(self, icon, item):
        self.language_clear()
        self.state_chi_sim = not item.checked

    def activate_hin(self, icon, item):
        self.language_clear()
        self.state_hin = not item.checked

    def activate_spa(self, icon, item):
        self.language_clear()
        self.state_spa = not item.checked

    def activate_fra(self, icon, item):
        self.language_clear()
        self.state_fra = not item.checked

    def activate_ara(self, icon, item):
        self.language_clear()
        self.state_ara = not item.checked

    def activate_rus(self, icon, item):
        self.language_clear()
        self.state_rus = not item.checked

    def activate_tur(self, icon, item):
        self.language_clear()
        self.state_tur = not item.checked
        print(self.state_tur)

    # Define a function for quit the window
    def quit_window(self, icon, item):
        self.icon.stop()
        os._exit(1)

    # Hide the window and show on the system taskbar
    def hide_window(self):
        self.root.withdraw()
        image = Image.open("favicon.ico")

        menu = pystray.Menu(
            item(
                "Languages",
                pystray.Menu(
                    item(
                        "English",
                        self.activate_eng,
                        checked=lambda item: self.state_eng,
                    ),
                    item(
                        "Chinese",
                        self.activate_chi_sim,
                        checked=lambda item: self.state_chi_sim,
                    ),
                    item(
                        "Hindi",
                        self.activate_hin,
                        checked=lambda item: self.state_hin,
                    ),
                    item(
                        "Spanish",
                        self.activate_spa,
                        checked=lambda item: self.state_spa,
                    ),
                    item(
                        "French",
                        self.activate_fra,
                        checked=lambda item: self.state_fra,
                    ),
                    item(
                        "Arabic",
                        self.activate_ara,
                        checked=lambda item: self.state_ara,
                    ),
                    item(
                        "Russian",
                        self.activate_rus,
                        checked=lambda item: self.state_rus,
                    ),
                    item(
                        "Turkish",
                        self.activate_tur,
                        checked=lambda item: self.state_tur,
                    ),
                ),
            ),
            item("Quit", self.quit_window),
        )

        self.icon = Icon(
            "image2text",
            image,
            "Easy Capture Image to Text",
            menu,
        )

        # Run the icon mainloop in a separate thread
        self.thread = threading.Thread(target=self.icon.run)
        self.thread.start()

        plyer.notification.notify(
            app_name="Easy Capture Image to Text",
            title="Easy Capture Image to Text",
            message="Press CTRL + ALT + Z togather, select area and It is already copied. Now you can Paste the text.",
            app_icon="favicon.ico",
            timeout=10,
        )

    def screen_parse(self):

        self.root.deiconify()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # making the canvas and making it recognise movements of the mouse
        print(screen_width, screen_height)

        root_geometry = (
            str(screen_width) + "x" + str(screen_height) + "+0" + "+0"
        )  # Creates a geometric string argument

        self.root.geometry(root_geometry)  # Sets the geometry string value
        print(root_geometry)

        self.root.wm_attributes("-alpha", 0.2)

        self.root.overrideredirect(True)
        # root.wait_visibility(root)

        self.canvas = Canvas(
            self.root, width=screen_width, height=screen_width
        )  # Crate canvas

        self.canvas.config(cursor="cross")  # Change mouse pointer to cross
        self.canvas.pack()

        # Collect events until released
        with Listener(on_move=App.on_move, on_click=App.on_click) as listener:
            self.canvas.bind("<ButtonPress-1>", self.onmouse)
            self.canvas.bind("<B1-Motion>", self.paint)  # drawing  line

            listener.join()
            self.canvas.destroy()  # destroy canvas

            self.root.withdraw()
            self.img_to_text_pytesseract()

    def onmouse(self, event):
        self.old_x = []
        self.old_y = []
        self.old_x.append(event.x)
        self.old_y.append(event.y)

    def paint(self, e):
        """creates a canvas where you can paint"""
        self.canvas.create_rectangle(
            self.old_x,
            self.old_y,
            e.x,
            e.y,
            fill="black",
            width=8,
            outline="white",
        )

    def on_move(x, y):
        print("Pointer moved to {0}".format((x, y)))
        return x, y

    # Start and End mouse position
    def on_click(x, y, button, pressed):
        global ix, iy

        if button == button.left:

            # Left button pressed then continue
            if pressed:
                ix = x
                iy = y
                print("left button pressed at {0}".format((x, y)))
                print(x, y)

            else:
                print("left button released at {0}".format((x, y)))
                root.wm_attributes("-alpha", 0)
                # Fixed to minus ix,iy coordinates
                if ix == x or iy == y:
                    ix, iy, x, y = 1, 2, 3, 4
                    print("Same x or y coordinates can not create an area!")
                elif ix > x and iy > y:
                    lx, ly = ix, iy
                    ix, iy = x, y
                    x, y = lx, ly
                elif ix > x:
                    lx = ix
                    ix = x
                    x = lx
                elif iy > y:
                    ly = iy
                    iy = y
                    y = ly

                bbox = (ix, iy, x, y)
                img = ImageGrab.grab(bbox)  # Take the screenshot
                grayscale = ImageOps.grayscale(img)
                # inverted = ImageOps.invert(grayscale.convert('RGB'))
                enhancer = ImageEnhance.Contrast(grayscale)
                factor = 1.6  # increase contrast
                grayscale = enhancer.enhance(factor)
                grayscale.save(
                    "screenshot_area.png", "PNG", dpi=(400.0, 400.0)
                )  # Save the screenshot

        if not pressed:
            # Stop listener
            return False

    def img_to_text_pytesseract(self):
        # Defining paths to tesseract.exe
        # and the image we would be using
        path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        image_path = r"screenshot_area.png"

        # Providing the tesseract executable
        # location to pytesseract library
        pytesseract.tesseract_cmd = path_to_tesseract

        # Passing the image object to image_to_string() function
        # This function will extract the text from the image
        img = Image.open(image_path)
        if self.state_eng == True:
            text = pytesseract.image_to_string(img, lang="eng", config="--psm 10")
        elif self.state_chi_sim == True:
            text = pytesseract.image_to_string(img, lang="chi_sim", config="--psm 10")
        elif self.state_hin == True:
            text = pytesseract.image_to_string(img, lang="hin", config="--psm 10")
        elif self.state_spa == True:
            text = pytesseract.image_to_string(img, lang="spa", config="--psm 10")
        elif self.state_fra == True:
            text = pytesseract.image_to_string(img, lang="fra", config="--psm 10")
        elif self.state_ara == True:
            text = pytesseract.image_to_string(img, lang="ara", config="--psm 10")
        elif self.state_rus == True:
            text = pytesseract.image_to_string(img, lang="rus", config="--psm 10")
        elif self.state_tur == True:
            text = pytesseract.image_to_string(img, lang="tur", config="--psm 10")

        pyperclip.copy(text)
        # Displaying the extracted text
        print(text[:])


if __name__ == "__main__":
    root = Tk()
    app = App(root)

    """ I replace self._state.remove(key) with 'self._state.clear()' in
     __init__ file at the line of 190 and 183. Because it is very hard to release
     3 pressed button at the same time. """
    global_keys = GlobalHotKeys({"<ctrl>+<alt>+z": app.screen_parse})

    global_keys.start()
    root.mainloop()
