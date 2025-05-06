class Huffman:
    def __init__(self):
        self.frequencies = {
            ' ': 15.0,  # the space is technically the most common character in text
            'E': 12.7,
            'T': 9.1,
            'A': 8.2,
            'O': 7.5,
            'I': 7.0,
            'N': 6.7,
            'S': 6.3,
            'H': 6.1,
            'R': 6.0,
            'D': 4.3,
            'L': 4.0,
            'C': 2.8,
            'U': 2.8,
            'M': 2.4,
            'W': 2.4,
            'F': 2.2,
            'G': 2.0,
            'Y': 2.0,
            'P': 1.9,
            'B': 1.5,
            'V': 0.98,
            'K': 0.77,
            'J': 0.15,
            'X': 0.15,
            'Q': 0.095,
            'Z': 0.074,
            '0': 0.05,  # digits default least common
            '1': 0.05,
            '2': 0.05,
            '3': 0.05,
            '4': 0.05,
            '5': 0.05,
            '6': 0.05,
            '7': 0.05,
            '8': 0.05,
            '9': 0.05,
        }

        self.root = None
        self.codes = {}
        self.build_huffman_tree()
        self.generate_codes()

    class Node:
        def __init__(self, char, freq):
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None

        def __lt__(self, other):
            return self.freq < other.freq

        def is_leaf(self):
            return self.left is None and self.right is None

    def build_huffman_tree(self):
        """
        built using the greedy Huffman algorithm discussed in CSC445 (Algorithms)
        :return:
        """
        import heapq

        priority_queue = [self.Node(char, freq) for char, freq in self.frequencies.items()]
        heapq.heapify(priority_queue)

        if len(priority_queue) == 1:
            node = heapq.heappop(priority_queue)
            self.root = node
            return

        while len(priority_queue) > 1:
            left = heapq.heappop(priority_queue)
            right = heapq.heappop(priority_queue)

            internal_node = self.Node(None, left.freq + right.freq)
            internal_node.left = left
            internal_node.right = right

            heapq.heappush(priority_queue, internal_node)

        self.root = priority_queue[0]

    def generate_codes(self):
        """
        dfs, init the huffman codes
        :return: None
        """
        def dfs(node, code):
            if node:
                if node.is_leaf():
                    self.codes[node.char] = code
                else:
                    dfs(node.left, code + '0')
                    dfs(node.right, code + '1')

        dfs(self.root, '')

    def encode(self, text):
        """
        encode a text string
        :return string of binary representation of huffman
        """
        if not text:
            return ""

        encoded = ''
        for char in text:
            char_upper = char.upper()
            if char_upper in self.codes:
                encoded += self.codes[char_upper]
            else:
                print(f"char: '{char} not valid'")

        return encoded

    def decode(self, encoded_text):
        """
        decode a bin string based on our huffman tree
        :return a string
        """
        if not encoded_text:
            return ""

        if not self.root:
            raise ValueError("build_huffman_tree() failed somehow")

        decoded = ''
        current_node = self.root

        for bit in encoded_text:
            if bit not in ('0', '1'):
                raise ValueError(f"Invalid: {bit}, not 1 or 0")

            if bit == '0':
                current_node = current_node.left
            elif bit == '1':
                current_node = current_node.right

            if current_node.is_leaf():
                decoded += current_node.char
                current_node = self.root

        if current_node != self.root:
            print("This text does not belong to this encoding")

        return decoded

    def print_codes(self):
        sorted_codes = sorted(self.codes.items(), key=lambda x: (len(x[1]), x[0]))

        print("Huffman Codes:")
        for char, code in sorted_codes:
            if char == ' ':
                print(f"Space: {code}")
            else:
                print(f"{char}: {code}")
