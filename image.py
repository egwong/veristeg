from PIL import Image
import os


class ImageInfo:
    def __init__(self, path):
        self.path = path
        self.ext = self.get_ext()
        self.format = None
        self.width = None
        self.height = None
        self.mode = None
        self.get_width_height_format_mode()

    def get_ext(self):
        try:
            return os.path.splitext(self.path)[1]
        except Exception as err:
            print(f"Error: {err} in {self.path}.get_ext")
            return None

    def get_width_height_format_mode(self):
        try:
            with Image.open(self.path) as img:
                w, h = img.size
                self.width = w
                self.height = h
                self.format = img.format
                self.mode = img.mode
        except Exception as err:
            print(f"Error: {err} in {self.path}.get_width_height_format_mode")
            return None