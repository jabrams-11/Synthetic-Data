import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path
import time
from datetime import datetime, timedelta

class ProgressWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Synthetic Data Generation Progress")
        self.root.geometry("600x400")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            length=500, 
            mode='determinate', 
            variable=self.progress_var
        )
        self.progress_bar.grid(row=0, column=0, pady=10, padx=10, sticky=(tk.W, tk.E))
        
        # Status labels
        self.status_label = ttk.Label(main_frame, text="Initializing...")
        self.status_label.grid(row=1, column=0, pady=5)
        
        self.time_label = ttk.Label(main_frame, text="Time elapsed: 00:00:00")
        self.time_label.grid(row=2, column=0, pady=5)
        
        self.eta_label = ttk.Label(main_frame, text="ETA: --:--:--")
        self.eta_label.grid(row=3, column=0, pady=5)
        
        # Pole distribution frame
        dist_frame = ttk.LabelFrame(main_frame, text="Pole Type Distribution", padding="5")
        dist_frame.grid(row=4, column=0, pady=10, sticky=(tk.W, tk.E))
        self.dist_text = tk.Text(dist_frame, height=5, width=50)
        self.dist_text.grid(row=0, column=0, pady=5)
        
        self.start_time = time.time()
        self.update_progress()
        
    def update_progress(self):
        """Update progress from status file"""
        try:
            status_file = Path("Renders/generation_status.json")
            if status_file.exists():
                with open(status_file, 'r') as f:
                    status = json.load(f)
                
                # Update progress bar
                progress = (status['completed_images'] / status['total_images']) * 100
                self.progress_var.set(progress)
                
                # Update status
                self.status_label.config(
                    text=f"Generating image {status['completed_images']}/{status['total_images']}"
                )
                
                # Update time
                elapsed = time.time() - self.start_time
                self.time_label.config(text=f"Time elapsed: {timedelta(seconds=int(elapsed))}")
                
                if status['completed_images'] > 0:
                    images_per_sec = status['completed_images'] / elapsed
                    remaining_images = status['total_images'] - status['completed_images']
                    eta_seconds = remaining_images / images_per_sec
                    self.eta_label.config(text=f"ETA: {timedelta(seconds=int(eta_seconds))}")
                
                # Update distribution
                dist_text = "Pole Type Distribution:\n"
                for pole_type, count in status['pole_type_counts'].items():
                    percentage = (count / status['completed_images']) * 100 if status['completed_images'] > 0 else 0
                    dist_text += f"{pole_type}: {count} ({percentage:.1f}%)\n"
                self.dist_text.delete('1.0', tk.END)
                self.dist_text.insert('1.0', dist_text)
        
        except Exception as e:
            print(f"Error updating progress: {e}")
        
        self.root.after(1000, self.update_progress)  # Update every second
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    window = ProgressWindow()
    window.run() 