import tkinter as tk
from tkinter import simpledialog
import openpyxl
from openpyxl import Workbook
import os
import datetime
import platform
import psutil

EXCEL_FILE = "assistant_data.xlsx"

def get_system_knowledge():
    """Retrieve basic system knowledge."""
    info = []
    info.append(f"OS: {platform.system()} {platform.release()}")
    info.append(f"CPU Usage: {psutil.cpu_percent()}%")
    
    mem = psutil.virtual_memory()
    info.append(f"RAM: {mem.used / (1024**3):.1f}GB / {mem.total / (1024**3):.1f}GB")
    
    return " | ".join(info)

class MouseAssistant:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True) # Remove window borders
        self.root.attributes("-topmost", True) # Always on top
        
        # Make the background transparent
        transparent_color = 'magenta'
        self.root.configure(bg=transparent_color)
        self.root.attributes("-transparentcolor", transparent_color)

        # Variables for animation and dragging
        self._offset_x = 0
        self._offset_y = 0
        self._dragged = False
        self.is_paused = False
        
        self.dx = 3 # Horizontal speed
        self.dy = 2 # Vertical speed
        self.window_width = 30
        self.window_height = 30
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        # Create a canvas to draw the dot
        self.canvas = tk.Canvas(root, width=self.window_width, height=self.window_height, bg=transparent_color, highlightthickness=0)
        self.canvas.pack()
        
        # Draw a solid red dot
        self.dot_id = self.canvas.create_oval(5, 5, 25, 25, fill="red", outline="darkred", width=2)

        # Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<Button-3>", self.on_right_click)

        self.init_excel()
        
        # Start in center
        x = (self.screen_width // 2) - (self.window_width // 2)
        y = (self.screen_height // 2) - (self.window_height // 2)
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        
        # Start animation loop
        self.walk_loop()

    def walk_loop(self):
        if not self.is_paused and not self._dragged:
            x = self.root.winfo_x() + self.dx
            y = self.root.winfo_y() + self.dy
            
            # Bounce horizontally
            if x <= 0:
                x = 0
                self.dx *= -1
            elif x + self.window_width >= self.screen_width:
                x = self.screen_width - self.window_width
                self.dx *= -1
            
            # Bounce vertically
            if y <= 0:
                y = 0
                self.dy *= -1
            elif y + self.window_height >= self.screen_height:
                y = self.screen_height - self.window_height
                self.dy *= -1
            
            self.root.geometry(f"+{x}+{y}")
            
        self.root.after(30, self.walk_loop)

    def init_excel(self):
        if not os.path.exists(EXCEL_FILE):
            wb = Workbook()
            ws = wb.active
            ws.title = "Assistant Logs"
            ws.append(["Timestamp", "Input Data", "System Context"])
            wb.save(EXCEL_FILE)

    def log_to_excel(self, data):
        try:
            wb = openpyxl.load_workbook(EXCEL_FILE)
            ws = wb.active
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sys_context = get_system_knowledge()
            ws.append([timestamp, data, sys_context])
            wb.save(EXCEL_FILE)
            print("Data saved successfully!")
        except Exception as e:
            print(f"Error saving to Excel: {e}")

    def on_press(self, event):
        self.is_paused = True
        self._offset_x = event.x
        self._offset_y = event.y
        self._dragged = False

    def on_motion(self, event):
        self._dragged = True
        x = self.root.winfo_x() + event.x - self._offset_x
        y = self.root.winfo_y() + event.y - self._offset_y
        self.root.geometry(f"+{x}+{y}")

    def on_release(self, event):
        if not self._dragged:
            self.take_input()
        else:
            self.is_paused = False

    def take_input(self):
        user_input = simpledialog.askstring("Mouse Assistant", "Tell me something to remember:", parent=self.root)
        if user_input:
            self.log_to_excel(user_input)
        self.is_paused = False

    def on_right_click(self, event):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseAssistant(root)
    root.mainloop()
