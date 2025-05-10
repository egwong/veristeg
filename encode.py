import image
from PIL import Image
from huffman import Huffman
import os
import re
import rng
import hashlib
from functions import *
from password import Password

SHA256_BYTES = 32
SHA256_BITS = 256
START = 1
USED_POSITIONS = []


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


def validate_input(text):
    pattern = r'[a-zA-Z0-9 ]+'
    return bool(re.fullmatch(pattern, text))


def get_input():
    while True:
        iput = input("Please enter the desired message (only lowercase letters (converted if existing),"
                     " numbers, and spaces allowed):\n")
        if validate_input(iput):
            good = input(f"Your message is [{iput}]\nGood? (y/n): ")
            if good.lower() == 'y':
                return iput
            else:
                print('then try again bud')
                continue
        else:
            print('input not valid try again')


def generate_message_places(mess, imag_ob, initialization_vector):
    places = []
    y, x = divmod(initialization_vector, imag_ob.width)

    with Image.open(imag_ob.path) as img:
        r, g, b, a = img.getpixel((x, y))
        seed = r * g + b

        places = generate_places(seed, len(mess), imag_ob)
    return places


def no_mask_place_length(mess, imag_ob, working_path, initialization_vector):
    high, low = divmod(len(mess), 256)

    high_bits = format(high, '08b')
    low_bits = format(low, '08b')

    combined = high_bits + low_bits

    # image_length = (imag_ob.width * imag_ob.height) - 1
    # mark_position_used(image_length)

    y, x = divmod(initialization_vector, imag_ob.width)

    with Image.open(working_path) as img:
        img = img.convert('RGBA')
        r, g, b, a = img.getpixel((x, y))
        seed = r * g + b
        places = generate_places(seed, len(combined), imag_ob)

    no_mask_place_bits(places, combined, imag_ob, working_path)


# put that shit into the image
def no_mask_place_bits(places, binary_data, imag, working_path):
    try:
        width = imag.width

        with Image.open(working_path) as img:
            pixels = img.load()
            for i in range(len(places)):
                place = places[i]
                bit = int(binary_data[i])
                y, x = divmod(place, width)
                r, g, b, a = pixels[x, y]
                new_r = (r & 0xFE) | bit
                pixels[x, y] = (new_r, g, b, a)
            img.save(working_path)
    except Exception as e:
        print(f"failed in no_mask_place_bits: {e}")


def create_final_output(working_path, original_filename):
    cwd = os.getcwd()
    base_filename = os.path.basename(original_filename)
    final_name = 'modified_' + base_filename
    final_path = os.path.join(cwd, final_name)

    try:
        os.rename(working_path, final_path)
    except Exception as e:
        with Image.open(working_path) as img:
            img.save(final_path)
        os.remove(working_path)
        print(e)

    return final_path


def determine_password_use():
    try:
        while True:
            i = input("Would you like to encode you message with password protection (recommended)? (y/n): ")
            if i.lower() == 'y':
                return True
            elif i.lower() == 'n':
                return False
            else:
                print("Please only type 'y' or 'n'")
    except Exception as e:
        print("Failed to determine_password_use")
        print(e)


def create_modified_copy(original_path):
    cwd = os.getcwd()
    base_filename = os.path.basename(original_path)
    working_name = 'temp_working_' + base_filename
    working_path = os.path.join(cwd, working_name)
    with Image.open(original_path) as img:
        img = img.convert('RGBA')
        img.save(working_path)
    return working_path


"""
password functions
"""


def mask_place_length(mess, imag_ob, working_path, initialization_vector, length_mask):
    high, low = divmod(len(mess), 256)

    high_bits = format(high, '08b')
    low_bits = format(low, '08b')

    combined = high_bits + low_bits

    y, x = divmod(initialization_vector, imag_ob.width)

    with Image.open(working_path) as img:
        img = img.convert('RGBA')
        r, g, b, a = img.getpixel((x, y))
        seed = r * g + b
        places = generate_places(seed, len(combined), imag_ob)

    mask_place_bits(places, combined, imag_ob, working_path, length_mask)


def mask_place_bits(places, binary_data, imag, working_path, mask):
    try:
        width = imag.width

        with Image.open(working_path) as img:
            pixels = img.load()
            for i in range(len(places)):
                i_mask = i*3
                bit_mask = mask[i_mask:i_mask+3]

                place = places[i]
                bit = int(binary_data[i])
                y, x = divmod(place, width)
                r, g, b, a = pixels[x, y]

                if bit_mask == "100" or bit_mask == "011" or bit_mask == "111" or bit_mask == "000":
                    new_r = (r & 0xFE) | bit
                    pixels[x, y] = (new_r, g, b, a)
                elif bit_mask == "101" or bit_mask == "010":
                    new_g = (g & 0xFE) | bit
                    pixels[x, y] = (r, new_g, b, a)
                else:
                    new_b = (b & 0xFE) | bit
                    pixels[x, y] = (r, g, new_b, a)

            img.save(working_path)
    except Exception as e:
        print(f"failed in mask_place_bits: {e}")


def main():
    reset_positions()

    cwd = os.getcwd()
    target_file = get_target_file()
    full_target = os.path.join(cwd, target_file)
    file_ob = image.ImageInfo(full_target)

    message = get_input().upper()
    huffman = Huffman()
    bin_message = huffman.encode(message)

    password_use = determine_password_use()

    # the modified copy
    working_path = create_modified_copy(full_target)
    working_image = image.ImageInfo(working_path)

    # print("after creating working image")

    if password_use:
        string_password = get_password()

        password = Password(string_password, working_image.width, working_image.height)
        password.set_message_length(len(bin_message))
        mark_position_used(password.length_iv)
        mark_position_used(password.message_iv)

        mask_place_length(bin_message, working_image, working_path, password.length_iv, password.length_mask)

        mess_places = generate_message_places(bin_message, file_ob, password.message_iv)
        assert len(mess_places) == len(bin_message)
        mask_place_bits(mess_places, bin_message, working_image, working_path, password.message_mask)

        hash_places = generate_places(mess_places[0], 256, working_image)
        byte_hash = mask_get_actual_hash(hash_places, working_image, password.hash_mask)
        binary_hash = bytes_to_binary_string(byte_hash)

        mask_place_bits(hash_places, binary_hash, working_image, working_path, password.hash_mask)

    else:
        with Image.open(working_path) as img:
            r, g, b, a = img.getpixel((0, 0))
            offset = b
        mark_position_used(0)

        len_iv, mess_iv = get_golden_ratio_pixels_with_offset(working_image.width, working_image.height, offset)

        i = 0
        while (len_iv == 0 or mess_iv == 0) or (len_iv == mess_iv):
            len_iv, mess_iv = get_golden_ratio_pixels_with_offset(file_ob.width, file_ob.height, offset + i)
            i += 1

        mark_position_used(len_iv)
        mark_position_used(mess_iv)

        no_mask_place_length(bin_message, working_image, working_path, len_iv)
        mess_places = generate_message_places(bin_message, working_image, mess_iv)
        assert len(mess_places) == len(bin_message)
        no_mask_place_bits(mess_places, bin_message, working_image, working_path)

        hash_places = generate_places(mess_places[0], 256, working_image)
        byte_hash = no_mask_get_actual_hash(hash_places, working_image)
        binary_hash = bytes_to_binary_string(byte_hash)

        no_mask_place_bits(hash_places, binary_hash, working_image, working_path)

    final_output = create_final_output(working_path, target_file)

    print(f"")
    print(f"Original Message Size: {len(message)*8} assuming UTF-8")
    print(f"Huffman Message Size:  {len(bin_message)}")
    print(f"Compression Rate: {(len(message)*8)/len(bin_message)}")
    print(f"")

    print(f"Calculated Hash (bytes): {byte_hash}")
    print(f"Saved to: {final_output}")
    #
    # print(f"\n")
    # print(f"Message Places: {mess_places}\n")
    # print(f"Hash Places: {hash_places}")
    # print(f"")









