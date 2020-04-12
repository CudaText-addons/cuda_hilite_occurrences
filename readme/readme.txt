Plugin for CudaText.
Highlights all occurrences of current word (under caret) or selected text with background color.
The highlighted words have the option to be marked with carets.

To set shortcuts to options use F9 functionality in Command palette (Ctrl+Shift+P)
------------------------------

Use commands in "Plugins / Highlight Occurrences" menu:

	- "Move to first occurrence"    : Move the cursor/caret to the first highlighted occurrence.
	- "Move to last occurrence"     : Move the cursor/caret to the last highlighted occurrence.
	- "Move to previous occurrence" : Move the cursor/caret to the previous highlighted occurrence.
	- "Move to next occurrence"     : Move the cursor/caret to the next highlighted occurrence.
	- "Select all occurrences"      : Selects (Marks with carets) to the highlighted occurrences.

------------------------------

Plugin have additional options in "Options / Settings-plugins / Highlight Occurrences".

Options:
    - "min_len"            : (def=2)           : Minimal length of fragment to handle
    - "max_lines"          : (def=5000)        : Maximal number of lines in document (plugin will disable highlight functionality)
    - "max_line_length"    : (def=500)         : Maximal length of lines, which will be handled by plugin (plugin will skip longer lines)
    - "nearest_count"      : (def=10000)       : (Deprecated) If value=0: only visible part of text is handled, If value>0: specified count of lines, around caret
    - "sel_allow"          : (def=True)        : Plugin handles current selection (on selection changing)
    - "sel_allow_spaces"   : (def=False)       : Plugin allows whitespace in selection, otherwise trim it
    - "sel_case_sens"      : (def=False)       : Search for selection is case-sensitive
    - "sel_words_only"     : (def=False)       : Plugin handles selection only when it is whole word
    - "sel_whole_words"    : (def=False)       : Search for selection finds whole words only
    - "sel_ignore_min_len" : (def=False)       : Mark occurrences of selected text ignores 'min_len' option. Related to "Plugins / Highlight Occurrences / Select all occurrences" option
    - "caret_allow"        : (def=True)        : Plugin handles word under caret (on caret moving)
    - "caret_case_sens"    : (def=True)        : Search for word under caret is case-sensitive
    - "caret_whole_words"  : (def=True)        : Search for word under caret finds whole words only
    - "theme_item_current" : (def="BracketBG") : Element of syntax-theme, which color is used for word under caret
    - "theme_item_other"   : (def="BracketBG") : Element of syntax-theme, which color is used for other found matches
    - "lexers_allowed"     : (def="")          : If not empty, plugin is active only for mentioned lexers. Comma-separated list, None-lexer must be written as '-'
    - "lexers_disabled"    : (def="")          : If not empty, plugin is disabled for mentioned lexers. Comma-separated list, Has higher priority than option 'lexers_allowed'.

Authors:
  Alexey Torgashin (CudaText)
  @myCrack (at Github)
  @Jairo-Martinez (at Github) 
License: MIT
