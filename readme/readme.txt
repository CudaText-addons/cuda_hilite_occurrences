Plugin for CudaText.
It highlights all occurences of current word (under first caret), or selected text, with custom color.

It has config file with many options - call menu item in "Options / Settings-plugins / Hilite Occurences".

Options "sel_..." are to handle selection.
Options "caret_..." are to handle word under caret, without selection.
Option "sel_words_only": allow to handle selection only if it's word.
Option "sel_whole_words": for selection, find matches only if they are words.
Option "use_nearest_line_count": if value=0 - only visible part of text is handled, if big value - big part of text (around visible text) is handled. To find matches in entire file of e.g. 200K lines, set option to 200000.


Authors:
  Alexey (CudaText)
  myCrack (at Github)
License: MIT
