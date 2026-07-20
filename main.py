##  Sprint1
#def main():
#    print("===================================")
#    print(" Work Aerobic Toolkit v0.1.0")
#    print("===================================")


#if __name__ == "__main__":
#    main()

## Sprint 2
from analysis.scanner import scan_music


def main():

    print("=" * 50)
    print("Work Aerobic Toolkit")
    print("Version 0.2.0")
    print("=" * 50)

    songs = scan_music("input")

    print()

    print(f"Found {len(songs)} songs")

    print()

    for i, song in enumerate(songs, start=1):
        print(f"{i:03d}. {song.name}")


if __name__ == "__main__":
    main()