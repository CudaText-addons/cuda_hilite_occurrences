import os
import json
import cudatext as app
import cudax_lib as appx
import cuda_options_editor as op_ed
from . import opt

NONWORD_DEF = '''-+*=/\()[]{}<>"'.,:;~?!@#$%^&|`…'''
NONWORD = {}
MARKTAG = 101 #uniq value for all markers plugins
fn_config = os.path.join(app.app_path(app.APP_DIR_SETTINGS), 'cuda_hilite_occurrences.json')
fn_meta = os.path.join(app.app_path(app.APP_DIR_SETTINGS), 'cuda_hilite_occurrences_meta.json')

ALLOWED_ITEMS = ['IncludeBG1', 'IncludeBG2', 'IncludeBG3', 'IncludeBG4', 'SectionBG1', 'SectionBG2', 'SectionBG3', 'SectionBG4', 'LightBG1', 'LightBG2', 'LightBG3', 'LightBG4', 'LightBG5', ]

def bool_to_str(v): return '1' if v else '0'
def str_to_bool(s): return s=='1'

def log(s):
    pass
    #print(s)

def get_line(ed, n):
    # limit max length of line
    return ed.get_text_line(n, 500)

def do_load_ops():
    
    if os.path.isfile(fn_config):
        d = json.load(open(fn_config, 'r'))
    else:
        d = {}

    opt.MIN_LEN               = d.get('min_len', 2)
    opt.MAX_LINES             = d.get('max_lines', 5000)
    opt.USE_NEAREST_LINE_COUNT = d.get('nearest_count', 10000)

    opt.SEL_ALLOW             = d.get('sel_allow', True)
    opt.SEL_ALLOW_WHITE_SPACE = d.get('sel_allow_spaces', False)
    opt.SEL_CASE_SENSITIVE    = d.get('sel_case_sens', False)
    opt.SEL_WORDS_ONLY        = d.get('sel_words_only', False)
    opt.SEL_WHOLE_WORDS       = d.get('sel_whole_words', False)

    opt.CARET_ALLOW           = d.get('caret_allow', True)
    opt.CARET_CASE_SENSITIVE  = d.get('caret_case_sens', True)
    opt.CARET_WHOLE_WORDS     = d.get('caret_whole_words', True)

    opt.THEMEITEM_CURRENT     = d.get('theme_item_current', 'SectionBG2')
    opt.THEMEITEM_OTHER       = d.get('theme_item_other', 'SectionBG1')

    theme = app.app_proc(app.PROC_THEME_SYNTAX_DICT_GET, '')
    item_id = theme['Id']
    item_cur = theme.get(opt.THEMEITEM_CURRENT)
    item_oth = theme.get(opt.THEMEITEM_OTHER)

    opt.COLOR_FONT_CURRENT = item_id['color_font']
    opt.COLOR_FONT_OTHER = opt.COLOR_FONT_CURRENT

    if item_cur and item_oth:
        opt.COLOR_BG_CURRENT = item_cur['color_back']
        opt.COLOR_BG_OTHER = item_oth['color_back']
    else:
        print('Incorrect theme item(s) "%s", "%s" in "%s"'%(opt.THEMEITEM_CURRENT, opt.THEMEITEM_OTHER, fn_config))
        opt.COLOR_BG_CURRENT = 0x80e080
        opt.COLOR_BG_OTHER = 0x00e0e0

    opt.LEXERS_ALLOWED = d.get('lexers_allowed', '')
    opt.LEXERS_DISABLED = d.get('lexers_disabled', '')


def is_lexer_ok(s):

    if opt.LEXERS_DISABLED:
        if ','+s+',' in ','+opt.LEXERS_DISABLED+',':
            return False

    if opt.LEXERS_ALLOWED:
        return ','+s+',' in ','+opt.LEXERS_ALLOWED+','
    else:
        return True


class Command:

    def __init__(self):
        do_load_ops()

    def on_save(self, ed_self):
        fn = ed_self.get_filename()
        if fn==fn_config:
            do_load_ops()

    def config(self):

        open(fn_meta, 'w').write(json.dumps([
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
            "def": "SectionBG2",
            "frm": "strs",
            "lst": ALLOWED_ITEMS,
            "chp": ""
        },
        ]))

        subset = '' # Key for isolated storage on plugin settings
        title = 'Highlight Occurrences options'
        how = {'hide_lex_fil': True, 'stor_json': fn_config}
        op_ed.OptEdD(path_keys_info=fn_meta, subset=subset, how=how).show(title)

    def on_caret(self, ed_self):

        lex = ed_self.get_prop(app.PROP_LEXER_FILE)
        if not lex:
            lex = '-'
        if not is_lexer_ok(lex):
            return

        ed_self.attr(app.MARKERS_DELETE_BY_TAG, MARKTAG)

        if ed_self.get_line_count()>opt.MAX_LINES:
            return

        current_text = _get_current_text(ed_self)
        if not current_text: return

        text, caret_pos, is_selection = current_text

        if caret_pos[1] != caret_pos[3]: return # no multiline
        if not opt.SEL_ALLOW_WHITE_SPACE: text = text.strip()
        if not text: return

        if is_selection:
            case_sensitive = opt.SEL_CASE_SENSITIVE
            words_only     = opt.SEL_WORDS_ONLY
            whole_words    = opt.SEL_WHOLE_WORDS if opt.SEL_WORDS_ONLY else False
        else:
            case_sensitive = opt.CARET_CASE_SENSITIVE
            words_only     = True
            whole_words    = opt.CARET_WHOLE_WORDS

        if len(text) < opt.MIN_LEN: return

        carets = ed_self.get_carets()
        if len(carets) != 1: return

        x0, y0, x1, y1 = caret_pos
        if x0 > x1: x0, x1 = x1, x0

        items = find_all_occurrences(ed_self, text, case_sensitive, whole_words, words_only)

        if not items or (len(items) == 1 and items[0] == (x0, y1)):
            app.msg_status('')
            return

        for item in items:
            if item == (x0, y0): continue

            ed_self.attr(app.MARKERS_ADD, MARKTAG, item[0], item[1], len(text), opt.COLOR_FONT_OTHER, opt.COLOR_BG_OTHER)
        else:
            if opt.CARET_ALLOW and not is_selection:
                ed_self.attr(app.MARKERS_ADD, MARKTAG, x0, y0, len(text), opt.COLOR_FONT_CURRENT, opt.COLOR_BG_CURRENT)

        app.msg_status('Matches hilited: {}'.format(len(items)))


def is_word(s, lexer):
    bads = NONWORD.get(lexer)
    if bads is None:
        bads = appx.get_opt('nonword_chars', NONWORD_DEF, appx.CONFIG_LEV_ALL, lexer=lexer)
        NONWORD[lexer] = bads

    for ch in s:
        if ch in ' \t'+bads:
            return False
    return True


def find_all_occurrences(ed, text, case_sensitive, whole_words, words_only):
    '''
    Finding matches to hilite
    '''
    lex = ed.get_prop(app.PROP_LEXER_FILE)
    if words_only and not is_word(text, lex):
        log('Hilite Occur: refured to search not whole word: '+text)
        return

    if not case_sensitive: text = text.lower()

    # don't handle entire file, handle only range
    line_min = max(0, ed.get_prop(app.PROP_LINE_TOP) - opt.USE_NEAREST_LINE_COUNT)
    line_max = min(ed.get_line_count()-1, ed.get_prop(app.PROP_LINE_BOTTOM) + opt.USE_NEAREST_LINE_COUNT)

    res = []
    for y in range(line_min, line_max+1):
        line = get_line(ed, y)
        if not line: continue
        #if len(line) > opt.MAX_LINE_LEN: continue

        if not case_sensitive: line = line.lower()

        x = 0
        text_len = len(text)
        while True:
            x = line.find(text, x)
            if x < 0: break

            if whole_words:
                if x > 0 and is_word(line[x - 1], lex):
                    log('Skipped match, not whole word: "%s", pos %d, char "%s"' % (line, x, line[x - 1]))
                    x += text_len + 1
                    continue

                next_char = x + text_len
                if next_char < len(line) and is_word(line[next_char], lex):
                    log('Skipped match, not whole word: "%s", pos %d, char "%s"' % (line, x, line[next_char]))
                    x += 2
                    continue

            res.append((x, y))

            x += text_len

    return res


def get_word_under_caret(ed):
    '''
    Gets tuple (word_under_caret, (x1, y1, x2, y2))
    Don't consider, is selection exist
    '''

    lex = ed.get_prop(app.PROP_LEXER_CARET)
    x1, y1, x2 = ed.get_carets()[0][:3]
    y2 = y1

    l_char = r_char = ''
    current_line = get_line(ed, y1)
    #if len(current_line) > opt.MAX_LINE_LEN: return

    if current_line:
        x = x1
        if x > 0:                 l_char = current_line[x - 1]
        if x < len(current_line): r_char = current_line[x]

        l_char, r_char = is_word(l_char, lex), is_word(r_char, lex)

        if not (l_char or r_char): return

        if l_char:
            for x1 in range(x - 1, -1, -1):
                if is_word(current_line[x1], lex): continue
                else: break
            else: x1 = -1
            x1 += 1

        if r_char:
            for x2 in range(x + 1, len(current_line)):
                if is_word(current_line[x2], lex): continue
                else: break
            else: x2 = len(current_line)
        else: x2 = x

        word_under_caret = current_line[x1 : x2]
    else: return

    return word_under_caret, (x1, y1, x2, y2)


def _get_current_text(ed):
    caret_pos = ed.get_carets()[0]
    x1, y1, x2, y2 = caret_pos
    is_selection = y2>=0
    current_text = ''

    if is_selection:
        if opt.SEL_ALLOW:
            current_text = ed.get_text_sel()
        else:
            return
    else:
        # sometimes caret can be beyond text end
        temp = get_line(ed, y1)
        if (temp is None) or (len(temp) < x1): return
        #if len(temp) > opt.MAX_LINE_LEN: return

        if opt.CARET_ALLOW:
            temp = get_word_under_caret(ed)
            if not temp: return
            current_text, caret_pos = temp

    return current_text, caret_pos, is_selection
