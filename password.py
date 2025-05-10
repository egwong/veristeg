from functions import *
"""
account for:
    length
    message
    hash
    extra - initialization vectors
"""


class Password:
    def __init__(self, password, image_width, image_height):
        self.password = password
        self.image_width = image_width
        self.image_height = image_height
        self.length_mask, self.message_mask, self.hash_mask, self.extra = self.get_initialization_vectors()
        self.length_iv, self.message_iv = self.turn_extra_into_ivs()
        self.set_hash_len_lengths()

    def get_initialization_vectors(self):
        bytes = self.password.encode('utf-8')
        bits = bytes_to_binary_string(bytes)

        length = ''
        message = ''
        hash = ''
        extra = ''

        for i in range(0, len(bits), 4):
            length += bits[i]
            message += bits[i + 1]
            hash += bits[i + 2]
            extra += bits[i + 3]

        return length, message, hash, extra

    def turn_extra_into_ivs(self):
        if len(self.extra) < 16:
            self.extra = self.extra * (16 // len(self.extra) + 1)

        total_pixels = self.image_width * self.image_height

        mid_point = len(self.extra) // 2
        len_half = self.extra[:mid_point]
        mess_half = self.extra[mid_point:]

        len_placement = int(len_half, 2) % total_pixels if len_half else 0
        mess_placement = int(mess_half, 2) % total_pixels if mess_half else 1

        if len_placement == mess_placement:
            mess_placement = (mess_placement + total_pixels // 3) % total_pixels
            if len_placement == mess_placement:
                mess_placement = (mess_placement + 1) % total_pixels
        return len_placement, mess_placement

    def set_hash_len_lengths(self):
        # if the hash len (256) > hash_iv then double it until it is not (3x for ensuring no out of bounds)
        while len(self.hash_mask) < 256 * 3:
            self.hash_mask = self.hash_mask * 2

        # if lengeth len > length_iv then double it until it is not (3x for ensuring no out of bounds)
        while len(self.length_mask) < 16 * 3:
            self.length_mask = self.length_mask * 2

    def set_message_length(self, message_length):
        # if the message len > message_iv then double it until it is not (3x for ensuring no out of bounds)
        while len(self.message_mask) < message_length * 3:
            self.message_mask = self.message_mask * 2
