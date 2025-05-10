import os
import hashlib
from PIL import Image


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


def no_mask_get_actual_hash(hash_places, message_placed_image):
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


def is_valid_utf8(text_to_check):
    if isinstance(text_to_check, str):
        try:
            text_to_check.encode('utf-8').decode('utf-8')
            return True
        except UnicodeError:
            return False
    elif isinstance(text_to_check, bytes):
        try:
            text_to_check.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
    return False


def get_golden_ratio_pixels_with_offset(width, height, offset=0):
    # phi (simplified)
    phi = 1.618033988749895

    x1_with_offset = width / phi + offset
    y1_with_offset = height / phi + offset

    x2_with_offset = width * (1 - 1 / phi) + offset
    y2_with_offset = height * (1 - 1 / phi) + offset

    _, y1 = divmod(int(y1_with_offset), height)
    _, x1 = divmod(int(x1_with_offset), width)

    _, y2 = divmod(int(y2_with_offset), height)
    _, x2 = divmod(int(x2_with_offset), width)

    index1 = y1 * width + x1
    index2 = y2 * width + x2

    return index1, index2


def get_password():
    try:
        while True:
            i = input("Please provide the password (all UTF-8 allowed, length limit of 100 chars):\n")
            if i and 100 > len(i) > 0 and is_valid_utf8(i):
                good = input(f"Your password is [{i}], good? (y/n): ")
                if good.lower() == 'y':
                    return i
                elif good.lower() == 'n':
                    print("then try again")
                else:
                    print("only 'y' and 'n' please, try again")
            else:
                print("Password not good, password must satisfy: 100 > len(password) > 0 "
                      "and is_valid_utf8(password), try again")

    except Exception as e:
        print(f"Failed at get_password: {e}")


def mask_get_actual_hash(hash_places, message_placed_image, mask):
    height = message_placed_image.height
    width = message_placed_image.width

    with Image.open(message_placed_image.path) as img:
        hash_img = img.copy()
        pixels = hash_img.load()

        for i in range(len(hash_places)):
            i_mask = i * 3
            bit_mask = mask[i_mask:i_mask + 3]

            place = hash_places[i]
            y, x = divmod(place, width)
            r, g, b, a = pixels[x, y]
            if bit_mask == "100" or bit_mask == "011" or bit_mask == "111" or bit_mask == "000":
                pixels[x, y] = (0, g, b, a)
            elif bit_mask == "101" or bit_mask == "010":
                pixels[x, y] = (r, 0, b, a)
            else:
                pixels[x, y] = (r, g, 0, a)

        pixel_data = hash_img.convert('RGBA').tobytes()
        hash_value = hashlib.sha256(pixel_data).digest()

    return hash_value

