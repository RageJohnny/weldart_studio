import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET

class SVGEditor:
    def __init__(self):
        self.drawing_tool = None
        self.current_drawn = None
        self.selected = None
        self.line_thickness = 1
        self.undo_stack = []
        self.redo_stack = []

        self.root = tk.Tk()
        self.root.title("WELDART Studio")

        self.root.iconbitmap('icons/logo.ico')  # Ersetzen Sie 'pfad_zum_icon.ico' mit dem Pfad zu Ihrer Icon-Datei

        self.add_menu()

        # Toolbar auf der linken Seite des Fensters
        self.toolbar = tk.Frame(self.root, bg="lightgrey")
        self.toolbar.pack(side="left", fill="y")

        # Bilder laden
        self.rect_image = tk.PhotoImage(file="icons/rectangle.png").subsample(12)
        self.circle_image = tk.PhotoImage(file="icons/circle.png").subsample(12)
        self.line_image = tk.PhotoImage(file="icons/line.png").subsample(12)
        self.free_image = tk.PhotoImage(file="icons/free.png").subsample(12)
        self.move_image = tk.PhotoImage(file="icons/move.png").subsample(12)
        self.resize_image = tk.PhotoImage(file="icons/resize.png").subsample(12)
        self.reset_image = tk.PhotoImage(file="icons/reset.png").subsample(12)
        self.select_image = tk.PhotoImage(file="icons/select.png").subsample(12)

        # Buttons mit Bildern erstellen
        self.rect_button = tk.Button(self.toolbar, image=self.rect_image, command=lambda: self.select_tool("rectangle"))
        self.rect_button.pack(side="top", fill="x")

        self.circle_button = tk.Button(self.toolbar, image=self.circle_image, command=lambda: self.select_tool("circle"))
        self.circle_button.pack(side="top", fill="x")

        self.line_button = tk.Button(self.toolbar, image=self.line_image, command=lambda: self.select_tool("line"))
        self.line_button.pack(side="top", fill="x")

        self.free_button = tk.Button(self.toolbar, image=self.free_image, command=lambda: self.select_tool("free"))
        self.free_button.pack(side="top", fill="x")

        self.move_button = tk.Button(self.toolbar, image=self.move_image, command=lambda: self.select_tool("move"))
        self.move_button.pack(side="top", fill="x")

        self.resize_button = tk.Button(self.toolbar, image=self.resize_image, command=lambda: self.select_tool("resize"))
        self.resize_button.pack(side="top", fill="x")

        self.reset_button = tk.Button(self.toolbar, image=self.reset_image, command=self.reset_canvas)
        self.reset_button.pack(side="top", fill="x")

        # Line thickness input
        self.line_thickness_frame = tk.Frame(self.root, bg="lightgrey")

        ttk.Label(self.line_thickness_frame, text="Linienstärke:").pack(pady=5)
        self.line_thickness_var = tk.StringVar(value=str(self.line_thickness))
        self.line_thickness_entry = ttk.Entry(self.line_thickness_frame, textvariable=self.line_thickness_var, state="disabled")
        self.line_thickness_entry.pack(pady=5)

        self.line_thickness_button = ttk.Button(self.line_thickness_frame, text="OK", command=self.set_line_thickness)
        self.line_thickness_button.pack(pady=5)

        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='white')
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_button_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def add_menu(self):
        self.menu_bar = tk.Menu(self.root)

        # Datei Reiter
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Speichern als SVG", command=self.save_as_svg)
        self.menu_bar.add_cascade(label="Datei", menu=file_menu)

        # About Reiter
        about_menu = tk.Menu(self.menu_bar, tearoff=0)
        about_menu.add_command(label="Über", command=self.show_about)
        self.menu_bar.add_cascade(label="Über", menu=about_menu)

        self.root.config(menu=self.menu_bar)

    def show_about(self):
        messagebox.showinfo("Über", "Erstellt von Johannes Georg Larcher")

    def on_button_press(self, event):
        self.undo_stack.append(self.canvas.find_all())  # Speichere den aktuellen Zustand vor der Änderung
        self.redo_stack = []  # Lösche den Redo-Stack

        self.start_x, self.start_y = event.x, event.y
        if self.drawing_tool == "move" or self.drawing_tool == "resize":
            self.selected = self.canvas.find_closest(event.x, event.y)[0]  # Get the id of the closest object
            self.canvas.tag_raise(self.selected)  # Bring the object to the front
            if self.drawing_tool == "resize":
                self.current_drawn = self.selected
        elif self.drawing_tool in ["rectangle", "circle", "line"]:
            if self.drawing_tool == "rectangle":
                self.current_drawn = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='black', fill='red')
            elif self.drawing_tool == "circle":
                self.current_drawn = self.canvas.create_oval(self.start_x, self.start_y, self.start_x, self.start_y, outline='black', fill='blue')
            elif self.drawing_tool == "line":
                self.current_drawn = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y, fill='green')
        elif self.drawing_tool == "free":
            self.prev_x, self.prev_y = event.x, event.y

    def on_button_motion(self, event):
        if self.drawing_tool == "move" and self.selected:
            dx, dy = event.x - self.start_x, event.y - self.start_y
            self.canvas.move(self.selected, dx, dy)
            self.start_x, self.start_y = event.x, event.y
        elif self.drawing_tool in ["resize", "rectangle", "circle", "line"]:
            self.update_shape(event)
        elif self.drawing_tool == "free":
            x, y = event.x, event.y
            self.canvas.create_line(self.prev_x, self.prev_y, x, y, fill='black', width=self.line_thickness, smooth=True, capstyle=tk.ROUND)
            self.prev_x, self.prev_y = x, y

    def update_shape(self, event):
        if self.current_drawn and (self.drawing_tool in ["rectangle", "resize"]):
            if (event.state & 0x0001):  # Check if Shift is pressed
                side = max(abs(event.x - self.start_x), abs(event.y - self.start_y))
                self.canvas.coords(self.current_drawn, self.start_x, self.start_y, self.start_x + side * (1 if event.x > self.start_x else -1), self.start_y + side * (1 if event.y > self.start_y else -1))
            else:
                self.canvas.coords(self.current_drawn, self.start_x, self.start_y, event.x, event.y)
        elif self.current_drawn and (self.drawing_tool in ["circle", "resize"]):
            if (event.state & 0x0001):  # Check if Shift is pressed
                radius = max(abs(event.x - self.start_x), abs(event.y - self.start_y))
                self.canvas.coords(self.current_drawn, self.start_x - radius, self.start_y - radius, self.start_x + radius, self.start_y + radius)
            else:
                dx = event.x - self.start_x
                dy = event.y - self.start_y
                radius = (dx**2 + dy**2)**0.5
                self.canvas.coords(self.current_drawn, self.start_x - radius, self.start_y - radius, self.start_x + radius, self.start_y + radius)
        elif self.current_drawn and self.drawing_tool == "line":
            self.canvas.coords(self.current_drawn, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        if self.current_drawn:
            self.update_shape(event)
            self.current_drawn = None
        self.selected = None  # Deselect any object

    def select_tool(self, tool):
        self.drawing_tool = tool
        self.selected = None
        self.current_drawn = None  # Reset any ongoing drawing operation

        # Adjust visibility of line thickness frame based on selected tool
        if self.drawing_tool == "free":
            self.line_thickness_frame.pack(side="right", fill="y")  # Make line thickness frame visible
            self.line_thickness_entry.config(state="normal")  # Enable line thickness entry
        else:
            self.line_thickness_frame.pack_forget()  # Hide line thickness frame
            self.line_thickness_entry.config(state="disabled")  # Disable line thickness entry

    def reset_canvas(self):
        if messagebox.askokcancel("Zurücksetzen bestätigen", "Möchten Sie wirklich die Zeichenfläche zurücksetzen?"):
            self.canvas.delete("all")

    def save_as_svg(self):
        svg_root = ET.Element("svg", width=str(self.canvas.winfo_width()), height=str(self.canvas.winfo_height()), xmlns="http://www.w3.org/2000/svg")
        for item in self.canvas.find_all():
            coords = self.canvas.coords(item)
            options = self.canvas.itemconfig(item)
            if self.canvas.type(item) == "rectangle":
                ET.SubElement(svg_root, "rect", x=str(coords[0]), y=str(coords[1]), width=str(coords[2]-coords[0]), height=str(coords[3]-coords[1]), fill=options['fill'][-1])
            elif self.canvas.type(item) == "oval":
                rx = (coords[2] - coords[0]) / 2
                ry = (coords[3] - coords[1]) / 2
                cx = coords[0] + rx
                cy = coords[1] + ry
                ET.SubElement(svg_root, "ellipse", cx=str(cx), cy=str(cy), rx=str(rx), ry=str(ry), fill=options['fill'][-1])
            elif self.canvas.type(item) == "line":
                line_attributes = {"x1": str(coords[0]), "y1": str(coords[1]), "x2": str(coords[2]), "y2": str(coords[3]), "stroke": options['fill'][-1]}
                if 'width' in options:
                    line_attributes["stroke-width"] = str(options['width'][-1])  # Set line thickness attribute
                ET.SubElement(svg_root, "line", **line_attributes)

        tree = ET.ElementTree(svg_root)
        filename = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG Files", "*.svg")])
        if filename:
            tree.write(filename)

    def set_line_thickness(self):
        self.line_thickness = int(self.line_thickness_var.get())


    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    svg_editor = SVGEditor()
    svg_editor.run()
