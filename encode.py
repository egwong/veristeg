import image
from PIL import Image
from huffman import Huffman
import os
import re
import rng
import hashlib
from functions import bytes_to_binary_string, get_target_file, get_actual_hash, is_valid_utf8
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


def no_pass_generate_message_places(mess, imag_ob):
    places = []

    with Image.open(imag_ob.path) as img:
        r, g, b, a = img.getpixel((0, 0))
        seed = r * g + b

        places = generate_places(seed, len(mess), imag_ob)
    return places


def no_pass_place_length(mess, imag_ob, working_path):
    high, low = divmod(len(mess), 256)

    high_bits = format(high, '08b')
    low_bits = format(low, '08b')

    combined = high_bits + low_bits

    image_length = (imag_ob.width * imag_ob.height) - 1
    mark_position_used(image_length)

    y, x = divmod(image_length, imag_ob.width)

    with Image.open(working_path) as img:
        img = img.convert('RGBA')
        r, g, b, a = img.getpixel((x, y))
        seed = r * g + b
        places = generate_places(seed, len(combined), imag_ob)

    place_bits(places, combined, imag_ob, working_path)


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


# put that shit into the image
def place_bits(places, binary_data, imag, working_path):
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
        print(f"failed in place_bits: {e}")


def create_final_output(working_path, original_filename):
    cwd = os.getcwd()
    base_filename = os.path.basename(original_filename)
    final_name = 'modified_' + base_filename
    final_path = os.path.join(cwd, final_name)

    try:
        os.rename(working_path, final_path)
    except:
        with Image.open(working_path) as img:
            img.save(final_path)
        os.remove(working_path)

    return final_path


def determine_password_use():
    try:
        while True:
            i = input("Would you like to encode you message with password protection (recommended)? (y/n)")
            if i.lower() == 'y':
                return True
            elif i.lower() == 'n':
                return False
            else:
                print("Please only type 'y' or 'n'")
    except Exception as e:
        print("Failed to determine_password_use")
        print(e)


def get_password():
    try:
        while True:
            i = input("Please provide the password (all UTF-8 allowed, length limit of 100 chars):\n")
            if i and 100 > len(i) > 0 and is_valid_utf8(i):
                good = input(f"Your password is [ {i} ], good? (y/n): ")
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


def create_modified_copy(original_path):
    cwd = os.getcwd()
    base_filename = os.path.basename(original_path)
    working_name = 'temp_working_' + base_filename
    working_path = os.path.join(cwd, working_name)
    with Image.open(original_path) as img:
        img = img.convert('RGBA')
        img.save(working_path)
    return working_path


def main():
    # get input
    # convert input to bin (huffman)
    # put into image
        # calculate where image stegs will go

    # put hash into image
        # calculate where hash will go
        # ensure no collision with message
    reset_positions()

    hash_placed_full, mess_placed_name, len_placed_name, hash_placed_name, byte_hash = None, None, None, None, None
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
        password = Password(string_password)




    else:
        no_pass_place_length(bin_message, file_ob, working_path)

        # print("after no_pass_place_length")

        mess_places = no_pass_generate_message_places(bin_message, file_ob)
        assert len(mess_places) == len(bin_message)

        # print("after assert")

        place_bits(mess_places, bin_message, file_ob, working_path)

        hash_places = generate_places(mess_places[0], 256, file_ob)

        # print("after calculating hash places")

        # For hash calculation, we need to compute it based on the current state of working_path
        byte_hash = get_actual_hash(hash_places, working_image)
        binary_hash = bytes_to_binary_string(byte_hash)

        # print("after calculating bytes_to_binary_string for hash")

        place_bits(hash_places, binary_hash, file_ob, working_path)

    final_output = create_final_output(working_path, target_file)

    print(f"")
    print(f"Original Message Size: {len(message)*8} assuming UTF-8")
    print(f"Huffman Message Size:  {len(bin_message)}")
    print(f"Compression Rate: {(len(message)*8)/len(bin_message)}")
    print(f"")

    print(f"Calculated Hash (bytes): {byte_hash}")
    print(f"Saved to: {final_output}")









