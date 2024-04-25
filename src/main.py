import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET

def on_button_press(event):
    global start_x, start_y, current_drawn, selected
    start_x, start_y = event.x, event.y
    if drawing_tool == "move" or drawing_tool == "resize":
        selected = canvas.find_closest(event.x, event.y)[0]  # Get the id of the closest object
        canvas.tag_raise(selected)  # Bring the object to the front
        if drawing_tool == "resize":
            current_drawn = selected
    elif drawing_tool in ["rectangle", "circle", "line"]:
        if drawing_tool == "rectangle":
            current_drawn = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='black', fill='red')
        elif drawing_tool == "circle":
            current_drawn = canvas.create_oval(start_x, start_y, start_x, start_y, outline='black', fill='blue')
        elif drawing_tool == "line":
            current_drawn = canvas.create_line(start_x, start_y, start_x, start_y, fill='green')

def on_button_motion(event):
    global start_x, start_y, current_drawn, selected
    if drawing_tool == "move" and selected:
        dx, dy = event.x - start_x, event.y - start_y
        canvas.move(selected, dx, dy)
        start_x, start_y = event.x, event.y
    elif drawing_tool in ["resize", "rectangle", "circle", "line"]:
        update_shape(event)
    elif drawing_tool == "free":
        canvas.create_line(start_x, start_y, event.x, event.y, fill='black', smooth=True, capstyle=tk.ROUND)
        start_x, start_y = event.x, event.y

def update_shape(event):
    global current_drawn
    if current_drawn and (drawing_tool in ["rectangle", "resize"]):
        if (event.state & 0x0001):  # Check if Shift is pressed
            side = max(abs(event.x - start_x), abs(event.y - start_y))
            canvas.coords(current_drawn, start_x, start_y, start_x + side * (1 if event.x > start_x else -1), start_y + side * (1 if event.y > start_y else -1))
        else:
            canvas.coords(current_drawn, start_x, start_y, event.x, event.y)
    elif current_drawn and (drawing_tool in ["circle", "resize"]):
        if (event.state & 0x0001):  # Check if Shift is pressed
            radius = max(abs(event.x - start_x), abs(event.y - start_y))
            canvas.coords(current_drawn, start_x - radius, start_y - radius, start_x + radius, start_y + radius)
        else:
            dx = event.x - start_x
            dy = event.y - start_y
            radius = (dx**2 + dy**2)**0.5
            canvas.coords(current_drawn, start_x - radius, start_y - radius, start_x + radius, start_y + radius)
    elif current_drawn and drawing_tool == "line":
        canvas.coords(current_drawn, start_x, start_y, event.x, event.y)

def on_button_release(event):
    global current_drawn, selected
    if current_drawn:
        update_shape(event)
        current_drawn = None
    selected = None  # Deselect any object

def select_tool(tool):
    global drawing_tool, selected, current_drawn
    drawing_tool = tool
    selected = None
    current_drawn = None  # Reset any ongoing drawing operation

def reset_canvas():
    if messagebox.askokcancel("Zurücksetzen bestätigen", "Möchten Sie wirklich die Zeichenfläche zurücksetzen?"):
        canvas.delete("all")

def save_as_svg():
    svg_root = ET.Element("svg", width=str(canvas.winfo_width()), height=str(canvas.winfo_height()), xmlns="http://www.w3.org/2000/svg")
    for item in canvas.find_all():
        coords = canvas.coords(item)
        options = canvas.itemconfig(item)
        if canvas.type(item) == "rectangle":
            ET.SubElement(svg_root, "rect", x=str(coords[0]), y=str(coords[1]), width=str(coords[2]-coords[0]), height=str(coords[3]-coords[1]), fill=options['fill'][-1])
        elif canvas.type(item) == "oval":
            rx = (coords[2] - coords[0]) / 2
            ry = (coords[3] - coords[1]) / 2
            cx = coords[0] + rx
            cy = coords[1] + ry
            ET.SubElement(svg_root, "ellipse", cx=str(cx), cy=str(cy), rx=str(rx), ry=str(ry), fill=options['fill'][-1])
        elif canvas.type(item) == "line":
            ET.SubElement(svg_root, "line", x1=str(coords[0]), y1=str(coords[1]), x2=str(coords[2]), y2=str(coords[3]), stroke=options['fill'][-1])

    tree = ET.ElementTree(svg_root)
    filename = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG Files", "*.svg")])
    if filename:
        tree.write(filename)

def add_menu(root):
    menu_bar = tk.Menu(root)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Speichern als SVG", command=save_as_svg)
    menu_bar.add_cascade(label="Datei", menu=file_menu)
    root.config(menu=menu_bar)

def main():
    global canvas, drawing_tool, current_drawn, selected
    drawing_tool = None
    current_drawn = None
    selected = None

    root = tk.Tk()
    root.title("SVG Editor")
    add_menu(root)

    # Toolbar auf der linken Seite des Fensters
    toolbar = tk.Frame(root, bg="grey")
    toolbar.pack(side="left", fill="y")

    # Bilder laden
    rect_image = tk.PhotoImage(file="icons/rectangle.png").subsample(12)
    circle_image = tk.PhotoImage(file="icons/circle.png").subsample(12)
    line_image = tk.PhotoImage(file="icons/line.png").subsample(12)
    free_image = tk.PhotoImage(file="icons/free.png").subsample(12)
    move_image = tk.PhotoImage(file="icons/move.png").subsample(12)
    resize_image = tk.PhotoImage(file="icons/resize.png").subsample(12)
    reset_image = tk.PhotoImage(file="icons/reset.png").subsample(12)

    # Buttons mit Bildern erstellen
    rect_button = tk.Button(toolbar, image=rect_image, command=lambda: select_tool("rectangle"))
    rect_button.pack(side="top", fill="x")

    circle_button = tk.Button(toolbar, image=circle_image, command=lambda: select_tool("circle"))
    circle_button.pack(side="top", fill="x")

    line_button = tk.Button(toolbar, image=line_image, command=lambda: select_tool("line"))
    line_button.pack(side="top", fill="x")

    free_button = tk.Button(toolbar, image=free_image, command=lambda: select_tool("free"))
    free_button.pack(side="top", fill="x")

    move_button = tk.Button(toolbar, image=move_image, command=lambda: select_tool("move"))
    move_button.pack(side="top", fill="x")

    resize_button = tk.Button(toolbar, image=resize_image, command=lambda: select_tool("resize"))
    resize_button.pack(side="top", fill="x")

    reset_button = tk.Button(toolbar, image=reset_image, command=reset_canvas)
    reset_button.pack(side="top", fill="x")

    canvas = tk.Canvas(root, width=800, height=600, bg='white')
    canvas.pack(fill=tk.BOTH, expand=True)

    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_button_motion)
    canvas.bind("<ButtonRelease-1>", on_button_release)

    root.mainloop()

if __name__ == "__main__":
    main()
