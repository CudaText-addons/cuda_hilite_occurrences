#import time
import datetime
import re
from enum import Enum

import cudatext as app
from cudatext import ed
import cudax_lib as appx
from . import opt

from cudax_lib import get_translation
_ = get_translation(__file__)  # I18N


NONWORD_DEF = '''-+*=/\\()[]{}<>"'.,:;~?!@#$%^&|`…'''
NONWORD = {}
MARKTAG = 101 # we need fixed value # app.app_proc(app.PROC_GET_UNIQUE_TAG, '')
fn_config = 'cuda_hilite_occurrences.json'

# Save current occurrences result, if user execute select_all command, Cud does
# not need to recall app.EDACTION_FIND_ALL function
occurrences = ()

# Control if the select_all command is being executed. Avoid to run the on_caret
# event
on_event_disabled = False
disable_status_msgs = False
time_start = 0
hili_full_doc = True
in_on_caret = False

class Moves(Enum):
    MOVE_FIRST = 0
    MOVE_LAST  = 1
    MOVE_PREV  = 2
    MOVE_NEXT  = 3


def log(s):
    # Change conditional to True to log messages in a Debug process
    if False:
        now = datetime.datetime.now()
        print(now.strftime("%H:%M:%S ") + s)
    pass


def get_opt(path, val):
    return appx.get_opt(path, val, user_json=fn_config)


def get_line(ed_self, n):
    # limit max length of line
    return ed_self.get_text_line(n, opt.MAX_LINE_LEN)

def get_area_lines(ed_self, x, y, w, h):
    lines = []
    for i in range(h):
        line = ed_self.get_text_substr(x,y+i, x+w,y+i)
        lines.append(line)
    return lines


def do_load_ops():
    meta_def    = lambda op: [it['def'] for it in opt.META_OPT if it['opt']==op][0]

    opt.MIN_LEN                = get_opt('min_len',             meta_def('min_len'))
    opt.MAX_LINES              = get_opt('max_lines',           meta_def('max_lines'))
    opt.MAX_LINE_LEN           = get_opt('max_line_len',        meta_def('max_line_len'))
    opt.MAX_TIME               = get_opt('max_time',            meta_def('max_time'))
    opt.AVG_LEN                = get_opt('avg_len',             meta_def('avg_len'))

    opt.SEL_ALLOW              = get_opt('sel_allow',           meta_def('sel_allow'))
    opt.SEL_ALLOW_WHITE_SPACE  = get_opt('sel_allow_spaces',    meta_def('sel_allow_spaces'))
    opt.SEL_CASE_SENSITIVE     = get_opt('sel_case_sens',       meta_def('sel_case_sens'))
    opt.SEL_WORDS_ONLY         = get_opt('sel_words_only',      meta_def('sel_words_only'))
    opt.SEL_WHOLE_WORDS        = get_opt('sel_whole_words',     meta_def('sel_whole_words'))

    opt.MARK_IGNORE_MIN_LEN    = get_opt('mark_ignore_min_len', meta_def('mark_ignore_min_len'))
    opt.VISIBLE_FALLBACK       = get_opt('visible_fallback',    meta_def('visible_fallback'))

    opt.CARET_ALLOW            = get_opt('caret_allow',         meta_def('caret_allow'))
    opt.CARET_CASE_SENSITIVE   = get_opt('caret_case_sens',     meta_def('caret_case_sens'))
    opt.CARET_WHOLE_WORDS      = get_opt('caret_whole_words',   meta_def('caret_whole_words'))

    opt.LEXERS_ALLOWED         = get_opt('lexers_allowed',      '')
    opt.LEXERS_DISABLED        = get_opt('lexers_disabled',     '')

    opt.THEME_CURRENT          = get_opt('theme_item_current',  meta_def('theme_item_current'))
    opt.THEME_OTHER            = get_opt('theme_item_other',    meta_def('theme_item_other'))
    do_update_colors()

    # subscribe to events
    events = 'on_caret,on_state,on_change_slow'
    if opt.VISIBLE_FALLBACK:
        events += ',on_scroll'
    ev_str = 'cuda_hilite_occurrences;{};;'.format(events)
    app.app_proc(app.PROC_SET_EVENTS, ev_str)


def do_update_colors():

    theme = app.app_proc(app.PROC_THEME_SYNTAX_DICT_GET, '')
    item_cur = theme.get(opt.THEME_CURRENT)
    item_oth = theme.get(opt.THEME_OTHER)

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
        log('Incorrect theme item(s) "%s", "%s" in "%s"' % (opt.THEME_CURRENT,
                                                            opt.THEME_OTHER,
                                                            fn_config))
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


def get_hi_full_doc(ed):
    '''
    Gets True if document needs FULL highlighting; ie document is not 'too big'.
    '''
    line_cnt = ed.get_line_count()
    if line_cnt > opt.MAX_LINES:
        #print('partial: from max_lines')
        return False
    if ed.get_prop(app.PROP_SCROLL_HORZ_INFO)['max'] > opt.MAX_COLUMNS:
        #print('partial: from scroll_horz')
        return False

    if hasattr(ed, 'get_char_count'): # support old CudaText releases
        char_cnt = ed.get_char_count(0x7fffFFFF, opt.MAX_TIME)
        if char_cnt < 0: # -2 means 'time limit reached'
            #print('partial: char_cnt time limit')
            return False
        if char_cnt > opt.AVG_LEN * line_cnt:
            #print('partial: too long lines > avg_len')
            return False

    return True


class Command:
    def __init__(self):
        do_load_ops()

    @staticmethod
    def config():

        try:
            import cuda_options_editor as op_ed
        except ImportError:
            import cuda_prefs as op_ed

        subset = ''  # Key for isolated storage on plugin settings
        title = _('Highlight Occurrences options')
        how = {'hide_lex_fil': True, 'stor_json': fn_config}
        op_ed.OptEdD(
            path_keys_info=opt.META_OPT,
            subset=subset,
            how=how
        ).show(title)
        do_load_ops()

    def on_state(self, ed_self, state):

        if state == app.APPSTATE_THEME_SYNTAX:
            do_update_colors()
            self.on_caret(ed)

    def work(self, ed_self):
        #global time_start
        #time_start = time.time()

        res = process_ocurrences(ed_self)
        if not res:
            app.msg_status('')
            return

        paint_occurrences(ed_self, res)

    def on_caret(self, ed_self):
        global occurrences
        global in_on_caret

        if on_event_disabled:
            return
        if in_on_caret:
            return
        in_on_caret = True

        if not opt.CARET_ALLOW:
            abort = False
            if opt.SEL_ALLOW:
                carets = ed.get_carets()
                if len(carets) != 1  or  carets[0][3] < 0:   # invalid/no selection
                    ed_self.attr(app.MARKERS_DELETE_BY_TAG, MARKTAG)
                    abort = True
            else:
                abort = True

            if abort:
                occurrences = ()
                in_on_caret = False
                return

        self.work(ed_self)
        in_on_caret = False

    def on_change_slow(self, ed_self):
        self.work(ed_self)

    def on_scroll(self, ed_self):
        global occurrences
        global disable_status_msgs

        occurrences = ()

        try:
            disable_status_msgs = True
            self.work(ed_self)
        finally:
            disable_status_msgs = False

    def select_all(self):
        global on_event_disabled

        res = process_ocurrences(ed, sel_occurrences=True)
        if not res:
            return

        items, text, is_selection, x0, y0 = res

        ncount = len(items)
        nlen = len(text)

        on_event_disabled = True
        # Cleaning previous carets if exists
        ed.set_caret(x0, y0, -1, -1)
        for item in items:
            ed.set_caret(item[0] + nlen, item[1], item[0], item[1], app.CARET_ADD)

        app.msg_status(_('Matches selected: {}').format(ncount))
        on_event_disabled = False

    def move_prev(self):
        move_caret(Moves.MOVE_PREV)

    def move_next(self):
        move_caret(Moves.MOVE_NEXT)

    def move_first(self):
        move_caret(Moves.MOVE_FIRST)

    def move_last(self):
        move_caret(Moves.MOVE_LAST)


def paint_occurrences(ed_self, occurrences):
    items, text, is_selection, x0, y0 = occurrences

    ncount = len(items)
    nlen = len(text)

    idx = 0

    # First item
    if items[0] == (x0, y0):
        idx = 1

    # Last item
    if items[ncount - 1] == (x0, y0):
        idx = ncount

    # Middle item
    if idx == 0:
        idx = next((i for i in range(1, ncount, 1)
                    if items[i - 1] == (x0, y0)), 0)

    items = [i for i in items if i != (x0, y0)]
    xx = [i[0] for i in items]
    yy = [i[1] for i in items]
    nn = [nlen] * len(items)

    theme = app.app_proc(app.PROC_THEME_SYNTAX_DICT_GET, '')
    item_cur = theme.get(opt.THEME_CURRENT)
    item_oth = theme.get(opt.THEME_OTHER)
    styles_cur = item_cur['styles']
    styles_oth = item_oth['styles']

    def b2i(b):
        return 1 if b else 0

    ed_self.attr(app.MARKERS_ADD_MANY, MARKTAG, xx, yy, nn,
                 color_font=item_oth['color_font'],
                 color_bg=item_oth['color_back'],
                 color_border=item_oth['color_border'],
                 font_bold=b2i('b' in styles_oth),
                 font_italic=b2i('i' in styles_oth),
                 font_strikeout=b2i('s' in styles_oth),
                 border_left=item_oth['border_left'],
                 border_right=item_oth['border_right'],
                 border_up=item_oth['border_top'],
                 border_down=item_oth['border_bottom']
                 )

    #if opt.CARET_ALLOW and not is_selection:
    ed_self.attr(app.MARKERS_ADD, MARKTAG, x0, y0, nlen,
                 color_font=item_cur['color_font'],
                 color_bg=item_cur['color_back'],
                 color_border=item_cur['color_border'],
                 font_bold=b2i('b' in styles_cur),
                 font_italic=b2i('i' in styles_cur),
                 font_strikeout=b2i('s' in styles_cur),
                 border_left=item_cur['border_left'],
                 border_right=item_cur['border_right'],
                 border_up=item_cur['border_top'],
                 border_down=item_cur['border_bottom']
                 )

    #tick = round((time.time() - time_start) * 1000)
    if not disable_status_msgs:
        if hili_full_doc:
            #app.msg_status(_('Matches highlighted:')+' {}/{} ({}ms)'.format(idx, ncount, tick))
            app.msg_status(_('Matches highlighted:')+' {}/{}'.format(idx, ncount))
        else:
            app.msg_status(_('Matches highlighted:')+' {}/{} '.format(idx, ncount)+_('(partial)'))

def is_word(s, lexer):
    bads = NONWORD.get(lexer)
    if bads is None:
        bads = appx.get_opt('nonword_chars', NONWORD_DEF, appx.CONFIG_LEV_ALL, lexer=lexer)
        NONWORD[lexer] = bads

    for ch in s:
        if ch in ' \t'+bads:
            return False
    return True


def find_all_occurrences(ed_self, text, case_sensitive, whole_words):
    """
    Finding matches to highlight
    """

    opts = ('c' if case_sensitive else '') + ('w' if whole_words else '')
    log("Calling ed_self.action: EDACTION_FIND_ALL")
    res = ed_self.action(app.EDACTION_FIND_ALL, text, opts, opt.MAX_LINE_LEN)
    res = [r[:2] for r in res]
    return res

def find_visible_occurrences(ed_self: app.Editor, text, case_sensitive, whole_words):
    '''
    Find matches only in the visible part of the screen.
    In visible part of huge lines.
    '''

    global in_on_caret
    in_on_caret = True

    text_len = len(text)
    wrap_type = ed_self.get_prop(app.PROP_WRAP)
    line_top = ed_self.get_prop(app.PROP_LINE_TOP)
    line_btm = ed_self.get_prop(app.PROP_LINE_BOTTOM)
    scroll_horz = ed_self.get_prop(app.PROP_SCROLL_HORZ_INFO)
    scroll_x = max(0, scroll_horz['pos'] - text_len)
    scroll_w = scroll_horz['page']
    old_carets = ed_self.get_carets()
    opts = ('c' if case_sensitive else '') + ('w' if whole_words else '') + 's' # search in selections only

    if wrap_type == app.WRAP_OFF:
        res = []
        for y in range(line_top, line_btm+1):
            nlen = ed_self.get_line_len(y)
            x_from = min(nlen, scroll_x)
            x_to = min(nlen, scroll_x + scroll_w + text_len*2 + 1)
            if x_from==x_to:
                continue
            ed_self.set_caret(
                x_from,
                y,
                x_to,
                y,
                app.CARET_SET_ONE,
                options=app.CARET_OPTION_NO_SCROLL
                )
            #print("wrap off; caret: {}, text: '{}', opts: '{}'".format(ed_self.get_carets(), text, opts))
            # API cannot find in multi-selections, so find in each selection
            res += ed_self.action(app.EDACTION_FIND_ALL, text, opts, 0x7FFFFFFF)
                
    else: # wrap=on
        ed_self.set_caret(
            0,
            line_top,
            ed_self.get_line_len(line_btm),
            line_btm,
            app.CARET_SET_ONE,
            options=app.CARET_OPTION_NO_SCROLL
            )
        #print("wrap on; caret: {}, text: '{}', opts: '{}'".format(ed_self.get_carets(), text, opts))
        res = ed_self.action(app.EDACTION_FIND_ALL, text, opts, 0x7FFFFFFF)
    #end if wrap

    res = [r[:2] for r in res]
    #print('res:', res)

    # restore old caret(s)
    if len(old_carets)==1:
        x, y, x2, y2 = old_carets[0]
        ed_self.set_caret(x, y, x2, y2, options=app.CARET_OPTION_NO_SCROLL)
    else:
        ed_self.set_caret(0, 0, -1, -1, app.CARET_DELETE_ALL)
        for x, y, x2, y2 in old_carets:
            ed_self.set_caret(x, y, x2, y2, app.CARET_ADD, options=app.CARET_OPTION_NO_SCROLL)

    in_on_caret = False
    return res


def get_word_under_caret(ed_self):
    """
    Gets a tuple (word_under_caret, (x1, y1, x2, y2)) containing the word under
    the current caret.
    """

    lex = ed_self.get_prop(app.PROP_LEXER_CARET)

    carets = ed_self.get_carets()

    # In this point the "one caret" rule is valid, so x2 and y2 is equal to -1
    # and there is no a selection
    x1, y1 = carets[0][:2]

    current_line = get_line(ed_self, y1)
    # if len(current_line) > opt.MAX_LINE_LEN: return

    n_x1 = n_x2 = x1

    if current_line:
        if x1 > 0 and is_word(current_line[x1 - 1], lex):
            n_x1 = next((i for i in range(x1 - 1, -1, -1)
                         if not is_word(current_line[i], lex)), -1) + 1

        if x1 < len(current_line) and is_word(current_line[x1], lex):
            n_x2 = next((i for i in range(x1 + 1, len(current_line))
                         if not is_word(current_line[i], lex)),
                        len(current_line))

    else: return

    if n_x1 == n_x2:
        return

    word_under_caret = current_line[n_x1: n_x2]

    return word_under_caret, (n_x1, y1, n_x2, y1)


def _get_current_text(ed_self):
    caret_pos = ed_self.get_carets()[0]

    x1, y1, x2, y2 = caret_pos

    is_selection = y2 >= 0

    current_text = ''

    if is_selection:
        if opt.SEL_ALLOW:
            # Sorting caret's values
            if (y1, x1) > (y2, x2):
                x1, x2 = x2, x1
                y1, y2 = y2, y1
                caret_pos = (x1, y1, x2, y2)

            # After sorting y2 always will be greater or equal to y1
            # No multi-line allowed
            if (y2 - y1) > 0: return

            current_text = ed_self.get_text_sel()
        else:
            return
    else:
        if not opt.CARET_ALLOW:
            return
        # Sometimes caret can be beyond text end
        temp = get_line(ed_self, y1)
        if (temp is None) or (len(temp) < x1): return
        # if len(temp) > opt.MAX_LINE_LEN: return

        temp = get_word_under_caret(ed_self)
        if not temp: return
        current_text, caret_pos = temp

    return current_text, caret_pos, is_selection


def move_caret(mode):
    global occurrences
    global on_event_disabled

    if len(occurrences) == 0:
        if opt.CARET_ALLOW:
            return
        else:
            res = process_ocurrences(ed, sel_occurrences=True)
            if not res:
                return

    items, text, is_selection = occurrences[:3]

    # Current caret
    caret = occurrences[-2:]
    x0, y0 = caret

    item = None

    # Getting the new caret
    if mode in [Moves.MOVE_FIRST]:
        item = items[0]
    elif mode in [Moves.MOVE_LAST]:
        item = items[len(items) - 1]
    elif mode in [Moves.MOVE_PREV]:
        idx = next((i for i in range(len(items) - 1, 0, -1)
                    if items[i] == caret), 0)
        if idx > 0:
            item = items[idx - 1]
    elif mode in [Moves.MOVE_NEXT]:
        idx = next((i for i in range(0, len(items) - 1, 1)
                    if items[i] == caret), len(items) - 1)
        if idx < len(items) - 1:
            item = items[idx + 1]
    else:
        log("Not found option for Move: " + mode.name)
        return

    if not item:
        log("Not found caret position for Move: " + mode.name)
        return

    x0, y0 = item[0], item[1]

    on_event_disabled = True
    occurrences = (items, text, is_selection, x0, y0)
    ed.set_caret(x0, y0, -1, -1)
    ed.focus()

    paint_occurrences(ed, occurrences)

    on_event_disabled = False


def process_ocurrences(ed_self, sel_occurrences=False):
    global occurrences

    ed_self.attr(app.MARKERS_DELETE_BY_TAG, MARKTAG)
    if not disable_status_msgs:
        #app.msg_status('')  # disable this, see https://github.com/Alexey-T/CudaText/issues/4206
        pass

    if sel_occurrences:
        # In this part of the events, occurrences variable must have data.
        # If not, force matches considering no min length selection.
        if len(occurrences) == 0 and (opt.MARK_IGNORE_MIN_LEN or not opt.CARET_ALLOW):
            log("No previous occurrences information")
            res = _get_occurrences(ed_self, sel_occurrences)

            if not res:
                occurrences = ()
                return
            else:
                occurrences = res

        return occurrences

    else:
        # The highlight function on_caret event only works with one caret.
        if len(ed_self.get_carets()) != 1: return

        res = _get_occurrences(ed_self)

        if res is None:
            occurrences = ()
            return
        else:
            occurrences = res

        return occurrences


def _get_occurrences(ed_self, ignore_min_len=False):
    """
    Gets a tuple (items, text, is_selection, x1, y1) containing all the
    occurrences for the selected word or for the word under current caret.
    param: ignore_min_len works only with selections.
    """
    global hili_full_doc
    global occurrences

    lex = ed_self.get_prop(app.PROP_LEXER_FILE)

    if not lex:
        lex = '-'
    if not is_lexer_ok(lex):
        return

    hili_full_doc = get_hi_full_doc(ed_self)
    if not hili_full_doc and not opt.VISIBLE_FALLBACK:
        return

    current_text = _get_current_text(ed_self)
    if not current_text: return

    text, caret_pos, is_selection = current_text

    log('Looking occurrences for text: "' + text + '"')

    if is_selection:
        if not ignore_min_len:
            if not opt.SEL_ALLOW_WHITE_SPACE: text = text.strip()
            if not text: return
            if len(text) < opt.MIN_LEN: return

        case_sensitive = opt.SEL_CASE_SENSITIVE
        words_only     = opt.SEL_WORDS_ONLY
        whole_words    = opt.SEL_WHOLE_WORDS if opt.SEL_WORDS_ONLY else False
    else:
        case_sensitive = opt.CARET_CASE_SENSITIVE
        words_only     = True
        whole_words    = opt.CARET_WHOLE_WORDS

    # Validate if current text is a 'valid word' for current lexer
    if words_only and not is_word(text, lex):
        log("Current text refused because is not a valid word")
        return

    # caret_pos have the information with sorted values
    x1, y1 = caret_pos[:2]

    # Validate if the searching word is the same of the previous occurrences
    if len(occurrences) > 0:
        prev_items = occurrences[0]
        prev_text = occurrences[1]
        if prev_text == text and (x1, y1) in prev_items:
            log("Returning previous occurrences")
            return prev_items, text, is_selection, x1, y1

    if hili_full_doc:
        items = find_all_occurrences(ed_self, text, case_sensitive, whole_words)
    else: # only visible
        items = find_visible_occurrences(ed_self, text, case_sensitive, whole_words)

    if not items or (len(items) == 1 and items[0] == (x1, y1)):
        return

    return items, text, is_selection, x1, y1
