from cudax_lib import get_translation
_ = get_translation(__file__)  # I18N

MIN_LEN = 1
MAX_LINES = 3000
MAX_LINE_LEN = 800000
MAX_COLUMNS = 500
MAX_TIME = 40
AVG_LEN = 100

SEL_ALLOW             = True  # Highlight all occurrences of selected text.
SEL_ALLOW_WHITE_SPACE = False # Highlight spaces there located in begin or end of selection
SEL_CASE_SENSITIVE    = False
SEL_WORDS_ONLY        = False # Highlight character only if it contains in CHARS.
SEL_WHOLE_WORDS       = False # Whole word only. Used only if bool(SEL_WORDS_ONLY) == True.

MARK_IGNORE_MIN_LEN   = False
VISIBLE_FALLBACK      = True

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
            "def": MIN_LEN,
            "frm": "int",
            "chp": ""
        },
        {   "opt": "max_lines",
            "cmt": [_("Maximal number of lines in document, when plugin is still active")],
            "def": MAX_LINES,
            "frm": "int",
            "chp": ""
        },
        {   "opt": "max_line_len",
            "cmt": [_("Maximal length of lines, which will be handled by plugin (plugin will skip longer lines)")],
            "def": MAX_LINE_LEN,
            "frm": "int",
            "chp": ""
        },
        {   "opt": "max_time",
            "cmt": [_("Maximal time in milliseconds, to count chars in the document")],
            "def": MAX_TIME,
            "frm": "int",
            "chp": ""
        },
        {   "opt": "avg_len",
            "cmt": [_("Average length of line. If document has lot of longer lines, it will fallback to highlight only visible matches.")],
            "def": AVG_LEN,
            "frm": "int",
            "chp": ""
        },
        {   "opt": "sel_allow",
            "cmt": [_("Plugin handles current selection (on selection changing)")],
            "def": SEL_ALLOW,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "sel_allow_spaces",
            "cmt": [_("Use also whitespace in selection, otherwise trim it")],
            "def": SEL_ALLOW_WHITE_SPACE,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "sel_case_sens",
            "cmt": [_("Search for selection is case-sensitive")],
            "def": SEL_CASE_SENSITIVE,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "sel_words_only",
            "cmt": [_("Plugin handles selection only when it is whole word")],
            "def": SEL_WORDS_ONLY,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "sel_whole_words",
            "cmt": [_("Search for selection finds whole words only")],
            "def": SEL_WHOLE_WORDS,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "mark_ignore_min_len",
            "cmt": [_("Mark occurrences of selected text ignores 'min_len' option")],
            "def": MARK_IGNORE_MIN_LEN,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "visible_fallback",
            "cmt": [_("When text is over max_lines - fallback to highlighting only in visible text")],
            "def": VISIBLE_FALLBACK,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "caret_allow",
            "cmt": [_("Plugin handles word under caret (on caret moving)")],
            "def": CARET_ALLOW,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "caret_case_sens",
            "cmt": [_("Search for word under caret is case-sensitive")],
            "def": CARET_CASE_SENSITIVE,
            "frm": "bool",
            "chp": ""
        },
        {   "opt": "caret_whole_words",
            "cmt": [_("Search for word under caret finds whole words only")],
            "def": CARET_WHOLE_WORDS,
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
            "def": LEXERS_ALLOWED,
            "frm": "str",
            "chp": ""
        },
        {   "opt": "lexers_disabled",
            "cmt": [_("If not empty, then plugin is disabled for mentioned lexers. Comma-separated list."),
                    _("Has higher priority than option 'lexers_allowed'.")],
            "def": LEXERS_DISABLED,
            "frm": "str",
            "chp": ""
        },
]
