from PIL import Image
import os
import rng
import hashlib
import image
from huffman import Huffman
from password import Password
from functions import *

SHA256_BYTES = 32
SHA256_BITS = 256
START = 1
USED_POSITIONS = []


"""
duplicate functions of generate_places, can't add to functions.py yet due to USED_POSITIONS being used
"""


def is_position_available(position):
    return position not in USED_POSITIONS


def mark_position_used(position):
    if position not in USED_POSITIONS:
        USED_POSITIONS.append(position)


def mark_positions_used(positions):
    for pos in positions:
        mark_position_used(pos)


def reset_positions():
    global USED_POSITIONS
    USED_POSITIONS = []


def generate_places(seed, length, imag_ob):
    image_length = (imag_ob.width * imag_ob.height) - 1
    places = []
    rando = rng.DeterministicRNG(seed=seed)
    i = 0
    while i < length:
        num = rando.randint(START, image_length)
        if is_position_available(num) and num != 0:
            places.append(num)
            mark_position_used(num)
            i += 1
    return places


"""
duplicate functions over?
"""


def bin_to_utf_string(bin_str):
    bytes_list = []
    for i in range(0, len(bin_str), 8):
        byte = bin_str[i:i + 8]

        decimal = int(byte, 2)

        bytes_list.append(decimal)

    result = bytes(bytes_list).decode("UTF-8")
    return result


def no_mask_get_message_length(imag_ob, initialization_vector):
    y_max, x_max = divmod(initialization_vector, imag_ob.width)

    with Image.open(imag_ob.path) as img:
        r, g, b, a = img.getpixel((x_max, y_max))

        seed = r * g + b

        places = generate_places(seed, 16, imag_ob)
        bin_list = []
        for i in range(16):
            curr = places[i]
            y, x = divmod(curr, imag_ob.width)
            r, g, b, a = img.getpixel((x, y))

            bin_list.append(r % 2)

        high_bin = ''.join(str(bit) for bit in bin_list[:8])
        low_bin = ''.join(str(bit) for bit in bin_list[8:])

        high_int = int(high_bin, 2)
        low_int = int(low_bin, 2)

        return 256 * high_int + low_int


def get_places(mess_len, imag_ob, initialization_vector):
    y, x = divmod(initialization_vector, imag_ob.width)

    with Image.open(imag_ob.path) as img:
        r, g, b, a = img.getpixel((x, y))
        seed = r * g + b

        places = generate_places(seed, mess_len, imag_ob)

    return places


def no_mask_get_message(places, imag):
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


def binary_string_to_bytes(binary_string):
    if len(binary_string) % 8 != 0:
        raise ValueError("string not a multiple of 8")

    bytes_list = []
    for i in range(0, len(binary_string), 8):
        byte = binary_string[i:i + 8]
        byte_value = int(byte, 2)
        bytes_list.append(byte_value)

    return bytes(bytes_list)


"""
password specific functions
"""


def mask_get_message_length(imag_ob, initialization_vector, mask):
    y_max, x_max = divmod(initialization_vector, imag_ob.width)

    with Image.open(imag_ob.path) as img:
        r, g, b, a = img.getpixel((x_max, y_max))
        seed = r * g + b

        places = generate_places(seed, 16, imag_ob)
        bin_list = []

        for i in range(16):
            i_mask = i*3
            bit_mask = mask[i_mask:i_mask+3]

            curr = places[i]
            y, x = divmod(curr, imag_ob.width)
            r, g, b, a = img.getpixel((x, y))

            if bit_mask == "100" or bit_mask == "011" or bit_mask == "111" or bit_mask == "000":
                bin_list.append(r % 2)
            elif bit_mask == "101" or bit_mask == "010":
                bin_list.append(g % 2)
            else:
                bin_list.append(b % 2)

        high_bin = ''.join(str(bit) for bit in bin_list[:8])
        low_bin = ''.join(str(bit) for bit in bin_list[8:])

        high_int = int(high_bin, 2)
        low_int = int(low_bin, 2)

        return 256 * high_int + low_int


def mask_get_message(places, imag, mask):
    width = imag.width
    message_list = []
    with Image.open(imag.path) as img:
        pixels = img.load()
        for i in range(len(places)):
            i_mask = i * 3
            bit_mask = mask[i_mask:i_mask+3]

            place = places[i]
            y, x = divmod(place, width)
            r, g, b, a = pixels[x, y]

            if bit_mask == "100" or bit_mask == "011" or bit_mask == "111" or bit_mask == "000":
                message_list.append(r % 2)
            elif bit_mask == "101" or bit_mask == "010":
                message_list.append(g % 2)
            else:
                message_list.append(b % 2)

    message = ''.join(str(bit) for bit in message_list)
    return message


def was_password_used():
    try:
        while True:
            iput = input("Was a password used with this image? (y/n): ")
            if iput.lower() == 'y':
                return True
            elif iput.lower() == 'n':
                return False
            else:
                print(f"Please only type 'y for YES, or 'n' for NO, you typed {iput}\ntry again")
    except Exception as e:
        print(f"Failed at was_password_used: {e}")


def main():
    cwd = os.getcwd()

    target_file = get_target_file()
    full_target = os.path.join(cwd, target_file)
    file_ob = image.ImageInfo(full_target)

    huffman = Huffman()

    password_used = was_password_used()
    if password_used:
        string_password = get_password()
        password = Password(string_password, file_ob.width, file_ob.height)
        mark_position_used(password.length_iv)
        mark_position_used(password.message_iv)

        message_length = mask_get_message_length(file_ob, password.length_iv, password.length_mask)
        password.set_message_length(message_length)

        message_places = get_places(message_length, file_ob, password.message_iv)

        # message_binary = no_mask_get_message(message_places, file_ob)
        message_binary = mask_get_message(message_places, file_ob, password.message_mask)
        decoded_message = huffman.decode(message_binary)

        hash_places = generate_places(message_places[0], 256, file_ob)
        # reported_hash = no_mask_get_message(hash_places, file_ob)
        reported_hash = mask_get_message(hash_places, file_ob, password.hash_mask)

        bytes_reported_hash = binary_string_to_bytes(reported_hash)

        real_hash = mask_get_actual_hash(hash_places, file_ob, password.hash_mask)

    else:
        with Image.open(full_target) as img:
            r, g, b, a = img.getpixel((0, 0))
            offset = b
        mark_position_used(0)

        len_iv, mess_iv = get_golden_ratio_pixels_with_offset(file_ob.width, file_ob.height, offset)

        i = 0
        while (len_iv == 0 or mess_iv == 0) or (len_iv == mess_iv):
            len_iv, mess_iv = get_golden_ratio_pixels_with_offset(file_ob.width, file_ob.height, offset + i)
            i += 1

        mark_position_used(len_iv)
        mark_position_used(mess_iv)

        message_length = no_mask_get_message_length(file_ob, len_iv)

        message_places = get_places(message_length, file_ob, mess_iv)

        message_binary = no_mask_get_message(message_places, file_ob)

        decoded_message = huffman.decode(message_binary)

        hash_places = generate_places(message_places[0], 256, file_ob)

        reported_hash = no_mask_get_message(hash_places, file_ob)
        bytes_reported_hash = binary_string_to_bytes(reported_hash)

        real_hash = no_mask_get_actual_hash(hash_places, file_ob)

    print(f"")
    print(f"Reported Hash: {bytes_reported_hash}")
    print(f"Actual Hash:   {real_hash}")
    if bytes_reported_hash == real_hash:
        print("\nreal_hash == reported_hash\nFILE INTEGRITY MAINTAINED")
    else:
        print("HASHES NOT THE SAME, FILE INTEGRITY LOST")
    print(f"\nFound Message: {decoded_message}")






