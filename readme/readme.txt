Plugin for CudaText.
It highlights all occurences of current word (under first caret), or selected text, with background color.

It has config file with many options - call menu item in "Options / Settings-plugins / Highlight Occurences".

- Option "min_len": minimal length of fragments to find.
- Option "max_lines": maximal count of lines in document, for which plugin is active.
- Options "sel_..." allow to activate plugin when selection is changed.
- Options "caret_..." allow to activate plugin when only caret position is changed.
- Option "sel_words_only": allow to handle selection only if it's word.
- Option "sel_whole_words": for selection, find matches only if they are words.
- Option "use_nearest_line_count": if value=0 - only visible part of text is handled, if big value - big part of text (around visible text) is handled. To find matches in entire huge file (not recommended, it's slow), set option to huge value, e.g. 200000.
- Option "lexers_allowed": if not empty, then plugin is active only for mentioned lexers. Comma-separated list. None-lexer must be written as "-".
- Option "lexers_disabled": if not empty, then plugin is disabled for mentioned lexers. Has higher priority than "lexers_allowed".


Authors:
  Alexey (CudaText)
  myCrack (at Github)
License: MIT
