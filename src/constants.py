SKIN_DIRECTORY = "./ppvs2_skins/"
MODULE_DIRECTORY = "./modules/"
METADATA_FILE = "/metadata.yml"
PUZZLE_FILE_ROOT = "puzzle_"
PUZZLE_FILE_EXT = ".yml"
MODULE_PARAMETERS = {
    "board_shape": (range(12, 27), range(6, 17)),
    "board_nhide": range(1, 3),
    "move_shape": (range(2, 3), range(1, 3)),
    "color_limit": range(3, 6),
    "pop_limit": range(2, 7),
}
MODULE_DEFAULTS = {
    "board_shape": (12, 6),
    "board_nhide": 1,
    "move_shape": (2, 1),
    "color_limit": 4,
    "pop_limit": 4,
}
POP_SPEED = 0.35
