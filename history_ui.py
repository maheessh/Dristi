import sqlite3
import tkinter as tk
from tkinter import ttk

class DetectionHistoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Detection History")
        self.root.geometry("500x400")

        # Title Label
        self.label = ttk.Label(root, text="Detection History", font=("Arial", 16, "bold"))
        self.label.pack(pady=10)

        # Listbox to Show History
        self.history_listbox = tk.Listbox(root, width=50, height=15, font=("Arial", 12))
        self.history_listbox.pack(pady=10)

        # Load Data Button
        self.load_button = ttk.Button(root, text="Load History", command=self.load_history)
        self.load_button.pack(pady=5)

        # Delete Selected Item
        self.delete_button = ttk.Button(root, text="Delete Selected", command=self.delete_selected)
        self.delete_button.pack(pady=5)

    def load_history(self):
        """ Load detection history from SQLite database """
        conn = sqlite3.connect("detections.db")
        cursor = conn.cursor()
        cursor.execute("SELECT detected_item, timestamp FROM history ORDER BY id DESC")
        records = cursor.fetchall()
        conn.close()

        # Update Listbox
        self.history_listbox.delete(0, tk.END)
        for item, timestamp in records:
            self.history_listbox.insert(tk.END, f"{timestamp} - {item}")

    def delete_selected(self):
        """ Delete selected detection from database """
        selected_item = self.history_listbox.curselection()
        if selected_item:
            conn = sqlite3.connect("detections.db")
            cursor = conn.cursor()
            text = self.history_listbox.get(selected_item).split(" - ")[1]
            cursor.execute("DELETE FROM history WHERE detected_item = ?", (text,))
            conn.commit()
            conn.close()
            self.load_history()  # Refresh list

if __name__ == "__main__":
    root = tk.Tk()
    app = DetectionHistoryApp(root)
    root.mainloop()
