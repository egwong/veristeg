import image
from PIL import Image
from huffman import Huffman
import os
import re
import rng
import hashlib

SHA256_BYTES = 32
SHA256_BITS = 256
START = 17


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


def generate_places(mess, imag):
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
        while i < len(mess):
            num = rando.randint(START, image_length)
            if num not in places:
                places.append(num)
                i += 1
    return places


def place_length(mess, imag):
    high, low = divmod(len(mess), 256)

    high_bits = format(high, '08b')
    low_bits = format(low, '08b')

    with Image.open(imag.path) as img:
        img = img.convert('RGBA')
        pixels = img.load()

        for i in range(8):
            pixel_pos = i + 1
            x, y = pixel_pos % img.width, pixel_pos // img.width
            r, g, b, a = pixels[x, y]

            bit = int(high_bits[i])
            new_r = (r & 0xFE) | bit

            pixels[x, y] = (new_r, g, b, a)

        for i in range(8):
            pixel_pos = i + 9
            x, y = pixel_pos % img.width, pixel_pos // img.width
            r, g, b, a = pixels[x, y]

            bit = int(low_bits[i])
            new_r = (r & 0xFE) | bit

            pixels[x, y] = (new_r, g, b, a)

        img.save('length_placed_' + os.path.basename(imag.path))

    return 'length_placed_' + os.path.basename(imag.path)


# put that shit into the image
def place_message(places, message, imag):
    # get the length, width of the image
    height = imag.height
    width = imag.width

    with Image.open(imag.path) as img:
        pixels = img.load()
        for i in range(len(places)):
            place = places[i]
            mess_bit = message[i]
            bit = int(mess_bit)
            y, x = divmod(place, width)
            # r, g, b, a = img.getpixel((x, y))
            r, g, b, a = pixels[x, y]
            new_r = (r & 0xFE) | bit
            pixels[x, y] = (new_r, g, b, a)
        img.save('message_placed_' + os.path.basename(imag.path))
    return 'message_placed_' + os.path.basename(imag.path)


# seed will need to be places[0]
# has to be utf-8 because we won't know the size beforehand
def calculate_hash_places(mess_places, imag):
    image_length = imag.width * imag.height
    hash_places = []
    seed = mess_places[0]
    rando = rng.DeterministicRNG(seed=seed)
    i = 0
    while i < SHA256_BITS:
        num = rando.randint(START, image_length)
        if num not in mess_places and num not in hash_places:
            hash_places.append(num)
            i += 1
    return hash_places


def place_hash(places, hash_bits, imag):
    # get the length, width of the image
    height = imag.height
    width = imag.width

    with Image.open(imag.path) as img:
        pixels = img.load()
        for i in range(len(places)):
            place = places[i]
            hash_bit = hash_bits[i]
            bit = int(hash_bit)
            y, x = divmod(place, width)
            # r, g, b, a = img.getpixel((x, y))
            r, g, b, a = pixels[x, y]
            new_r = (r & 0xFE) | bit
            pixels[x, y] = (new_r, g, b, a)
        img.save('hash_placed_' + os.path.basename(imag.path))
    return 'hash_placed_' + os.path.basename(imag.path)


# set all hash-places to 0 and then hash
def get_hash(hash_places, message_placed_image):
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


# convert hash bytes to a binary utf-8 string
def bytes_to_binary_string(hash_bytes):
    binary_string = ''
    for byte in hash_bytes:
        binary_byte = format(byte, '08b')
        binary_string += binary_byte
    return binary_string


def clean_up_files(filenames):
    for filename in filenames:
        try:
            os.remove(filename)
        except Exception as e:
            print(f"Error deleting {filename}: {e}")


# deletes all the shit infront of the filename
def create_final_output(final_hash_placed_path, original_filename):
    cwd = os.getcwd()

    base_filename = os.path.basename(original_filename)
    final_name = 'modified_' + base_filename
    final_path = os.path.join(cwd, final_name)

    with Image.open(final_hash_placed_path) as img:
        img.save(final_path)

    return final_path


def main():
    # get input
    # convert input to bin (huffman)
    # put into image
        # calculate where image stegs will go

    # put hash into image
        # calculate where hash will go
        # ensure no collision with message

    cwd = os.getcwd()

    target_file = get_target_file()
    full_target = os.path.join(cwd, target_file)
    file_ob = image.ImageInfo(full_target)

    message = get_input().upper()
    huffman = Huffman()
    bin_message = huffman.encode(message)

    # place length
    # delete later
    len_placed_name = place_length(bin_message, file_ob)
    len_placed_full = os.path.join(cwd, len_placed_name)
    len_placed = image.ImageInfo(len_placed_full)

    # get places
    mess_places = generate_places(bin_message, file_ob)
    assert len(mess_places) == len(bin_message)

    # place message into len_placed
    mess_placed_name = place_message(mess_places, bin_message, len_placed)
    mess_placed_full = os.path.join(cwd, mess_placed_name)
    mess_placed = image.ImageInfo(mess_placed_full)

    # get hash places
    # uses the original file_ob, hopefully doesn't cause issues
    hash_places = calculate_hash_places(mess_places, file_ob)

    # get the hash of the image with no hash-place-pixels
    byte_hash = get_hash(hash_places, mess_placed)
    binary_hash = bytes_to_binary_string(byte_hash)

    # place the hash
    hash_placed_name = place_hash(hash_places, binary_hash, mess_placed)
    hash_placed_full = os.path.join(cwd, hash_placed_name)

    final_output = create_final_output(hash_placed_full, target_file)

    to_clean = [mess_placed_name, len_placed_name, hash_placed_name]
    clean_up_files(to_clean)

    print(f"")
    print(f"Original Message Size: {len(message)*8} assuming UTF-8")
    print(f"Huffman Message Size:  {len(bin_message)}")
    print(f"Compression Rate: {(len(message)*8)/len(bin_message)}")
    print(f"")

    print(f"Calculated Hash (bytes): {byte_hash}")









