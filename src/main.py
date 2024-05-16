import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET
from tooltip import *

class SVGEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WELDART Studio")
        self.root.geometry("1200x800")
        self.root.iconbitmap('icons/logo.ico')

        self.drawing_tool = None
        self.current_drawn = None
        self.selected = None
        self.line_thickness = 1
        self.eraser_radius = 10
        self.fill_enabled = False
        self.undo_stack = []
        self.redo_stack = []
        self.eraser_circle = None
        self.zoom_scale = 1.0  # Initial zoom scale

        self.add_menu()
        
        self.toolbar = tk.Frame(self.root, bg="#f0f0f0", bd=2, relief=tk.RAISED)
        self.toolbar.pack(side="left", fill="y", padx=(10, 0), pady=10)

        self.load_icons()
        self.add_buttons_to_toolbar()

        self.line_thickness_frame = tk.Frame(self.root, bg="#f0f0f0", bd=2, relief=tk.SUNKEN, padx=10, pady=10)
        
        settings_label = tk.Label(self.line_thickness_frame, text="Settings", bg="#d9d9d9", font=("Helvetica", 16, "bold"))
        settings_label.pack(side="top", pady=(10, 10), fill="x")

        self.line_thickness_label = tk.Label(self.line_thickness_frame, text="Line Thickness in mm", bg="#f0f0f0", font=("Helvetica", 12, "bold"))
        self.line_thickness_label.pack(pady=(10, 0), fill="x")
        self.line_thickness_label.config(anchor="center")

        self.line_thickness_var = tk.StringVar(value=str(self.line_thickness))
        self.line_thickness_entry = ttk.Entry(self.line_thickness_frame, textvariable=self.line_thickness_var, font=("Helvetica", 10))
        self.line_thickness_entry.pack(pady=10, side="top", fill="x")
        self.line_thickness_entry.config(state="disabled")

        # Adding a description label for Line Thickness
        self.line_thickness_desc = tk.Label(self.line_thickness_frame, text="Sets the thickness in mm for the freehand pencil.", bg="#f0f0f0", font=("Helvetica", 8))
        self.line_thickness_desc.pack(pady=(0, 10), fill="x")
        self.line_thickness_desc.config(anchor="center")

        # Adding separator and Fill Objects label
        ttk.Separator(self.line_thickness_frame, orient="horizontal").pack(fill="x", pady=10)
        fill_objects_label = tk.Label(self.line_thickness_frame, text="Fill Objects", bg="#f0f0f0", font=("Helvetica", 12, "bold"))
        fill_objects_label.pack(pady=(10, 0), fill="x")
        fill_objects_label.config(anchor="center")

        self.fill_checkbox_var = tk.BooleanVar(value=False)
        self.fill_checkbox = ttk.Checkbutton(self.line_thickness_frame, text="Fill Objects", variable=self.fill_checkbox_var, command=self.toggle_fill, style="TCheckbutton")
        self.fill_checkbox.pack(side="top", padx=10, pady=10, anchor="w")
        
        # Adding a description label for Fill Objects
        self.fill_objects_desc = tk.Label(self.line_thickness_frame, text="Determines whether objects are filled or just outlined.", bg="#f0f0f0", font=("Helvetica", 8))
        self.fill_objects_desc.pack(pady=(0, 10), fill="x")
        self.fill_objects_desc.config(anchor="center")

        # Adding separator and Eraser Radius label
        ttk.Separator(self.line_thickness_frame, orient="horizontal").pack(fill="x", pady=10)
        eraser_radius_label = tk.Label(self.line_thickness_frame, text="Eraser Radius in px", bg="#f0f0f0", font=("Helvetica", 12, "bold"))
        eraser_radius_label.pack(pady=(10, 0), fill="x")
        eraser_radius_label.config(anchor="center")

        self.eraser_radius_var = tk.IntVar(value=self.eraser_radius)
        self.eraser_radius_slider = ttk.Scale(self.line_thickness_frame, from_=0, to=200, orient=tk.HORIZONTAL, variable=self.eraser_radius_var, command=self.update_eraser_radius)
        self.eraser_radius_slider.pack(pady=10, side="top", fill="x")
        self.eraser_radius_slider.state(['disabled'])  # Disable slider by default

        # Adding a label to display current eraser radius value
        self.eraser_radius_value = tk.Label(self.line_thickness_frame, text=f"{self.eraser_radius} px", bg="#f0f0f0", font=("Helvetica", 10))
        self.eraser_radius_value.pack(pady=(0, 10), fill="x")
        self.eraser_radius_value.config(anchor="center")

        # Adding a description label for Eraser Radius
        self.eraser_radius_desc = tk.Label(self.line_thickness_frame, text="Sets the radius in pixels for the eraser.", bg="#f0f0f0", font=("Helvetica", 8))
        self.eraser_radius_desc.pack(pady=(0, 10), fill="x")
        self.eraser_radius_desc.config(anchor="center")

        self.line_thickness_button = ttk.Button(self.line_thickness_frame, text="OK", command=self.set_line_thickness)
        self.line_thickness_button.pack(pady=10, side="top")

        self.line_thickness_frame.pack(side="right", fill="y", padx=(0, 10), pady=10)

        self.horizontal_ruler = tk.Canvas(self.root, bg='#f8f8f8', height=30)
        self.horizontal_ruler.pack(side="top", fill="x", padx=(50, 0), pady=(10, 0))
        self.vertical_ruler = tk.Canvas(self.root, bg='#f8f8f8', width=30)
        self.vertical_ruler.pack(side="left", fill="y", padx=(0, 10), pady=(0, 10))

        self.canvas = tk.Canvas(self.root, width=900, height=700, bg='white')
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True, padx=(0, 10), pady=(0, 10))

        self.bind_canvas_events()
        self.root.bind("<Configure>", self.redraw_rulers)

        # Shortcuts für Undo, Redo und Save hinzufügen
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-y>", lambda event: self.redo())
        self.root.bind("<Control-s>", lambda event: self.save_as_svg())

        # Mousewheel zoom binding
        self.canvas.bind("<MouseWheel>", self.zoom)

        # Styling für Checkbutton
        self.style = ttk.Style()
        self.style.configure("TCheckbutton", background="#f0f0f0", font=("Helvetica", 10))

        # Adding tooltips
        Tooltip(self.select_button, "Select Tool")
        Tooltip(self.rect_button, "Draw Rectangle")
        Tooltip(self.circle_button, "Draw Circle")
        Tooltip(self.line_button, "Draw Line")
        Tooltip(self.free_button, "Free Draw")
        Tooltip(self.move_button, "Move Object")
        Tooltip(self.resize_button, "Resize Object")
        Tooltip(self.reset_button, "Reset Canvas")
        Tooltip(self.erase_button, "Erase Freehand Line")

    def load_icons(self):
        self.rect_image = tk.PhotoImage(file="icons/rectangle.png").subsample(12)
        self.circle_image = tk.PhotoImage(file="icons/circle.png").subsample(12)
        self.line_image = tk.PhotoImage(file="icons/line.png").subsample(12)
        self.free_image = tk.PhotoImage(file="icons/free.png").subsample(12)
        self.move_image = tk.PhotoImage(file="icons/move.png").subsample(12)
        self.resize_image = tk.PhotoImage(file="icons/resize.png").subsample(12)
        self.reset_image = tk.PhotoImage(file="icons/reset.png").subsample(12)
        self.select_image = tk.PhotoImage(file="icons/select.png").subsample(12)
        self.erase_image = tk.PhotoImage(file="icons/erase.png").subsample(12)  # Add erase icon

    def add_buttons_to_toolbar(self):
        self.select_button = tk.Button(self.toolbar, image=self.select_image, command=lambda: self.select_tool("select"), bg="white")
        self.select_button.pack(side="top", fill="x", padx=2, pady=2)
        self.rect_button = tk.Button(self.toolbar, image=self.rect_image, command=lambda: self.select_tool("rectangle"), bg="white")
        self.rect_button.pack(side="top", fill="x", padx=2, pady=2)
        self.circle_button = tk.Button(self.toolbar, image=self.circle_image, command=lambda: self.select_tool("circle"), bg="white")
        self.circle_button.pack(side="top", fill="x", padx=2, pady=2)
        self.line_button = tk.Button(self.toolbar, image=self.line_image, command=lambda: self.select_tool("line"), bg="white")
        self.line_button.pack(side="top", fill="x", padx=2, pady=2)
        self.free_button = tk.Button(self.toolbar, image=self.free_image, command=lambda: self.select_tool("free"), bg="white")
        self.free_button.pack(side="top", fill="x", padx=2, pady=2)
        self.erase_button = tk.Button(self.toolbar, image=self.erase_image, command=lambda: self.select_tool("erase"), bg="white")  # Add erase button
        self.erase_button.pack(side="top", fill="x", padx=2, pady=2)
        self.move_button = tk.Button(self.toolbar, image=self.move_image, command=lambda: self.select_tool("move"), state=tk.DISABLED, bg="white")
        self.move_button.pack(side="top", fill="x", padx=2, pady=2)
        self.resize_button = tk.Button(self.toolbar, image=self.resize_image, command=lambda: self.select_tool("resize"), state=tk.DISABLED, bg="white")
        self.resize_button.pack(side="top", fill="x", padx=2, pady=2)
        self.reset_button = tk.Button(self.toolbar, image=self.reset_image, command=self.reset_canvas, bg="white")
        self.reset_button.pack(side="top", fill="x", padx=2, pady=2)

    def bind_canvas_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_button_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def redraw_rulers(self, event=None):
        self.horizontal_ruler.delete("all")
        self.vertical_ruler.delete("all")
        self.add_rulers()

    def add_rulers(self):
        width = self.canvas.winfo_width()
        for i in range(0, width, 50):
            self.horizontal_ruler.create_line(i, 10, i, 30, fill="gray")
            self.horizontal_ruler.create_text(i+5, 20, text=str(i), anchor="n", font=("Helvetica", 8))
        height = self.canvas.winfo_height()
        for i in range(0, height, 50):
            self.vertical_ruler.create_line(10, i, 30, i, fill="gray")
            self.vertical_ruler.create_text(20, i+5, text=str(i), anchor="e", font=("Helvetica", 8))

    def add_menu(self):
        self.menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Save as SVG", command=self.save_as_svg, accelerator="Ctrl+S")
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        about_menu = tk.Menu(self.menu_bar, tearoff=0)
        about_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Copyright Johannes Georg Larcher"))
        self.menu_bar.add_cascade(label="About", menu=about_menu)
        self.root.config(menu=self.menu_bar)

    def toggle_fill(self):
        self.fill_enabled = not self.fill_enabled

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.drawing_tool == "move" or self.drawing_tool == "resize":
            self.selected = self.canvas.find_closest(event.x, event.y)[0]
            self.canvas.tag_raise(self.selected)
            if self.drawing_tool == "resize":
                self.current_drawn = self.selected
        elif self.drawing_tool == "erase":
            self.erase_line(event)
        elif self.drawing_tool in ["rectangle", "circle", "line"]:
            if self.drawing_tool == "rectangle":
                fill_color = "red" if self.fill_enabled else ""
                self.current_drawn = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='black', fill=fill_color)
            elif self.drawing_tool == "circle":
                fill_color = "blue" if self.fill_enabled else ""
                self.current_drawn = self.canvas.create_oval(self.start_x, self.start_y, self.start_x, self.start_y, outline='black', fill=fill_color)
            elif self.drawing_tool == "line":
                self.current_drawn = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y, fill='green')
            self.undo_stack.append(self.current_drawn)
            self.redo_stack = []
        elif self.drawing_tool == "free":
            self.prev_x, self.prev_y = event.x, event.y

    def on_button_motion(self, event):
        if self.drawing_tool == "move" and self.selected:
            if self.selected == self.canvas.find_closest(event.x, event.y)[0]:
                dx, dy = event.x - self.start_x, event.y - self.start_y
                self.canvas.move(self.selected, dx, dy)
                self.start_x, self.start_y = event.x, event.y
        elif self.drawing_tool == "resize" and self.selected:
            if self.selected == self.current_drawn:
                self.update_shape(event)
        elif self.drawing_tool in ["rectangle", "circle", "line"]:
            self.update_shape(event)
        elif self.drawing_tool == "free":
            x, y = event.x, event.y
            self.canvas.create_line(self.prev_x, self.prev_y, x, y, fill='black', width=self.line_thickness, smooth=True, capstyle=tk.ROUND)
            self.prev_x, self.prev_y = x, y
        elif self.drawing_tool == "erase":
            self.erase_line(event)
        self.update_eraser_circle(event)

    def update_shape(self, event):
        if self.current_drawn:
            if self.drawing_tool in ["rectangle", "resize"]:
                if (event.state & 0x0001):
                    side = max(abs(event.x - self.start_x), abs(event.y - self.start_y))
                    self.canvas.coords(self.current_drawn, self.start_x, self.start_y, self.start_x + side * (1 if event.x > self.start_x else -1), self.start_y + side * (1 if event.y > self.start_y else -1))
                else:
                    self.canvas.coords(self.current_drawn, self.start_x, self.start_y, event.x, event.y)
            elif self.drawing_tool in ["circle", "resize"]:
                if (event.state & 0x0001):
                    radius = max(abs(event.x - self.start_x), abs(event.y - self.start_y))
                    self.canvas.coords(self.current_drawn, self.start_x - radius, self.start_y - radius, self.start_x + radius, self.start_y + radius)
                else:
                    dx = event.x - self.start_x
                    dy = event.y - self.start_y
                    radius = (dx**2 + dy**2)**0.5
                    self.canvas.coords(self.current_drawn, self.start_x - radius, self.start_y - radius, self.start_x + radius, self.start_y + radius)
            elif self.drawing_tool == "line":
                self.canvas.coords(self.current_drawn, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        if self.current_drawn:
            self.update_shape(event)

        if self.drawing_tool in ["resize", "move"]:
            if self.canvas.type(self.selected) in ["rectangle", "oval"]:
                self.canvas.itemconfig(self.selected, outline="black", width=1)
            elif self.canvas.type(self.selected) == "line":
                self.canvas.itemconfig(self.selected, fill="black", width=1)

            self.selected = None

            self.resize_button.config(state=tk.DISABLED)
            self.move_button.config(state=tk.DISABLED)

        self.current_drawn = None
        self.selected = None

        if self.eraser_circle:
            self.canvas.delete(self.eraser_circle)
            self.eraser_circle = None

    def erase_line(self, event):
        radius = self.eraser_radius
        overlapping_items = self.canvas.find_overlapping(event.x - radius, event.y - radius, event.x + radius, event.y + radius)
        for item in overlapping_items:
            if self.canvas.type(item) == "line":
                self.canvas.delete(item)
                self.undo_stack.append(item)
                self.redo_stack = []

    def update_eraser_circle(self, event):
        if self.drawing_tool == "erase":
            radius = self.eraser_radius
            x, y = event.x, event.y
            if self.eraser_circle:
                self.canvas.coords(self.eraser_circle, x - radius, y - radius, x + radius, y + radius)
            else:
                self.eraser_circle = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="red", dash=(2, 2))
        else:
            if self.eraser_circle:
                self.canvas.delete(self.eraser_circle)
                self.eraser_circle = None

    def zoom(self, event):
        scale = 1.1 if event.delta > 0 else 0.9
        self.zoom_scale *= scale
        self.canvas.scale("all", event.x, event.y, scale, scale)
        self.redraw_rulers()

    def select_tool(self, tool):
        self.drawing_tool = tool
        self.current_drawn = None  # Reset current_drawn when tool is changed
        self.canvas.unbind("<Button-1>")
        if self.drawing_tool == "select":
            self.canvas.bind("<Button-1>", self.on_canvas_click)
        else:
            self.bind_canvas_events()
            if self.selected and self.canvas.itemcget(self.selected, "outline") == "yellow":
                if tool == "resize":
                    self.resize_button.config(state=tk.NORMAL)
                else:
                    self.resize_button.config(state=tk.DISABLED)
            else:
                self.move_button.config(state=tk.DISABLED)
                self.resize_button.config(state=tk.DISABLED)

            if self.drawing_tool == "free":
                self.line_thickness_frame.pack(side="right", fill="y")
                self.line_thickness_entry.config(state="normal")
            else:
                self.line_thickness_entry.config(state="disabled")

            if self.drawing_tool == "erase":
                self.eraser_radius_slider.state(['!disabled'])
                self.canvas.bind("<Motion>", self.update_eraser_circle)
                self.eraser_circle = self.canvas.create_oval(0, 0, 0, 0, outline="red", dash=(2, 2))  # Add eraser circle initially
            else:
                self.eraser_radius_slider.state(['disabled'])
                self.canvas.unbind("<Motion>")
                if self.eraser_circle:
                    self.canvas.delete(self.eraser_circle)
                    self.eraser_circle = None

    def clear_selection(self):
        if self.selected:
            self.canvas.itemconfig(self.selected, outline="black")
            self.selected = None

    def on_canvas_click(self, event):
        if self.drawing_tool == "select":
            for item in self.canvas.find_all():
                item_type = self.canvas.type(item)
                if item_type in ["rectangle", "oval"]:
                    self.canvas.itemconfig(item, outline="black", width=1)
                elif item_type == "line":
                    self.canvas.itemconfig(item, fill="black", width=1)

            selected_items = self.canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1)
            if selected_items:
                self.selected = selected_items[-1]
                selected_type = self.canvas.type(self.selected)
                if selected_type in ["rectangle", "oval"]:
                    self.canvas.itemconfig(self.selected, outline="yellow", width=3)
                elif selected_type == "line":
                    self.canvas.itemconfig(self.selected, fill="yellow", width=3)
                self.move_button.config(state=tk.NORMAL)
                self.resize_button.config(state=tk.NORMAL)
            else:
                self.selected = None
                self.move_button.config(state=tk.DISABLED)
                self.resize_button.config(state=tk.DISABLED)

    def reset_canvas(self):
        if messagebox.askokcancel("Zurücksetzen bestätigen", "Möchten Sie wirklich die Zeichenfläche zurücksetzen?"):
            self.canvas.delete("all")
            self.undo_stack = []
            self.redo_stack = []

    def save_as_svg(self):
        svg_root = ET.Element("svg", width=str(self.canvas.winfo_width()), height=str(self.canvas.winfo_height()), xmlns="http://www.w3.org/2000/svg")
        for item in self.canvas.find_all():
            if self.canvas.itemcget(item, 'state') != 'hidden':  # Nur sichtbare Objekte speichern
                coords = self.canvas.coords(item)
                options = self.canvas.itemconfig(item)
                fill_color = options.get('fill', [None])[-1]
                outline_color = options.get('outline', [None])[-1]
                if self.canvas.type(item) == "rectangle":
                    if fill_color:
                        ET.SubElement(svg_root, "rect", x=str(coords[0]), y=str(coords[1]), width=str(coords[2]-coords[0]), height=str(coords[3]-coords[1]), fill=fill_color, stroke=outline_color, stroke_width="1")
                    else:
                        ET.SubElement(svg_root, "rect", x=str(coords[0]), y=str(coords[1]), width=str(coords[2]-coords[0]), height=str(coords[3]-coords[1]), fill="none", stroke=outline_color, stroke_width="1")
                elif self.canvas.type(item) == "oval":
                    rx = (coords[2] - coords[0]) / 2
                    ry = (coords[3] - coords[1]) / 2
                    cx = coords[0] + rx
                    cy = coords[1] + ry
                    if fill_color:
                        ET.SubElement(svg_root, "ellipse", cx=str(cx), cy=str(cy), rx=str(rx), ry=str(ry), fill=fill_color, stroke=outline_color, stroke_width="1")
                    else:
                        ET.SubElement(svg_root, "ellipse", cx=str(cx), cy=str(cy), rx=str(rx), ry=str(ry), fill="none", stroke=outline_color, stroke_width="1")
                elif self.canvas.type(item) == "line":
                    line_attributes = {"x1": str(coords[0]), "y1": str(coords[1]), "x2": str(coords[2]), "y2": str(coords[3]), "stroke": options.get('fill', [None])[-1]}
                    if 'width' in options:
                        line_attributes["stroke-width"] = str(options['width'][-1])
                    ET.SubElement(svg_root, "line", **line_attributes)

        tree = ET.ElementTree(svg_root)
        filename = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG Files", "*.svg")])
        if filename:
            tree.write(filename)

    def set_line_thickness(self):
        try:
            self.line_thickness = int(self.line_thickness_var.get())
            self.eraser_radius = self.eraser_radius_var.get()
            print("Linienstärke gesetzt auf:", self.line_thickness)
            print("Radiergummi-Radius gesetzt auf:", self.eraser_radius)
        except ValueError:
            messagebox.showerror("Fehler", "Bitte eine gültige Zahl eingeben")

    def update_eraser_radius(self, val):
        self.eraser_radius = int(float(val))
        self.eraser_radius_value.config(text=f"{self.eraser_radius} px")
        print("Radiergummi-Radius aktualisiert auf:", self.eraser_radius)

    def clear_highlights(self):
        for item in self.canvas.find_all():
            item_type = self.canvas.type(item)
            if item_type in ["rectangle", "oval"]:
                self.canvas.itemconfig(item, outline="black", width=1)
            elif item_type in ["line"]:
                self.canvas.itemconfig(item, fill="black", width=1)

    def undo(self):
        if self.undo_stack:
            last_item = self.undo_stack.pop()
            self.redo_stack.append(last_item)
            self.canvas.itemconfig(last_item, state='hidden')

    def redo(self):
        if self.redo_stack:
            last_item = self.redo_stack.pop()
            self.undo_stack.append(last_item)
            self.canvas.itemconfig(last_item, state='normal')

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    svg_editor = SVGEditor()
    svg_editor.run()
