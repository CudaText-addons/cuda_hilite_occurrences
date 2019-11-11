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

LEXERS_ALLOWED = ''
LEXERS_DISABLED = ''

THEMEITEM_CURRENT = 'LightBG5'
THEMEITEM_OTHER = 'LightBG2'

COLOR_FONT_CURRENT = 0
COLOR_FONT_OTHER = 0
COLOR_BG_CURRENT = 0
COLOR_BG_OTHER = 0


ALLOWED_ITEMS = ['IncludeBG1', 'IncludeBG2', 'IncludeBG3', 'IncludeBG4', 'SectionBG1', 'SectionBG2', 'SectionBG3', 'SectionBG4', 'LightBG1', 'LightBG2', 'LightBG3', 'LightBG4', 'LightBG5', ]
META_OPT = [
        {   "opt": "min_len",
            "cmt": ["Minimal length of fragment to handle"],
            "def": 2,
            "frm": "int",
            "chp": ""
        },
        {   "opt": "max_lines",
            "cmt": ["Maximal number of lines in document, when plugin is still active"],
            "def": 5000,
            "frm": "int",
            "chp": ""
        },
        {   "opt": "nearest_count",
            "cmt": ["Find matches only in ... lines above+below the caret"],
            "def": 10000,
            "frm": "int",
            "chp": ""
        },
        {   "opt": "sel_allow",
            "cmt": ["Plugin handles current selection (on selection changing)"],
            "def": True,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "sel_allow_spaces",
            "cmt": ["Use also whitespace in selection, otherwise trim it"],
            "def": False,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "sel_case_sens",
            "cmt": ["Search for selection is case-sensitive"],
            "def": False,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "sel_words_only",
            "cmt": ["Plugin handles selection only when it is whole word"],
            "def": False,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "sel_whole_words",
            "cmt": ["Search for selection finds whole words only"],
            "def": False,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "caret_allow",
            "cmt": ["Plugin handles word under caret (on caret moving)"],
            "def": True,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "caret_case_sens",
            "cmt": ["Search for word under caret is case-sensitive"],
            "def": True,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "caret_whole_words",
            "cmt": ["Search for word under caret finds whole words only"],
            "def": True,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "theme_item_current",
            "cmt": ["Element of syntax-theme, which color is used for word under caret"],
            "def": "SectionBG2",
            "frm": "strs",
            "lst": ALLOWED_ITEMS,
            "chp": ""
        },
        {   "opt": "theme_item_other",
            "cmt": ["Element of syntax-theme, which color is used for other found matches"],
            "def": "SectionBG1",
            "frm": "strs",
            "lst": ALLOWED_ITEMS,
            "chp": ""
        },
        {   "opt": "lexers_allowed",
            "cmt": ["Comma-separated list of allowed lexers"],
            "def": "",
            "frm": "str",
            "chp": ""
        },
        {   "opt": "lexers_disabled",
            "cmt": ["Comma-separated list of disabled lexers"],
            "def": "",
            "frm": "str",
            "chp": ""
        },
]