import os
import json
import cudatext as app
import cudax_lib as appx
import cuda_options_editor as op_ed
from cudatext import ed
from . import opt

NONWORD_DEF = '''-+*=/\()[]{}<>"'.,:;~?!@#$%^&|`…'''
NONWORD = {}
MARKTAG = 101 #uniq value for all markers plugins
fn_config = 'cuda_hilite_occurrences.json'

def log(s):
    pass
    #print(s)

def get_opt(path, val):
    return appx.get_opt(path, val, user_json=fn_config)

def get_line(ed, n):
    # limit max length of line
    return ed.get_text_line(n, 500)

def do_load_ops():
    meta_def    = lambda op: [it['def'] for it in opt.META_OPT if it['opt']==op][0]

    opt.MIN_LEN               = get_opt('min_len',              meta_def('min_len'))
    opt.MAX_LINES             = get_opt('max_lines',            meta_def('max_lines'))
    opt.USE_NEAREST_LINE_COUNT = get_opt('nearest_count',       meta_def('nearest_count'))

    opt.SEL_ALLOW             = get_opt('sel_allow',            meta_def('sel_allow'))
    opt.SEL_ALLOW_WHITE_SPACE = get_opt('sel_allow_spaces',     meta_def('sel_allow_spaces'))
    opt.SEL_CASE_SENSITIVE    = get_opt('sel_case_sens',        meta_def('sel_case_sens'))
    opt.SEL_WORDS_ONLY        = get_opt('sel_words_only',       meta_def('sel_words_only'))
    opt.SEL_WHOLE_WORDS       = get_opt('sel_whole_words',      meta_def('sel_whole_words'))

    opt.CARET_ALLOW           = get_opt('caret_allow',          meta_def('caret_allow'))
    opt.CARET_CASE_SENSITIVE  = get_opt('caret_case_sens',      meta_def('caret_case_sens'))
    opt.CARET_WHOLE_WORDS     = get_opt('caret_whole_words',    meta_def('caret_whole_words'))

    opt.LEXERS_ALLOWED = get_opt('lexers_allowed', '')
    opt.LEXERS_DISABLED = get_opt('lexers_disabled', '')

    opt.theme_cur     = get_opt('theme_item_current',   meta_def('theme_item_current'))
    opt.theme_oth     = get_opt('theme_item_other',     meta_def('theme_item_other'))
    do_update_colors()

def do_update_colors():

    theme = app.app_proc(app.PROC_THEME_SYNTAX_DICT_GET, '')
    item_cur = theme.get(opt.theme_cur)
    item_oth = theme.get(opt.theme_oth)

    opt.COLOR_FONT_CURRENT = app.COLOR_NONE
    opt.COLOR_FONT_OTHER = app.COLOR_NONE

    if item_cur and item_oth:
        opt.COLOR_BG_CURRENT = item_cur['color_back']
        opt.COLOR_BRD_CURRENT = item_cur['color_border']
        opt.BRD_CURRENT = item_cur['border_bottom']
        opt.COLOR_BG_OTHER = item_oth['color_back']
        opt.COLOR_BRD_OTHER = item_oth['color_border']
        opt.BRD_OTHER = item_oth['border_bottom']
    else:
        print('Incorrect theme item(s) "%s", "%s" in "%s"'%(opt.THEMEITEM_CURRENT, opt.THEMEITEM_OTHER, fn_config))
        opt.COLOR_BG_CURRENT = 0x80e080
        opt.COLOR_BG_OTHER = 0x00e0e0
        opt.COLOR_BRD_CURRENT = 0
        opt.COLOR_BRD_OTHER = 0
        opt.BRD_CURRENT = 0
        opt.BRD_OTHER = 0


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

    def config(self):

#       open(fn_meta, 'w').write(json.dumps(opt.META_OPT))

        subset = '' # Key for isolated storage on plugin settings
        title = 'Highlight Occurrences options'
        how = {'hide_lex_fil': True, 'stor_json': fn_config}
#       if op_ed.OptEdD(path_keys_info=fn_meta, subset=subset, how=how).show(title):
        op_ed.OptEdD(
            path_keys_info=opt.META_OPT,
            subset=subset,
            how=how
        ).show(title)
        do_load_ops()

    def on_state(self, ed_self, state):

        if state==app.APPSTATE_THEME_SYNTAX:
            do_update_colors()
            self.on_caret(ed_self)

    def on_caret(self, ed_self):
        res = _process_occurrences(ed_self)
        if not res:
            return

        items, text, is_selection, x0, y0 = res

        ncount = len(items)
        nlen = len(text)
        items = [i for i in items if i!=(x0, y0)]
        xx = [i[0] for i in items]
        yy = [i[1] for i in items]
        nn = [nlen for i in items]
        ed_self.attr(app.MARKERS_ADD_MANY, MARKTAG, xx, yy, nn,
                    color_font=opt.COLOR_FONT_OTHER,
                    color_bg=opt.COLOR_BG_OTHER,
                    color_border=opt.COLOR_BRD_OTHER,
                    border_left=opt.BRD_OTHER,
                    border_right=opt.BRD_OTHER,
                    border_up=opt.BRD_OTHER,
                    border_down=opt.BRD_OTHER,
                    )

        if opt.CARET_ALLOW and not is_selection:
            ed_self.attr(app.MARKERS_ADD, MARKTAG, x0, y0, nlen,
                        color_font=opt.COLOR_FONT_CURRENT,
                        color_bg=opt.COLOR_BG_CURRENT,
                        color_border=opt.COLOR_BRD_CURRENT,
                        border_left=opt.BRD_CURRENT,
                        border_right=opt.BRD_CURRENT,
                        border_up=opt.BRD_CURRENT,
                        border_down=opt.BRD_CURRENT,
                        )

        app.msg_status('Matches hilited: {}'.format(ncount))


    def select_all(self):
        res = _process_occurrences(ed)
        if not res:
            return

        items, text, is_selection, x0, y0 = res

        ncount = len(items)
        nlen = len(text)

        for item in items:
            ed.set_caret(item[0] + nlen, item[1], item[0], item[1], app.CARET_ADD)

        app.msg_status('Matches selected: {}'.format(ncount))


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


def _process_occurrences(ed):
    lex = ed.get_prop(app.PROP_LEXER_FILE)
    if not lex:
        lex = '-'
    if not is_lexer_ok(lex):
        return

    ed.attr(app.MARKERS_DELETE_BY_TAG, MARKTAG)

    if ed.get_line_count()>opt.MAX_LINES:
        return

    current_text = _get_current_text(ed)
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

    carets = ed.get_carets()
    if len(carets) != 1: return

    x0, y0, x1, y1 = caret_pos
    if x0 > x1: x0, x1 = x1, x0

    items = find_all_occurrences(ed, text, case_sensitive, whole_words, words_only)

    if not items or (len(items) == 1 and items[0] == (x0, y1)):
        app.msg_status('')
        return

    return items, text, is_selection, x0, y0
