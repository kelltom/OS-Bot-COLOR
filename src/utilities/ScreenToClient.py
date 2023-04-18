from utilities.WindowLocal import Window

window_title = "RuneLite"
def screen_to_window(screen_x: int, screen_y: int) -> tuple:
    global window_title
    padding_top = 26 # replace with desired value
    padding_left = 0 # replace with desired value
    my_window = Window(window_title, padding_top, padding_left)
    window_rectangle = my_window.rectangle()

    # Convert screen coordinates to window coordinates
    window_x = screen_x - window_rectangle.left
    window_y = screen_y - window_rectangle.top

    return (window_x, window_y)
