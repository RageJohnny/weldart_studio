import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET

class SVGEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WELDART Studio")
        self.root.geometry("1000x700")
        self.root.iconbitmap('icons/logo.ico')

        # Definiere alle Variablen vor ihrer Verwendung
        self.drawing_tool = None
        self.current_drawn = None
        self.selected = None
        self.line_thickness = 1
        self.fill_enabled = False
        self.undo_stack = []
        self.redo_stack = []

        self.add_menu()
        self.toolbar = tk.Frame(self.root, bg="lightgrey")
        self.toolbar.pack(side="left", fill="y", padx=(10, 10), pady=(10,10))

        self.load_icons()
        self.add_buttons_to_toolbar()

        self.line_thickness_frame = tk.Frame(self.root, bg="lightgrey")

        # Überschrift hinzufügen
        settings_label = tk.Label(self.line_thickness_frame, text="Settings", bg="lightgrey", font=("Helvetica", 10, "bold"))
        settings_label.pack(side="top", pady=(5, 0))

        # Linienstärke-Eingabefeld hinzufügen
        self.line_thickness_label = tk.Label(self.line_thickness_frame, text="Line Thickness in mm", bg="lightgrey")
        self.line_thickness_label.pack(pady=(5, 0))
        self.line_thickness_var = tk.StringVar(value=str(self.line_thickness))
        self.line_thickness_entry = ttk.Entry(self.line_thickness_frame, textvariable=self.line_thickness_var)
        self.line_thickness_entry.pack(pady=5, side="top")
        self.line_thickness_entry.config(state="disabled")  # Deaktiviert das Textfeld standardmäßig

        # Gefüllt-Checkbox hinzufügen
        self.fill_checkbox_var = tk.BooleanVar(value=False)
        self.fill_checkbox = ttk.Checkbutton(self.line_thickness_frame, text="Filled", variable=self.fill_checkbox_var, command=self.toggle_fill)
        self.fill_checkbox.pack(side="top", padx=5, pady=20)

        # OK-Button hinzufügen
        self.line_thickness_button = ttk.Button(self.line_thickness_frame, text="OK", command=self.set_line_thickness)
        self.line_thickness_button.pack(pady=5, side="top")

        # Frame packen
        self.line_thickness_frame.pack(side="right", fill="y", padx=(10, 10), pady=(10, 10))

        

        self.horizontal_ruler = tk.Canvas(self.root, bg='white', height=30)
        self.horizontal_ruler.pack(side="top", fill="x", padx=(30, 0))
        self.vertical_ruler = tk.Canvas(self.root, bg='white', width=30)
        self.vertical_ruler.pack(side="left", fill="y")


        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='white')
        self.horizontal_ruler.pack(side="top", fill=tk.X)
        self.vertical_ruler.pack(side="left", fill=tk.Y)
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)
        

        self.bind_canvas_events()
        self.root.bind("<Configure>", self.redraw_rulers)


    def load_icons(self):
        # Icon files should be in the 'icons' directory relative to this script
        self.rect_image = tk.PhotoImage(file="icons/rectangle.png").subsample(12)
        self.circle_image = tk.PhotoImage(file="icons/circle.png").subsample(12)
        self.line_image = tk.PhotoImage(file="icons/line.png").subsample(12)
        self.free_image = tk.PhotoImage(file="icons/free.png").subsample(12)
        self.move_image = tk.PhotoImage(file="icons/move.png").subsample(12)
        self.resize_image = tk.PhotoImage(file="icons/resize.png").subsample(12)
        self.reset_image = tk.PhotoImage(file="icons/reset.png").subsample(12)
        self.select_image = tk.PhotoImage(file="icons/select.png").subsample(12)

    def add_buttons_to_toolbar(self):
        self.rect_button = tk.Button(self.toolbar, image=self.select_image, command=lambda: self.select_tool("select"))
        self.rect_button.pack(side="top", fill="x")
        self.rect_button = tk.Button(self.toolbar, image=self.rect_image, command=lambda: self.select_tool("rectangle"))
        self.rect_button.pack(side="top", fill="x")
        self.circle_button = tk.Button(self.toolbar, image=self.circle_image, command=lambda: self.select_tool("circle"))
        self.circle_button.pack(side="top", fill="x")
        self.line_button = tk.Button(self.toolbar, image=self.line_image, command=lambda: self.select_tool("line"))
        self.line_button.pack(side="top", fill="x")
        self.free_button = tk.Button(self.toolbar, image=self.free_image, command=lambda: self.select_tool("free"))
        self.free_button.pack(side="top", fill="x")
        self.move_button = tk.Button(self.toolbar, image=self.move_image, command=lambda: self.select_tool("move"), state=tk.DISABLED)
        self.move_button.pack(side="top", fill="x")
        self.resize_button = tk.Button(self.toolbar, image=self.resize_image, command=lambda: self.select_tool("resize"), state=tk.DISABLED)
        self.resize_button.pack(side="top", fill="x")
        self.reset_button = tk.Button(self.toolbar, image=self.reset_image, command=self.reset_canvas)
        self.reset_button.pack(side="top", fill="x")

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
            self.horizontal_ruler.create_text(i+5, 20, text=str(i), anchor="n")
        height = self.canvas.winfo_height()
        for i in range(0, height, 50):
            self.vertical_ruler.create_line(10, i, 30, i, fill="gray")
            self.vertical_ruler.create_text(20, i+5, text=str(i), anchor="e")

    def add_menu(self):
        self.menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Save as SVG", command=self.save_as_svg)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        about_menu = tk.Menu(self.menu_bar, tearoff=0)
        about_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Copyright Johannes Georg Larcher"))
        self.menu_bar.add_cascade(label="About", menu=about_menu)
        self.root.config(menu=self.menu_bar)

    def toggle_fill(self):
        self.fill_enabled = not self.fill_enabled

    def on_button_press(self, event):
        self.undo_stack.append(self.canvas.find_all())
        self.redo_stack = []
        self.start_x, self.start_y = event.x, event.y
        if self.drawing_tool == "move" or self.drawing_tool == "resize":
            self.selected = self.canvas.find_closest(event.x, event.y)[0]
            self.canvas.tag_raise(self.selected)
            if self.drawing_tool == "resize":
                self.current_drawn = self.selected
        elif self.drawing_tool in ["rectangle", "circle", "line"]:
            if self.drawing_tool == "rectangle":
                fill_color = "red" if self.fill_enabled else ""
                self.current_drawn = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='black', fill=fill_color)
            elif self.drawing_tool == "circle":
                fill_color = "blue" if self.fill_enabled else ""
                self.current_drawn = self.canvas.create_oval(self.start_x, self.start_y, self.start_x, self.start_y, outline='black', fill=fill_color)
            elif self.drawing_tool == "line":
                self.current_drawn = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y, fill='green')
        elif self.drawing_tool == "free":
            self.prev_x, self.prev_y = event.x, event.y

    def on_button_motion(self, event):
        if self.drawing_tool == "move" and self.selected:
            if self.selected == self.canvas.find_closest(event.x, event.y)[0]:  # Überprüfe, ob das nächste Objekt das ausgewählte ist
                dx, dy = event.x - self.start_x, event.y - self.start_y
                self.canvas.move(self.selected, dx, dy)
                self.start_x, self.start_y = event.x, event.y
        elif self.drawing_tool == "resize" and self.selected:
            if self.selected == self.current_drawn:  # Stelle sicher, dass das zu verändernde Objekt das ausgewählte ist
                self.update_shape(event)
        elif self.drawing_tool in ["rectangle", "circle", "line"]:
            self.update_shape(event)
        elif self.drawing_tool == "free":
            x, y = event.x, event.y
            self.canvas.create_line(self.prev_x, self.prev_y, x, y, fill='black', width=self.line_thickness, smooth=True, capstyle=tk.ROUND)
            self.prev_x, self.prev_y = x, y

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

        # Überprüfe, ob das Tool zum Resizen oder Bewegen verwendet wurde
        if self.drawing_tool in ["resize", "move"]:
            # Entferne das Highlight vom bearbeiteten Objekt
            if self.canvas.type(self.selected) in ["rectangle", "oval"]:
                self.canvas.itemconfig(self.selected, outline="black", width=1)
            elif self.canvas.type(self.selected) == "line":
                self.canvas.itemconfig(self.selected, fill="black", width=1)

            # Setze das ausgewählte Objekt zurück
            self.selected = None

            # Deaktiviere die Resize- und Move-Buttons
            self.resize_button.config(state=tk.DISABLED)
            self.move_button.config(state=tk.DISABLED)

        # Setze das current_drawn-Objekt zurück, unabhängig vom Werkzeug
        self.current_drawn = None
        self.selected = None

    def select_tool(self, tool):
        self.drawing_tool = tool
        self.canvas.unbind("<Button-1>")
        if self.drawing_tool == "select":
            self.canvas.bind("<Button-1>", self.on_canvas_click)
        else:
            self.bind_canvas_events()
            # Überprüfe, ob ein Objekt hervorgehoben ist, bevor der Resize-Button aktiviert wird
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



    def clear_selection(self):
        if self.selected:
            self.canvas.itemconfig(self.selected, outline="black")  # Setze die Highlight-Farbe zurück
            self.selected = None  # Setze das ausgewählte Objekt zurück

    def on_canvas_click(self, event):
        if self.drawing_tool == "select":
            for item in self.canvas.find_all():
                item_type = self.canvas.type(item)
                if item_type in ["rectangle", "oval"]:  # Diese Typen unterstützen 'outline'
                    self.canvas.itemconfig(item, outline="black", width=1)
                elif item_type == "line":  # Linien unterstützen 'fill' statt 'outline'
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

    def save_as_svg(self):
        svg_root = ET.Element("svg", width=str(self.canvas.winfo_width()), height=str(self.canvas.winfo_height()), xmlns="http://www.w3.org/2000/svg")
        for item in self.canvas.find_all():
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
            print("Linienstärke gesetzt auf:", self.line_thickness)
        except ValueError:
            messagebox.showerror("Fehler", "Bitte eine gültige Zahl eingeben")

    def clear_highlights(self):
        for item in self.canvas.find_all():
            item_type = self.canvas.type(item)
            if item_type in ["rectangle", "oval"]:
                self.canvas.itemconfig(item, outline="black", width=1)
            elif item_type in ["line"]:
                self.canvas.itemconfig(item, fill="black", width=1)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    svg_editor = SVGEditor()
    svg_editor.run()