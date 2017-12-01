def html_color_to_int(s):
    """
    Convert HTML color '#RRGGBB' or '#RGB' to int
    """
    s = s.strip().lstrip('#')
    if len(s)==3:
        s = s[0]*2 + s[1]*2 + s[2]*2
    if len(s)!=6:
        raise Exception('Incorrect color token: '+s)
    s = s[4:6] + s[2:4] + s[0:2]
    color = int(s, 16)
    return color

def int_to_html(n):
    s = '%06x' % n
    r, g, b = s[4:], s[2:4], s[:2]
    return '#'+r+g+b


