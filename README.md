# veristeg
****Purpose:****
This started because Jake Denno told me that it would be nearly impossible to do, read'em and weep.

Run main.py to run the program for both encoding and decoding, for Mac is it 'python3 main.py' in the terminal.

***This is going to change, it lacks documentation, has repeat code that I copied and pasted from encode.py to decode.py, and this code makes it seem like I have never heard of the word 'efficiency'***

**How**
This steganography implementation uses a very stupid pseudo-random system to hide data and verify that the data has not changed through the use of SHA256 hash verification.

**Steganography Implementation**
* Veristeg uses the first pixel (pixel 0) as a seed for a pseudo-random algorithm to randomly choose pixels in the image to contain the hidden data.
* Because I was lazy and didn't want to hide the length in the same manner, the length of the data is given in pixels 1-16 (not including pixel 0). (I might implement the pseudo-random placement for length as well later, same for the seed)
* To save space and increase the amount of data that can be hidden, I implemented Huffman Encoding over UTF-8. I opted to not use Morse Code (even though it is smaller than my Huffman implementation) because Huffman solves the issue of intermediate representations being prefixes of other intermediate representations. The Huffman tree was built using the greedy algorithm discussed in CSC445 (Algorithms). 
* It should go without saying that the data is hidden in the Red channels of pixels.

**Hash Verification Implementation**
* Veristeg uses a SHA256 hash to verify the data has not been modified, MD5 would probably have worked (but pixels are cheap and data is expensive) and saved half the space that SHA256 too.
* The hash is hidden in the same manner as the data, it is given a seed (the seed for the hash placement is the first placement of the data) for a pseudo-random algorithm and chooses the pixels that will hold the computed hash.
* The hash is calculated by first determining its placements, setting all red channels in its placements to 0, and hashing this intermediate representation to ensure the hash does not affect the hash.
* The hash is verified in decoding by using first calculating the data placements (through its seed and length). Since the SHA256 is a consistent 256 bits, I generated 256 numbers within the allowed range (using the found seed in the data placements, and ensuring no collisions with data placements) and then collect the bits and turn them into bytes. To verify the hash I set all the red channels in the hash placements to 0 and hash it. I hash only the pixels to verify the given hash (There was possibly issues with hashing the whole file and getting a consistent value even if pixel data was the same, so I only hash pixels).

**Thank You To:**
* Jake Denno, for always making me want to do more
* Li Xu, for introducing me to steganography and the wonders of Python in cybersecurity

*TODO*
* walk for files instead of direct search