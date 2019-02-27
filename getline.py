import cudatext as app

NEW = app.app_api_version() >= '1.0.275'
MAX_LEN = 500

def get_line(ed, n):
    if NEW:
        return ed.get_text_line(n, MAX_LEN)
    else:
        return ed.get_text_line(n)
