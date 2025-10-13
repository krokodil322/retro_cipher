import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")

SOUNDS_DIR = os.path.join(RESOURCES_DIR, "sounds")
IMAGES_DIR = os.path.join(RESOURCES_DIR, "images")
BACKGROUNDS_DIR = os.path.join(IMAGES_DIR, "backgrounds")
BUTTONS_DIR = os.path.join(IMAGES_DIR, "buttons")

FONTS_DIR = os.path.join(RESOURCES_DIR, "fonts")
STYLES_DIR = os.path.join(RESOURCES_DIR, "styles")


if __name__ == "__main__":
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"RESOURCES_DIR: {RESOURCES_DIR}")
    print(f"SOUNDS_DIR: {SOUNDS_DIR}")
    print(f"IMAGES_DIR: {IMAGES_DIR}")
    print(f"BACKGROUNS_DIR: {BACKGROUNDS_DIR}")
    print(f"BUTTONS_DIR: {BUTTONS_DIR}")
    print(f"FONTS_DIR: {FONTS_DIR}")
    print(f"STYLES_DIR: {STYLES_DIR}")




