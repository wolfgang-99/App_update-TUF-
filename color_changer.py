import tkinter as tk
import random

def change_color():
    colors = ["#FF5733", "#33FF57", "#5733FF", "#F1C40F", "#9B59B6", "#2ECC71", "#E74C3C", "#3498DB"]
    window.config(bg=random.choice(colors))

# Create the main window
window = tk.Tk()
window.title("Color Changer")
window.geometry("400x300")
window.resizable(False, False)

# Add a button to change the background color
button = tk.Button(window, text="Change Color", font=("Arial", 16), command=change_color)
button.pack(pady=20)

# Add a label for fun
label = tk.Label(window, text="Click the button to change the background color!", font=("Arial", 12))
label.pack(pady=20)

# Add a label for fun
label = tk.Label(window, text="This to show you i have update!", font=("Arial", 14))
label.pack(pady=20)

# Run the application
window.mainloop()
