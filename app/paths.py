import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.split(BASE_DIR)[0]
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
if "config" not in os.listdir():
    os.mkdir(CONFIG_DIR)

RESOURCES_DIR = os.path.join(BASE_DIR, "resources")

SOUNDS_DIR = os.path.join(RESOURCES_DIR, "sounds")
IMAGES_DIR = os.path.join(RESOURCES_DIR, "images")
ICONS_DIR = os.path.join(IMAGES_DIR, "icons")
BACKGROUNDS_DIR = os.path.join(IMAGES_DIR, "backgrounds")
BUTTONS_DIR = os.path.join(IMAGES_DIR, "buttons")

FONTS_DIR = os.path.join(RESOURCES_DIR, "fonts")
STYLES_DIR = os.path.join(RESOURCES_DIR, "styles")


if __name__ == "__main__":
    print(f"ROOT_DIR: {ROOT_DIR}")
    print(f"CONFIG_DIR: {CONFIG_DIR}")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"RESOURCES_DIR: {RESOURCES_DIR}")
    print(f"SOUNDS_DIR: {SOUNDS_DIR}")
    print(f"IMAGES_DIR: {IMAGES_DIR}")
    print(f"ICONS_DIR: {ICONS_DIR}")
    print(f"BACKGROUNS_DIR: {BACKGROUNDS_DIR}")
    print(f"BUTTONS_DIR: {BUTTONS_DIR}")
    print(f"FONTS_DIR: {FONTS_DIR}")
    print(f"STYLES_DIR: {STYLES_DIR}")




