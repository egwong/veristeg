from PIL import Image
import os
import rng
import hashlib
import image
from huffman import Huffman

SHA256_BYTES = 32
SHA256_BITS = 256
START = 17


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


# used for hash-decoding from utf-8
def bin_to_utf_string(bin_str):
    bytes_list = []
    for i in range(0, len(bin_str), 8):
        byte = bin_str[i:i + 8]

        decimal = int(byte, 2)

        bytes_list.append(decimal)

    result = bytes(bytes_list).decode("UTF-8")
    return result


def get_message_length(imag):
    with Image.open(imag.path) as img:
        bin_list = []
        for i in range(1,17):
            r, g, b, a = img.getpixel((i, 0))
            bin_list.append(r % 2)
        high_bin = ''.join(str(bit) for bit in bin_list[:8])
        low_bin = ''.join(str(bit) for bit in bin_list[8:])

        high_int = int(high_bin, 2)
        low_int = int(low_bin, 2)

        return 256 * high_int + low_int


def get_places(mess_len, imag):
    height = imag.height
    width = imag.width
    image_length = width * height
    places = []
    # pixel_0 = seed
    # pixel_1-16 = length
    # start = 17
    with Image.open(imag.path) as img:
        r, g, b, a = img.getpixel((0, 0))
        seed = r * g + b

        rando = rng.DeterministicRNG(seed=seed)

        i = 0
        while i < mess_len:
            num = rando.randint(START, image_length)
            if num not in places:
                places.append(num)
                i += 1
    return places


def calculate_hash_places(mess_places, imag):
    image_length = imag.width * imag.height
    hash_places = []
    seed = mess_places[0]
    rando = rng.DeterministicRNG(seed=seed)
    i = 0
    while i < SHA256_BITS:
        num = rando.randint(START, image_length)
        if num not in mess_places:
            hash_places.append(num)
            i += 1
    return hash_places


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


def get_message(places, imag):
    """
    :param places: a list of places to get values
    :param imag: the image
    :return: a string of binary collected from places
    """
    # get the length, width of the image
    height = imag.height
    width = imag.width
    message_list = []
    with Image.open(imag.path) as img:
        pixels = img.load()
        for i in range(len(places)):
            place = places[i]
            y, x = divmod(place, width)
            r, g, b, a = pixels[x, y]

            message_list.append(r % 2)

    message = ''.join(str(bit) for bit in message_list)
    return message


def bytes_to_binary_string(hash_bytes):
    binary_string = ''
    for byte in hash_bytes:
        binary_byte = format(byte, '08b')
        binary_string += binary_byte
    return binary_string


def binary_string_to_bytes(binary_string):
    if len(binary_string) % 8 != 0:
        raise ValueError("string not a multiple of 8")

    bytes_list = []
    for i in range(0, len(binary_string), 8):
        byte = binary_string[i:i + 8]
        byte_value = int(byte, 2)
        bytes_list.append(byte_value)

    return bytes(bytes_list)


def main():
    cwd = os.getcwd()

    target_file = get_target_file()
    full_target = os.path.join(cwd, target_file)
    file_ob = image.ImageInfo(full_target)

    huffman = Huffman()

    message_length = get_message_length(file_ob)

    message_places = get_places(message_length, file_ob)

    message_binary = get_message(message_places, file_ob)

    decoded_message = huffman.decode(message_binary)

    hash_places = calculate_hash_places(message_places, file_ob)

    reported_hash = get_message(hash_places, file_ob)
    bytes_reported_hash = binary_string_to_bytes(reported_hash)

    real_hash = get_actual_hash(hash_places, file_ob)
    print(f"")
    print(f"Reported Hash: {bytes_reported_hash}")
    print(f"Actual Hash:   {real_hash}")
    if bytes_reported_hash == real_hash:
        print("\nholy shit it worked, real_hash == reported_hash")
    else:
        print("hashes not the same, corrupted file")
    print(f"\nFound Message: {decoded_message}")






