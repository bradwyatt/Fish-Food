import sys


ITCH_MODE_ARGS = {"itch", "--itch"}
IS_WEB_RUNTIME = sys.platform == "emscripten"
ITCH_MODE = IS_WEB_RUNTIME or any(arg.lower() in ITCH_MODE_ARGS for arg in sys.argv[1:])
