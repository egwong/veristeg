# veristeg
****Purpose:****
This started because Jake Denno told me that it would be nearly impossible to do, read'em and weep.

Run main.py to run the program for both encoding and decoding, for Mac is it 'python3 main.py' in the terminal.

***! Steged files using a previous iteration of veristeg are not compatable with the new implementation***

***Do not use the password selection yet, it is not implemented and will cause an error. This is going to change, it lacks documentation, has repeat code that I copied and pasted from encode.py to decode.py, and this code makes it seem like I have never heard of the word 'efficiency'***

### How
This steganography implementation uses a very stupid pseudo-random system to hide data and verify that the data has not changed through the use of SHA256 hash verification.

**Steganography Implementation**
* Veristeg uses the first pixel's (pixel 0) blue value as a seed for a 2-part pseudo-random algorithm to randomly choose pixels in the image to contain the hidden data. 
* The length of the message data is hidden in the same manner where a 2-part pseudo-random algorithm is used as an initialization vector for where the length declaration is going to hide.
* To save space and increase the amount of data that can be hidden, I implemented Huffman Encoding over UTF-8. I opted to not use Morse Code (even though it is smaller than my Huffman implementation) because Huffman solves the issue of intermediate representations being prefixes of other intermediate representations. The Huffman tree was built using the greedy algorithm discussed in CSC445 (Algorithms). 
* The Huffman Encoding was also so that if the data was found, it would be significantly less obvious than if it was just UTF-8
* All data is hidden in the LSB of the red channel (for now, I want to change this later)
* The 2-part pseudo-random algorithm first creates 2 initialization vectors using a golden-ratio (phi) and offset (offset starts at pixel[0,0]'s blue value but gets incremented if a collision exists or an IV == 0), each IV correlates to a pixel in the image, the IV's pixel is then used to create a seed (r * g + b) and is then fed into a deterministic RNG to begin generating pixel-places for data. The two IVs correlate to the length declaration and message placements respectively.

**Hash Verification Implementation**
* Veristeg uses a SHA256 hash to verify the data has not been modified.
* The hash is hidden in the same manner as the data, it is given a seed (the seed for the hash placement is the first placement of the data) for a pseudo-random algorithm and chooses the pixels that will hold the computed hash.
* The hash is calculated by first determining its placements, setting all red channels in its placements to 0, and hashing this intermediate representation to ensure the hash does not affect the hash.
* The hash is verified in decoding by using first calculating the data placements (through its seed and length). Since the SHA256 is a consistent 256 bits, I generated 256 numbers within the allowed range (using the found seed in the data placements, and ensuring no collisions with data placements) and then collect the bits and turn them into bytes. To verify the hash I set all the red channels in the hash placements to 0 and hash it. I hash only the pixels to verify the given hash (There was possibly issues with hashing the whole file and getting a consistent value even if pixel data was the same, so I only hash pixels).

**Thank You To:**
* Jake Denno, for always making me want to do more
* Li Xu, for introducing me to steganography and the wonders of Python in cybersecurity

*TODO*
* Add option for password
* add option to spoof exif data
* walk for files instead of direct search
* increase diffusion
* change data from only being hidden in red channel to being distributed across different channels 
