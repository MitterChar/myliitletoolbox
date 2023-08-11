import tkinter as tk
import pickle
import time

# File to save the window's position and size data
DATA_FILE = "window_data.pkl"

def save_window_data(x, y, w, h):
    with open(DATA_FILE, 'wb') as f:
        pickle.dump((x, y, w, h), f)

def load_window_data():
    try:
        with open(DATA_FILE, 'rb') as f:
            return pickle.load(f)
    except (FileNotFoundError, pickle.UnpicklingError):
        return None

def create_window():
    window = tk.Tk()
    window.overrideredirect(True)

    
    data = load_window_data()
    if data:
        x, y, w, h = data
        window.geometry(f"{w}x{h}+{x}+{y}")
    else:
        window.geometry("1000x600+100+50")

    window.configure(background='#FFFFFF')  # Default to white
    window.attributes('-topmost', 1)

    sensitivity = 20  
    double_click_timer = None
    minimized = False
    colors = ['#FFFFFF', '#202020', '#808080']  # RGB codes for the colors
    color_index = 0  # Start with the default color
    
    def on_press(event):

        x, y, w, h = window.winfo_x(), window.winfo_y(), window.winfo_width(), window.winfo_height()
        window.drag_data = {"x": event.x_root, "y": event.y_root}
        
        # Check if click is in the center region
        center_x, center_y = w // 2, h // 2
        if center_x - 25 <= event.x <= center_x + 25 and center_y - 25 <= event.y <= center_y + 25:
            change_color()
            return
        
        # Determine resizing edge based on mouse press location
        if event.x < sensitivity:  # left edge
            window.drag_data["edge"] = "left"
        elif event.x > w - sensitivity:  # right edge
            window.drag_data["edge"] = "right"
        else:
            window.drag_data["edge"] = None

        if event.y < sensitivity:  # top edge
            if window.drag_data["edge"]:  # corner
                window.drag_data["edge"] += "_top"
            else:
                window.drag_data["edge"] = "top"
        elif event.y > h - sensitivity:  # bottom edge
            if window.drag_data["edge"]:  # corner
                window.drag_data["edge"] += "_bottom"
            else:
                window.drag_data["edge"] = "bottom"
        else:
            if not window.drag_data["edge"]:  # not on any edge
                window.drag_data["action"] = "move"
                return

        window.drag_data["action"] = "resize"

    def on_release(event):
        release_time = time.time()

        window.drag_data = None

    def on_motion(event):
        if not window.drag_data:
            return

        dx = event.x_root - window.drag_data["x"]
        dy = event.y_root - window.drag_data["y"]

        x, y, w, h = window.winfo_x(), window.winfo_y(), window.winfo_width(), window.winfo_height()

        if window.drag_data["action"] == "resize":
            # Check for corner switch while dragging
            if "left" in window.drag_data["edge"] and event.y > h - sensitivity:
                window.drag_data["edge"] = "left_bottom"
            elif "left" in window.drag_data["edge"] and event.y < sensitivity:
                window.drag_data["edge"] = "left_top"
                
            elif "right" in window.drag_data["edge"] and event.y > h - sensitivity:
                window.drag_data["edge"] = "right_bottom"
            elif "right" in window.drag_data["edge"] and event.y < sensitivity:
                window.drag_data["edge"] = "right_top"
                
            elif "top" in window.drag_data["edge"] and event.x < sensitivity:
                window.drag_data["edge"] = "left_top"
            elif "top" in window.drag_data["edge"] and event.x > w - sensitivity:
                window.drag_data["edge"] = "right_top"
                
            elif "bottom" in window.drag_data["edge"] and event.x < sensitivity:
                window.drag_data["edge"] = "left_bottom"
            elif "bottom" in window.drag_data["edge"] and event.x > w - sensitivity:
                window.drag_data["edge"] = "right_bottom"

            # Adjust dimensions based on the dragged edge or corner
            if "left" in window.drag_data["edge"]:
                x += dx
                w -= dx
            elif "right" in window.drag_data["edge"]:
                w += dx
            if "top" in window.drag_data["edge"]:
                y += dy
                h -= dy
            elif "bottom" in window.drag_data["edge"]:
                h += dy

            window.geometry(f"{w}x{h}+{x}+{y}")

        elif window.drag_data["action"] == "move":
            x += dx
            y += dy
            window.geometry(f"{w}x{h}+{x}+{y}")

        window.drag_data["x"] = event.x_root
        window.drag_data["y"] = event.y_root


    def close_window(event=None):
        window.destroy()

    def minimize_window(event=None):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_position = screen_width - 100
        y_position = screen_height - 100
        window.geometry(f"100x100+{x_position}+{y_position}")

    def on_double_click(event):
        nonlocal double_click_timer
        if double_click_timer:
            window.after_cancel(double_click_timer)
            double_click_timer = None
        double_click_timer = window.after(300, minimize_window)  # 300ms delay

    def on_triple_click(event):
        nonlocal double_click_timer
        if double_click_timer:
            window.after_cancel(double_click_timer)
            double_click_timer = None
        close_window()

    def close_window(event=None):
        x, y, w, h = parse_geometry(window.geometry())
        save_window_data(x, y, w, h)
        window.destroy()

    def minimize_window(event=None):
        nonlocal minimized
        if not minimized:
            x, y, w, h = parse_geometry(window.geometry())
            save_window_data(x, y, w, h)
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x_position = screen_width - 105  # Shifted 10 pixels to the left
            y_position = screen_height - 85  # Shifted 10 pixels upwards
            window.geometry(f"100x40+{x_position}+{y_position}")
            minimized = True
        else:
            data = load_window_data()
            if data:
                x, y, w, h = data
                window.geometry(f"{w}x{h}+{x}+{y}")
            else:
                window.geometry("1000x600+100+50")
            minimized = False


    def parse_geometry(geometry):
        w, h, x, y = map(int, geometry.replace("x", "+").split("+"))
        return x, y, w, h
    

    def change_color(event=None):
        nonlocal color_index
        color_index += 1
        if color_index >= len(colors):
            color_index = 0
        window.configure(background=colors[color_index])


    window.bind("<Button-1>", change_color)
    window.bind("<ButtonPress-1>", on_press)
    window.bind("<ButtonRelease-1>", on_release)
    window.bind("<B1-Motion>", on_motion)
    window.bind("<Double-Button-1>", on_double_click)
    window.bind("<Triple-Button-1>", on_triple_click)

    window.mainloop()

create_window()