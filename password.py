from functions import bytes_to_binary_string
"""
account for:
    length
    message
    hash
"""


class Password:
    def __init__(self, password):
        self.password = password
        self.length_iv, self.message_iv, self.hash_iv, self.extra = self.get_initialization_vectors()

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
