# Import the required libraries
from tkinter import *
from pystray import MenuItem as item
from pystray import Icon
from PIL import Image, ImageGrab
from pynput.mouse import Listener
from pynput.keyboard import GlobalHotKeys
from pytesseract import pytesseract
import pyperclip
import time
import os
import threading


class App:
    def __init__(self, root):
        self.root = root
        self.hide_window()
        ix = None
        iy = None

    # Define a function for quit the window
    def quit_window(self, icon, item):
        self.icon.stop()
        os._exit(1)

    # Hide the window and show on the system taskbar
    def hide_window(self):
        self.root.withdraw()
        image = Image.open("favicon.ico")

        menu = (item("Çıkış", self.quit_window),)
        self.icon = Icon(
            "image2text",
            image,
            "Ekran görüntüsünü metine çevirme",
            menu,
        )
        self.icon.notify(
            "CTRL + ALT + Z ile ekran görüntüsünü metine çevirebilirsiniz."
        )

        # Run the icon mainloop in a separate thread
        self.thread = threading.Thread(target=self.icon.run)
        self.thread.start()

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
                img.save("screenshot_area.jpg")  # Save the screenshot

        if not pressed:
            # Stop listener
            return False

    def img_to_text_pytesseract(self):
        # Defining paths to tesseract.exe
        # and the image we would be using
        path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        image_path = r"screenshot_area.jpg"

        # Providing the tesseract executable
        # location to pytesseract library
        pytesseract.tesseract_cmd = path_to_tesseract

        # Passing the image object to image_to_string() function
        # This function will extract the text from the image
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang="tur")
        pyperclip.copy(text)
        # Displaying the extracted text
        print(text[:])


class CopyPaste:
    def on_activate_copy():
        print("<CTRL> + C pressed!")

        time.sleep(0.01)
        all_text = pyperclip.paste()

        for number in all_text[:11:2]:
            if number.isnumeric():
                tc = "".join(i for i in all_text if i.isnumeric())
                pyperclip.copy(tc)
        try:
            print(all_text)
            print(tc)
        except:
            pass


if __name__ == "__main__":
    root = Tk()
    app = App(root)

    """ I replace self._state.remove(key) with 'self._state.clear()' in
     __init__ file at the line of 190. Because it is very hard to release
     3 pressed button at the same time. """
    global_keys = GlobalHotKeys(
        {
            "<ctrl>+<alt>+z": app.screen_parse,
            "<ctrl>+c": CopyPaste.on_activate_copy,
        }
    )

    global_keys.start()
    root.mainloop()
