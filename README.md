# veristeg
****Purpose:****
This started because Jake Denno told me that it would be nearly impossible to do, read'em and weep.

Run main.py to run the program for both encoding and decoding, for Mac is it 'python3 main.py' in the terminal.

***! Steged files using a previous iteration of veristeg are not compatable with the newest implementation***

***This is going to change, it lacks documentation, has repeat code that I copied and pasted from encode.py to decode.py, and this code makes it seem like I have never heard of the word 'efficiency'***

### About
This steganography implementation uses a pseudo-random algorithm to hide data and verify that the data has not changed through the use of SHA256 hash verification included in the steganograpy.

### Steganography Implementation
**No Password**
* Veristeg the first pixel's (pixel 0) blue value as a seed for a 2-part pseudo-random algorithm to randomly choose pixels in the image to contain the hidden data. 
* The length of the message data is hidden in the same manner where a 2-part pseudo-random algorithm is used as an initialization vector for where the length declaration is going to hide.
* The 2-part pseudo-random algorithm first creates 2 initialization vectors using a golden-ratio (phi) and offset (offset starts at pixel[0,0]'s blue value but gets incremented if a collision exists or an IV == 0), each IV correlates to a pixel in the image, the IV's pixel is then used to create a seed (r * g + b) and is then fed into a deterministic RNG to begin generating pixel-places for data. The two IVs correlate to the length declaration and message placements respectively.
* All data is hidden in the red channel


**Password**
* When a password is used a Password object is created, upon initialization it converts the password into binary UTF-8 and distributes every 4 pixels to 4 categories {the length mask, the message mask, the hash mask, and 'extra' which is converted into 2 initialization vectors for the length declaration and message placements}
* These masks are used to determine which color channel will be modified, the odd bit out will be the modified channel. 
* The 2 initialization vectors represent a pixel whose values will be used as a seed in a deterministic RNG to calculate their placements.

**Both No Password and Password**
* To save space and increase the amount of data that can be hidden, I implemented Huffman Encoding over UTF-8. I opted to not use Morse Code (even though it is smaller than my Huffman implementation) because Huffman solves the issue of intermediate representations being prefixes of other intermediate representations. The Huffman tree was built using the greedy algorithm discussed in CSC445 (Algorithms). 
* The Huffman Encoding was also so that if the data was found, it would be significantly less obvious than if it was just UTF-8
* All data is hidden in the LSB

**Hash Verification Implementation**
* Veristeg uses a SHA256 hash to verify the data has not been modified.
* The hash is hidden in the same manner as the data, it is given a seed (the seed for the hash placement is the first placement of the data) for a deterministic RNG and chooses the pixels that will hold the computed hash.
* The hash is calculated by first determining its placements:
  * For no password: setting all red channels in its placements to 0, and hashing this intermediate representation to ensure the hash does not affect the hash.
  * For password:  setting all masked channels in its placements to 0, and hashing this intermediate representation to ensure the hash does not affect the hash.
* The hash is verified in decoding by using first calculating the data placements (through its seed and length). Since the SHA256 is a consistent 256 bits, I generated 256 numbers within the allowed range (using the found seed in the data placements, and ensuring no collisions with data placements), then collect the bits and turn them into bytes. To verify the hash I set all the (red/masked) channels in the hash placements to 0 and hash it. I hash only the pixels to verify the given hash (There was possibly issues with hashing the whole file and getting a consistent value even if pixel data was the same, so I only hash pixels).

### Thank You To:
* Jake Denno, for always making me want to do more
* Li Xu, for introducing me to steganography and the wonders of Python in cybersecurity

***Iterations***
* 1: used pixel 0 as IV for message placement; length declaration in pixels 1-17; all data hidden in red channel.
* 2: used pixel 0 as IV for message placement; used pixel image_length-1 as IV for length declaration; all data hidden in red channel.
* 3: IV pixels for message and length declaration placement were calculated using the golden ratio (phi) on the image's width and length and an offset of pixel 0's blue value; all data hidden in LSB of red.
* 4: Added password to change IV pixels for message and length declaration placement; password also creates 3 masks for length, message, and hash placements; if no password is chosen then it defaults to Iteration 3's implementation.


*TODO*
* add option to include 2 messages in one image with different passwords
* add option to spoof exif data
* walk for files instead of direct search
* increase diffusion
