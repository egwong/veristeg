import os
import image
from PIL import Image
import hashlib


# convert hash bytes to a binary utf-8 string
def bytes_to_binary_string(hash_bytes):
    binary_string = ''
    for byte in hash_bytes:
        binary_byte = format(byte, '08b')
        binary_string += binary_byte
    return binary_string


def get_target_file():
    cwd = os.getcwd()
    while True:
        filename = input("Target PNG File (png only for now please): ")
        full = os.path.join(cwd, filename)
        if os.path.exists(full) and os.path.isfile(full):
            try:
                with Image.open(full) as img:
                    return filename
            except Exception as e:
                print(f"file must be an image (png only for now)\n{e}\n")
        print(f"{filename} not found; try again")
        print("Target file must be in the Current Working Directory, or provide relative path")


def get_actual_hash(hash_places, message_placed_image):
    """
    get the hash found in the actual image
    :param hash_places: a list of places that the hash sits in
    :param message_placed_image: stupid name from copying and pasting
    :return: sha256 hash in byte form
    """
    height = message_placed_image.height
    width = message_placed_image.width

    with Image.open(message_placed_image.path) as img:
        hash_img = img.copy()
        pixels = hash_img.load()

        for i in range(len(hash_places)):
            place = hash_places[i]
            y, x = divmod(place, width)
            r, g, b, a = pixels[x, y]
            pixels[x, y] = (0, g, b, a)

        pixel_data = hash_img.convert('RGBA').tobytes()
        hash_value = hashlib.sha256(pixel_data).digest()

    return hash_value


def is_valid_utf8(bytes_to_check):
    try:
        bytes_to_check.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False




