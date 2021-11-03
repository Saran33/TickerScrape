
def phi_align(win, win_w, win_h):
    """Aligns a tkinker GUI window in the horizotal centre of screen,
    with top of window vertically aligned to the screen's golden ratio"""

    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()

    x_cordinate = int((screen_w/2) - (win_w/2))
    y_cordinate = int((screen_h*0.382) - (win_h*0.382))

    return win.geometry("{}x{}+{}+{}".format(win_w, win_h, x_cordinate, y_cordinate))


def centre_window(win, win_w, win_h):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x_coordinate = (screen_width/2)-(win_w/2)
    y_coordinate = (screen_height/2)-(win_h/2)
    return win.geometry("%dx%d+%d+%d" %(win_w,win_h,x_coordinate,y_coordinate))