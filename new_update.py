import tkinter as tk

# Variable to track the user's choice
user_choice = None


# Function to handle button clicks
def handle_update(choice):
    global user_choice
    user_choice = choice  # Update the shared variable
    print(f"User choice: {'Update selected' if choice else 'Update declined'}")
    return user_choice


# Function to launch the update dialog
def launch_update_dialog():
    global user_choice
    user_choice = None  # Reset the choice

    # Create the main window
    window = tk.Tk()
    window.title("App Update")
    window.geometry("400x200")

    # Add a label to display the status
    status_label = tk.Label(window, text="A new version of the app is out.\nWould you like to update the app?",
                            font=("Arial", 14))
    status_label.pack(pady=20)

    # Add a "Yes" button
    yes_button = tk.Button(window, text="Yes", bg="white", fg="green", font=("Arial", 12),
                           command=lambda: [handle_update(True), window.destroy()])
    yes_button.pack(side=tk.LEFT, padx=40, pady=20)

    # Add a "No" button
    no_button = tk.Button(window, text="No", bg="white", fg="red", font=("Arial", 12),
                          command=lambda: [handle_update(False), window.destroy()])
    no_button.pack(side=tk.RIGHT, padx=40, pady=20)

    # Run the application
    window.mainloop()

    return user_choice  # Return the choice after the dialog is closed

