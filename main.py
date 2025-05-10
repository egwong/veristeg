import encode
import decode


def main():
    print(f"\nHello! Would you like to encode or decode an image?")
    while True:
        e_or_d = input("Type 'E' for encoding OR type 'D' for decoding (or 'Q' to exit):\n")
        if e_or_d.upper() == 'E':
            try:
                encode.main()
                encode.reset_positions()
            except Exception as e:
                print(f"oopsie, something fucked up while encoding\n{e}")
        elif e_or_d.upper() == 'D':
            try:
                decode.main()
                decode.reset_positions()
            except Exception as e:
                print(f"oopsie, something fucked up while decoding\n{e}")
        elif e_or_d.upper() == 'Q':
            print("LATER LOSER")
            break
        else:
            print("oops! you don't seem to have eyes!\ntype only E, D, or Q")


if __name__ == "__main__":
    main()

