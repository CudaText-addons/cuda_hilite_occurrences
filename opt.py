MIN_LEN = 2
MAX_LINES = 5000
MAX_LINE_LEN = 2000
USE_NEAREST_LINE_COUNT = 10000

SEL_ALLOW             = True  # Hilite all occurrences of selected text.
SEL_ALLOW_WHITE_SPACE = False # Hilite spaces there located in begin or end of selection
SEL_CASE_SENSITIVE    = False
SEL_WORDS_ONLY        = False # Hilite character only if it containts in CHARS.
SEL_WHOLE_WORDS       = False # Whole word only. Used only if bool(SEL_WORDS_ONLY) == True.

CARET_ALLOW          = True # Hilite all occurrences of word under caret.
CARET_CASE_SENSITIVE = True
CARET_WHOLE_WORDS    = True # Whole word only.

COLOR_FONT_OTHER   = 0x000000
COLOR_BG_OTHER     = 0x80FFFF
COLOR_FONT_CURRENT = COLOR_FONT_OTHER
COLOR_BG_CURRENT   = 0xe3c1e3

LEXERS_ALLOWED = ''
LEXERS_DISABLED = ''
