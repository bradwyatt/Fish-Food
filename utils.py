import pygame
import os

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 600
FPS = 60
TOP_UI_LAYER_HEIGHT = 60

IMAGES = {}
SOUNDS = {}
FONTS = {}

IMAGE_MANIFEST = [
    ("sprites/coral_reef.png", "spr_wall", True, None, None),
    ("sprites/player_left.png", "player_left", True, None, None),
    ("sprites/player_down_left.png", "player_down_left", True, None, None),
    ("sprites/player_down.png", "player_down", True, None, None),
    ("sprites/player_down_right.png", "player_down_right", True, None, None),
    ("sprites/player_right.png", "player_right", True, None, None),
    ("sprites/player_up_right.png", "player_up_right", True, None, None),
    ("sprites/player_up.png", "player_up", True, None, None),
    ("sprites/player_up_left.png", "player_up_left", True, None, None),
    ("sprites/player_left_munch.png", "player_left_munch", True, None, None),
    ("sprites/player_down_left_munch.png", "player_down_left_munch", True, None, None),
    ("sprites/player_down_munch.png", "player_down_munch", True, None, None),
    ("sprites/player_down_right_munch.png", "player_down_right_munch", True, None, None),
    ("sprites/player_right_munch.png", "player_right_munch", True, None, None),
    ("sprites/player_up_right_munch.png", "player_up_right_munch", True, None, None),
    ("sprites/player_up_munch.png", "player_up_munch", True, None, None),
    ("sprites/player_up_left_munch.png", "player_up_left_munch", True, None, None),
    ("sprites/player_left_face.png", "player_left_face", True, None, None),
    ("sprites/player_down_left_face.png", "player_down_left_face", True, None, None),
    ("sprites/player_down_face.png", "player_down_face", True, None, None),
    ("sprites/player_down_right_face.png", "player_down_right_face", True, None, None),
    ("sprites/player_right_face.png", "player_right_face", True, None, None),
    ("sprites/player_up_right_face.png", "player_up_right_face", True, None, None),
    ("sprites/player_up_face.png", "player_up_face", True, None, None),
    ("sprites/player_up_left_face.png", "player_up_left_face", True, None, None),
    ("sprites/player_left_gold.png", "player_left_gold", True, None, None),
    ("sprites/player_down_left_gold.png", "player_down_left_gold", True, None, None),
    ("sprites/player_down_gold.png", "player_down_gold", True, None, None),
    ("sprites/player_down_right_gold.png", "player_down_right_gold", True, None, None),
    ("sprites/player_right_gold.png", "player_right_gold", True, None, None),
    ("sprites/player_up_right_gold.png", "player_up_right_gold", True, None, None),
    ("sprites/player_up_gold.png", "player_up_gold", True, None, None),
    ("sprites/player_up_left_gold.png", "player_up_left_gold", True, None, None),
    ("sprites/red_fish.png", "spr_red_fish", True, None, None),
    ("sprites/green_fish.png", "spr_green_fish_right", True, None, None),
    ("sprites/big_green_fish_left.png", "spr_big_green_fish_left", True, None, None),
    ("sprites/big_green_fish_left_face.png", "spr_big_green_fish_left_face", True, None, None),
    ("sprites/big_green_fish_right.png", "spr_big_green_fish_right", True, None, None),
    ("sprites/big_green_fish_right_face.png", "spr_big_green_fish_right_face", True, None, None),
    ("sprites/big_green_fish_turning.png", "spr_big_green_fish_turning", True, None, None),
    ("sprites/silver_fish.png", "spr_silver_fish", True, None, None),
    ("sprites/snake_1.png", "spr_snake_1", True, None, None),
    ("sprites/snake_2.png", "spr_snake_2", True, None, None),
    ("sprites/snake_3.png", "spr_snake_3", True, None, None),
    ("sprites/snake_4.png", "spr_snake_4", True, None, None),
    ("sprites/seahorse.png", "spr_seahorse", True, None, None),
    ("sprites/jellyfish_1.png", "spr_jellyfish_1", True, None, None),
    ("sprites/jellyfish_2.png", "spr_jellyfish_2", True, None, None),
    ("sprites/jellyfish_3.png", "spr_jellyfish_3", True, None, None),
    ("sprites/jellyfish_4.png", "spr_jellyfish_4", True, None, None),
    ("sprites/jellyfish_5.png", "spr_jellyfish_5", True, None, None),
    ("sprites/jellyfish_6.png", "spr_jellyfish_6", True, None, None),
    ("sprites/jellyfish_7.png", "spr_jellyfish_7", True, None, None),
    ("sprites/shark_left.png", "spr_shark_left", True, None, None),
    ("sprites/shark_face_left.png", "spr_shark_face_left", True, None, None),
    ("sprites/shark_face_right.png", "spr_shark_face_right", True, None, None),
    ("sprites/shark_right.png", "spr_shark_right", True, None, None),
    ("sprites/shark_turning.png", "spr_shark_turning", True, None, None),
    ("sprites/bright_blue_fish_right.png", "spr_bright_blue_fish_right", True, None, None),
    ("sprites/bright_blue_fish_right_face.png", "spr_bright_blue_fish_right_face", True, None, None),
    ("sprites/bright_blue_fish_left.png", "spr_bright_blue_fish_left", True, None, None),
    ("sprites/bright_blue_fish_left_face.png", "spr_bright_blue_fish_left_face", True, None, None),
    ("sprites/starfish_1.png", "spr_star_1", True, None, None),
    ("sprites/starfish_2.png", "spr_star_2", True, None, None),
    ("sprites/starfish_3.png", "spr_star_3", True, None, None),
    ("sprites/arrow_warning_red.png", "arrow_warning_red_top", True, None, None),
    ("sprites/arrow_warning_silver.png", "arrow_warning_silver_top", True, None, None),
    ("sprites/arrow_warning_blue_left.png", "arrow_warning_blue_left", True, None, None),
    ("sprites/arrow_warning_blue_right.png", "arrow_warning_blue_right", True, None, None),
    ("sprites/seaweed_middle.png", "spr_seaweed", True, None, None),
    ("sprites/seaweed_left.png", "spr_seaweed_left", True, None, None),
    ("sprites/seaweed_right.png", "spr_seaweed_right", True, None, None),
    ("sprites/rainbow_fish_left.png", "spr_rainbow_fish_left", True, None, None),
    ("sprites/rainbow_fish_left_face.png", "spr_rainbow_fish_left_face", True, None, None),
    ("sprites/rainbow_fish_turning.png", "spr_rainbow_fish_turning", True, None, None),
    ("sprites/rainbow_fish_right.png", "spr_rainbow_fish_right", True, None, None),
    ("sprites/rainbow_fish_right_face.png", "spr_rainbow_fish_right_face", True, None, None),
    ("sprites/unpressed_arrow_up.png", "spr_unpressed_arrow_up", True, 128, None),
    ("sprites/pressed_arrow_up.png", "spr_pressed_arrow_up", True, 128, None),
    ("sprites/pressed_arrow_up_right.png", "spr_pressed_arrow_up_right", True, 128, None),
    ("sprites/pressed_arrow_right.png", "spr_pressed_arrow_right", True, 128, None),
    ("sprites/pressed_arrow_down_right.png", "spr_pressed_arrow_down_right", True, 128, None),
    ("sprites/pressed_arrow_down.png", "spr_pressed_arrow_down", True, 128, None),
    ("sprites/pressed_arrow_down_left.png", "spr_pressed_arrow_down_left", True, 128, None),
    ("sprites/pressed_arrow_left.png", "spr_pressed_arrow_left", True, 128, None),
    ("sprites/pressed_arrow_up_left.png", "spr_pressed_arrow_up_left", True, 128, None),
    ("sprites/unpressed_arrow_up_right.png", "spr_unpressed_arrow_up_right", True, 128, None),
    ("sprites/unpressed_arrow_right.png", "spr_unpressed_arrow_right", True, 128, None),
    ("sprites/unpressed_arrow_down_right.png", "spr_unpressed_arrow_down_right", True, 128, None),
    ("sprites/unpressed_arrow_down.png", "spr_unpressed_arrow_down", True, 128, None),
    ("sprites/unpressed_arrow_down_left.png", "spr_unpressed_arrow_down_left", True, 128, None),
    ("sprites/unpressed_arrow_left.png", "spr_unpressed_arrow_left", True, 128, None),
    ("sprites/unpressed_arrow_up_left.png", "spr_unpressed_arrow_up_left", True, 128, None),
    ("sprites/neutral_zone.png", "spr_neutral_zone", True, 128, None),
    ("sprites/ground.jpg", "ground", False, None, None),
    ("sprites/play_background.jpg", "play_background", False, None, None),
    ("sprites/top_ui_layer.jpg", "top_ui_layer", False, None, None),
    ("sprites/start_menu.png", "start_menu_bg", False, None, None),
    ("sprites/info_screen.jpg", "info_screen_bg", False, None, None),
]

FONT_MANIFEST = [
    ("fonts/ocean_font.ttf", 16, False),
    ("fonts/ocean_font.ttf", 22, False),
    ("fonts/ocean_font.ttf", 48, False),
    ("fonts/ocean_font.ttf", 76, False),
    ("Arial", 32, True),
]

SOUND_MANIFEST = [
    ("sounds/snd_eat.ogg", "snd_eat", 0.2),
    ("sounds/eat_shark.ogg", "snd_eat_shark", 0.2),
    ("sounds/size_down.ogg", "snd_size_down", None),
    ("sounds/player_die.ogg", "snd_player_die", 0.3),
    ("sounds/powerup_timer.ogg", "snd_powerup_timer", 0.3),
    ("sounds/siren.ogg", "snd_siren", 0.05),
    ("sounds/shark_incoming.ogg", "snd_shark_incoming", 0.03),
]


def resolve_asset_path(file, preferred_extensions=None):
    """
    Resolve an asset path by trying a preferred extension order when the exact file
    is not available. This keeps call sites stable across web/native-friendly formats.
    """
    if os.path.exists(file):
        return file

    preferred_extensions = preferred_extensions or []
    root, ext = os.path.splitext(file)

    if ext:
        candidate_extensions = list(preferred_extensions)
        if ext not in candidate_extensions:
            candidate_extensions.append(ext)
    else:
        candidate_extensions = list(preferred_extensions)

    for candidate_ext in candidate_extensions:
        candidate = f"{root}{candidate_ext}"
        if os.path.exists(candidate):
            return candidate

    return file


class SilentSound:
    """No-op sound used when an asset can't be decoded in the current runtime."""

    def play(self, *args, **kwargs):
        return None

    def stop(self):
        return None

    def set_volume(self, *args, **kwargs):
        return None

def load_image(file, name, alpha=False, global_alpha=None, colorkey=None):
    """
    Loads an image, prepares it for play, and stores it in the IMAGES dictionary.
    :param file: Path to the image file.
    :param name: Name/key to store the image in the IMAGES dictionary.
    :param alpha: Boolean to indicate if alpha transparency should be used.
    :param global_alpha: Global alpha value to set for the image. 
                         Should be a number between 0 (transparent) and 255 (opaque).
    :param colorkey: Color key for transparency. If None, no colorkey is applied. 
                     If -1, the color of the top-left pixel is used.
    """
    try:
        image = pygame.image.load(file)
        if alpha:
            image = image.convert_alpha()  # Converts with per-pixel alpha

        if global_alpha is not None:
            image.set_alpha(global_alpha)  # Applies global alpha to the entire image

        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)

        if not alpha:
            image = image.convert()  # Converts without per-pixel alpha

        # Store the image in the global IMAGES dictionary
        IMAGES[name] = image
        return image
    except pygame.error as message:
        print('Cannot load image:', file)
        # Handle the error as per your game's requirements
        return None  # or any fallback mechanism

def load_sound(file, name):
    """
    Loads a sound file and stores it in the SOUNDS dictionary.
    :param file: Path to the sound file.
    :param name: Name/key to store the sound in the SOUNDS dictionary.
    """
    try:
        file = resolve_asset_path(file, preferred_extensions=[".ogg", ".wav", ".mp3"])
        sound = pygame.mixer.Sound(file)
        # Store the sound in the global SOUNDS dictionary
        SOUNDS[name] = sound
    except pygame.error as message:
        print('Cannot load sound:', file, message)
        SOUNDS[name] = SilentSound()

def load_font(name, size, is_system_font=False):
    """
    Loads a font and stores it in the FONTS dictionary.
    :param name: Name of the font file or system font.
    :param size: Size of the font.
    :param is_system_font: Boolean, True if loading a system font.
    """
    try:
        if is_system_font:
            font = pygame.font.SysFont(name, size)
        else:
            font = pygame.font.Font(name, size)
        
        if not is_system_font:
            # Use only the base name of the file (without path and extension) for the key
            base_name = os.path.splitext(os.path.basename(name))[0]
            font_key = f"{base_name.lower()}_{size}"
        else:
            # For system fonts, use the name directly
            font_key = f"{name.replace(' ', '_').lower()}_{size}"
    
        FONTS[font_key] = font
    except IOError as e:
        print(f"Cannot load font: {name}, {e}")
        raise SystemExit(e)


def load_all_assets():
    for file, name, alpha, global_alpha, colorkey in IMAGE_MANIFEST:
        load_image(file, name, alpha, global_alpha, colorkey)

    IMAGES["spr_green_fish_left"] = pygame.transform.flip(IMAGES["spr_green_fish_right"], 1, 0)

    bright_blue_keys = [
        "spr_bright_blue_fish_right",
        "spr_bright_blue_fish_right_face",
        "spr_bright_blue_fish_left",
        "spr_bright_blue_fish_left_face",
    ]
    for key in bright_blue_keys:
        IMAGES[key] = pygame.transform.smoothscale(IMAGES[key], (300, 200))

    IMAGES["top_ui_layer"] = pygame.transform.scale(
        IMAGES["top_ui_layer"],
        (SCREEN_WIDTH, TOP_UI_LAYER_HEIGHT),
    )

    for name, size, is_system_font in FONT_MANIFEST:
        load_font(name, size, is_system_font)

    pygame.mouse.set_visible(True)

    for file, name, volume in SOUND_MANIFEST:
        load_sound(file, name)
        if volume is not None:
            SOUNDS[name].set_volume(volume)

    try:
        pygame.mixer.music.load(resolve_asset_path("sounds/game_music.ogg", [".ogg", ".mp3", ".wav"]))
        pygame.mixer.music.set_volume(.1)
        pygame.mixer.music.play(-1)
    except pygame.error as message:
        print("Cannot load music:", message)
