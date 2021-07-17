from cudax_lib import get_translation
_ = get_translation(__file__)  # I18N

MIN_LEN = 2
MAX_LINES = 5000
MAX_LINE_LEN = 500

SEL_ALLOW             = True  # Highlight all occurrences of selected text.
SEL_ALLOW_WHITE_SPACE = False # Highlight spaces there located in begin or end of selection
SEL_CASE_SENSITIVE    = False
SEL_WORDS_ONLY        = False # Highlight character only if it contains in CHARS.
SEL_WHOLE_WORDS       = False # Whole word only. Used only if bool(SEL_WORDS_ONLY) == True.

MARK_IGNORE_MIN_LEN   = False
VISIBLE_FALLBACK      = False

CARET_ALLOW           = True # Highlight all occurrences of word under caret.
CARET_CASE_SENSITIVE  = True
CARET_WHOLE_WORDS     = True # Whole word only.

LEXERS_ALLOWED = ''
LEXERS_DISABLED = ''

COLOR_FONT_CURRENT = 0
COLOR_FONT_OTHER = 0
COLOR_BG_CURRENT = 0
COLOR_BG_OTHER = 0

THEME_CURRENT = ''
THEME_OTHER = ''
COLOR_BRD_OTHER = 0
BRD_OTHER = 0
COLOR_BRD_CURRENT = 0
BRD_CURRENT = 0

ALLOWED_ITEMS = ['IncludeBG1', 'IncludeBG2', 'IncludeBG3', 'IncludeBG4', 'SectionBG1', 'SectionBG2', 'SectionBG3', 'SectionBG4', 'BracketBG', 'CurBlockBG', 'LightBG1', 'LightBG2', 'LightBG3', 'LightBG4', 'LightBG5']
META_OPT = [
        {   "opt": "min_len",
            "cmt": [_("Minimal length of fragment to handle")],
            "def": 2,
            "frm": "int",
            "chp": ""
        },
        {   "opt": "max_lines",
            "cmt": [_("Maximal number of lines in document, when plugin is still active")],
            "def": 5000,
            "frm": "int",
            "chp": ""
        },
        {   "opt": "max_line_len",
            "cmt": [_("Maximal length of lines, which will be handled by plugin (plugin will skip longer lines)")],
            "def": 500,
            "frm": "int",
            "chp": ""
        },
        {   "opt": "sel_allow",
            "cmt": [_("Plugin handles current selection (on selection changing)")],
            "def": True,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "sel_allow_spaces",
            "cmt": [_("Use also whitespace in selection, otherwise trim it")],
            "def": False,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "sel_case_sens",
            "cmt": [_("Search for selection is case-sensitive")],
            "def": False,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "sel_words_only",
            "cmt": [_("Plugin handles selection only when it is whole word")],
            "def": False,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "sel_whole_words",
            "cmt": [_("Search for selection finds whole words only")],
            "def": False,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "mark_ignore_min_len",
            "cmt": [_("Mark occurrences of selected text ignores 'min_len' option")],
            "def": False,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "visible_fallback",
            "cmt": [_("When text is over max_lines - fallback to highlighting only in visible text")],
            "def": False,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "caret_allow",
            "cmt": [_("Plugin handles word under caret (on caret moving)")],
            "def": True,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "caret_case_sens",
            "cmt": [_("Search for word under caret is case-sensitive")],
            "def": True,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "caret_whole_words",
            "cmt": [_("Search for word under caret finds whole words only")],
            "def": True,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "theme_item_current",
            "cmt": [_("Element of syntax-theme, which color is used for word under caret")],
            "def": "BracketBG",
            "frm": "strs",
            "lst": ALLOWED_ITEMS,
            "chp": ""
        },
        {   "opt": "theme_item_other",
            "cmt": [_("Element of syntax-theme, which color is used for other found matches")],
            "def": "BracketBG",
            "frm": "strs",
            "lst": ALLOWED_ITEMS,
            "chp": ""
        },
        {   "opt": "lexers_allowed",
            "cmt": [_("If not empty, then plugin is active only for mentioned lexers. Comma-separated list."),
                    _("None-lexer must be written as '-'.")],
            "def": "",
            "frm": "str",
            "chp": ""
        },
        {   "opt": "lexers_disabled",
            "cmt": [_("If not empty, then plugin is disabled for mentioned lexers. Comma-separated list."),
                    _("Has higher priority than option 'lexers_allowed'.")],
            "def": "",
            "frm": "str",
            "chp": ""
        },
]
