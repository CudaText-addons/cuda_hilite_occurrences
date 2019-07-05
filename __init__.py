import os
import string
import cudatext as app
import cudax_lib as appx
from . import opt
import unicodedata as ud

all_unicode = [chr(i) for i in range(0x10000)]
unicode_letters = ''.join([c for c in all_unicode if ud.category(c) in ('Lu', 'Ll')])

CHARS = string.ascii_letters + string.digits + '_$' + unicode_letters
MARKTAG = 101 #uniq value for all markers plugins
fn_ini = os.path.join(app.app_path(app.APP_DIR_SETTINGS), 'cuda_hilite_occurrences.ini')

def bool_to_str(v): return '1' if v else '0'
def str_to_bool(s): return s=='1'


def get_line(ed, n):
  # limit max length of line
  return ed.get_text_line(n, 500)

def do_load_ops():
  print('Highlight Occurrences: load options')

  opt.MIN_LEN               = int(app.ini_read(fn_ini, 'op', 'min_len', '2'))
  opt.MAX_LINES             = int(app.ini_read(fn_ini, 'op', 'max_lines', '5000'))
  opt.USE_NEAREST_LINE_COUNT = int(app.ini_read(fn_ini, 'op', 'use_nearest_line_count', '10000'))

  opt.SEL_ALLOW             = str_to_bool(app.ini_read(fn_ini, 'op', 'sel_allow', '1'))
  opt.SEL_ALLOW_WHITE_SPACE = str_to_bool(app.ini_read(fn_ini, 'op', 'sel_allow_white_space', '0'))
  opt.SEL_CASE_SENSITIVE    = str_to_bool(app.ini_read(fn_ini, 'op', 'sel_case_sensitive', '0'))
  opt.SEL_WORDS_ONLY        = str_to_bool(app.ini_read(fn_ini, 'op', 'sel_words_only', '0'))
  opt.SEL_WHOLE_WORDS       = str_to_bool(app.ini_read(fn_ini, 'op', 'sel_whole_words', '0'))

  opt.CARET_ALLOW           = str_to_bool(app.ini_read(fn_ini, 'op', 'caret_allow', '1'))
  opt.CARET_CASE_SENSITIVE  = str_to_bool(app.ini_read(fn_ini, 'op', 'caret_case_sensitive', '1'))
  opt.CARET_WHOLE_WORDS     = str_to_bool(app.ini_read(fn_ini, 'op', 'caret_whole_words', '1'))

  opt.COLOR_FONT_OTHER      = appx.html_color_to_int(app.ini_read(fn_ini, 'colors', 'font_other', '#000'))
  opt.COLOR_BG_OTHER        = appx.html_color_to_int(app.ini_read(fn_ini, 'colors', 'bg_other', '#ff0'))
  opt.COLOR_FONT_CURRENT    = appx.html_color_to_int(app.ini_read(fn_ini, 'colors', 'font_current', '#000'))
  opt.COLOR_BG_CURRENT      = appx.html_color_to_int(app.ini_read(fn_ini, 'colors', 'bg_current', '#e4c0e4'))

  opt.LEXERS_ALLOWED = app.ini_read(fn_ini, 'op', 'lexers_allowed', '')
  opt.LEXERS_DISABLED = app.ini_read(fn_ini, 'op', 'lexers_disabled', '')

def do_save_ops():
  app.ini_write(fn_ini, 'op', 'min_len', str(opt.MIN_LEN))
  app.ini_write(fn_ini, 'op', 'max_lines', str(opt.MAX_LINES))
  app.ini_write(fn_ini, 'op', 'use_nearest_line_count', str(opt.USE_NEAREST_LINE_COUNT))

  app.ini_write(fn_ini, 'op', 'sel_allow', bool_to_str(opt.SEL_ALLOW))
  app.ini_write(fn_ini, 'op', 'sel_allow_white_space', bool_to_str(opt.SEL_ALLOW_WHITE_SPACE))
  app.ini_write(fn_ini, 'op', 'sel_case_sensitive', bool_to_str(opt.SEL_CASE_SENSITIVE))
  app.ini_write(fn_ini, 'op', 'sel_words_only', bool_to_str(opt.SEL_WORDS_ONLY))
  app.ini_write(fn_ini, 'op', 'sel_whole_words', bool_to_str(opt.SEL_WHOLE_WORDS))

  app.ini_write(fn_ini, 'op', 'caret_allow', bool_to_str(opt.CARET_ALLOW))
  app.ini_write(fn_ini, 'op', 'caret_case_sensitive', bool_to_str(opt.CARET_CASE_SENSITIVE))
  app.ini_write(fn_ini, 'op', 'caret_whole_words', bool_to_str(opt.CARET_WHOLE_WORDS))

  app.ini_write(fn_ini, 'colors', 'font_other', appx.int_to_html_color(opt.COLOR_FONT_OTHER))
  app.ini_write(fn_ini, 'colors', 'bg_other', appx.int_to_html_color(opt.COLOR_BG_OTHER))
  app.ini_write(fn_ini, 'colors', 'font_current', appx.int_to_html_color(opt.COLOR_FONT_CURRENT))
  app.ini_write(fn_ini, 'colors', 'bg_current', appx.int_to_html_color(opt.COLOR_BG_CURRENT))

  app.ini_write(fn_ini, 'op', 'lexers_allowed', opt.LEXERS_ALLOWED)
  app.ini_write(fn_ini, 'op', 'lexers_disabled', opt.LEXERS_DISABLED)


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
    if fn==fn_ini:
      do_load_ops()

  def config(self):
    do_save_ops()
    if os.path.isfile(fn_ini):
      app.file_open(fn_ini)
    else:
      app.msg_status('Config file not found')


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


def is_word(s):
  for ch in s:
    if not ch in CHARS: return False
  return True


def find_all_occurrences(ed, text, case_sensitive, whole_words, words_only):
  '''
  Finding matches to hilite
  '''
  if words_only and not is_word(text): return

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
        if x > 0 and is_word(line[x - 1]):
          x += text_len + 1
          continue

        next_char = x + text_len
        if next_char < len(line) and is_word(line[next_char]):
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

  x1, y1, x2 = ed.get_carets()[0][:3]
  y2 = y1

  l_char = r_char = ''
  current_line = get_line(ed, y1)
  #if len(current_line) > opt.MAX_LINE_LEN: return

  if current_line:
    x = x1
    if x > 0:                 l_char = current_line[x - 1]
    if x < len(current_line): r_char = current_line[x]

    l_char, r_char = is_word(l_char), is_word(r_char)

    if not (l_char or r_char): return

    if l_char:
      for x1 in range(x - 1, -1, -1):
        if is_word(current_line[x1]): continue
        else: break
      else: x1 = -1
      x1 += 1

    if r_char:
      for x2 in range(x + 1, len(current_line)):
        if is_word(current_line[x2]): continue
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
