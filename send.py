import tkinter as tk
from tkinter import filedialog, messagebox
import socket
import os
from tkinter import ttk
import threading
import netifaces  # To get the system's IP address
from tkinterdnd2 import DND_FILES, TkinterDnD

class FileTransferApp:

    def __init__(self, master):
        self.master = master
        self.master.title("File Transfer App")
        self.master.geometry("450x50")  # Set a smaller initial window size
        self.master.resizable(False, False)  # Disable resizing

        # Default theme
        self.is_dark_theme = False
        self.main_frame = None
        self.progress_bar = None  # Initialize progress_bar
        self.create_widgets()

    def create_widgets(self):
        """Create all the widgets for the application."""
        # Main Frame
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(pady=10)

        # Theme Toggle Button
        self.theme_button = tk.Button(self.main_frame, text="🌈 Toggle Theme", command=self.toggle_theme)
        self.theme_button.grid(row=0, column=2, padx=10)

        # Buttons to choose send or receive
        self.send_button = tk.Button(self.main_frame, text="📤 Send File(s)", command=self.show_send_options)
        self.send_button.grid(row=0, column=0, padx=10)

        self.receive_button = tk.Button(self.main_frame, text="📥 Receive File", command=self.show_receive_options)
        self.receive_button.grid(row=0, column=1, padx=10)

        # Options Frame (Hidden by default)
        self.options_frame = tk.Frame(self.master)
        self.options_frame.pack(pady=10)

        # Send Panel (Hidden by default)
        self.ip_label = tk.Label(self.options_frame, text="Enter IP Address:")
        self.ip_entry = tk.Entry(self.options_frame)
        self.ip_entry.insert(0, "192.168.1.")  # Set initial value
        self.drop_area = tk.Label(self.options_frame, text="Drag and Drop Files Here", relief="groove", width=50, height=10)

        # Message Label for Receive File
        self.message_label = tk.Label(self.options_frame, text="", wraplength=400)
        self.system_ip_label = tk.Label(self.options_frame, text="", wraplength=400)

        # Apply the initial theme
        self.apply_theme()

    def apply_theme(self):
        """Apply the current theme to the application."""
        if self.is_dark_theme:
            bg_color = 'black'
            fg_color = 'white'
            button_bg_color = 'gray'
        else:
            bg_color = 'white'
            fg_color = 'black'
            button_bg_color = 'lightgray'

        # Update main frame and buttons
        self.master.configure(bg=bg_color)
        self.main_frame.configure(bg=bg_color)
        self.theme_button.configure(bg=button_bg_color, fg=fg_color)
        self.send_button.configure(bg=button_bg_color, fg=fg_color)
        self.receive_button.configure(bg=button_bg_color, fg=fg_color)

        # Update options frame and elements
        self.options_frame.configure(bg=bg_color)
        self.ip_label.configure(bg=bg_color, fg=fg_color)
        self.ip_entry.configure(bg=button_bg_color, fg=fg_color)
        self.drop_area.configure(bg=button_bg_color, fg=fg_color)
        self.message_label.configure(bg=bg_color, fg=fg_color)
        self.system_ip_label.configure(bg=bg_color, fg=fg_color)

    def toggle_theme(self):
        """Toggle between dark and light themes."""
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()

    def show_send_options(self):
        """Show the options for sending files."""
        self.clear_options()
        self.ip_label.grid(row=0, column=0, padx=5)
        self.ip_entry.grid(row=0, column=1, padx=5)
        self.drop_area.grid(row=1, column=0, columnspan=2, pady=10)

        # Create a horizontal progress bar under the drop area
        self.progress_bar = ttk.Progressbar(self.options_frame, orient='horizontal', length=350, mode='determinate')
        self.progress_bar.grid(row=2, column=0, columnspan=2, pady=10)  # Position the progress bar below the drop area

        # Bind drag and drop
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.on_drop)  # Update to use '<<Drop>>'
        self.drop_area.bind("<Button-1>", self.select_file_dialog)  # Open file dialog on click

        # Expand window size
        self.master.geometry("450x335")  # Adjust height for options

    def show_receive_options(self):
        """Show the options for receiving files."""
        self.clear_options()
        self.message_label.configure(text="🟢 Server started. Waiting for incoming files...")
        self.message_label.grid(row=0, column=0, columnspan=2, pady=5)

        # Get and display the system IP address
        ip_address = self.get_ip_address()
        self.system_ip_label.configure(text=f"🌐 Your DHCP IP Address: {ip_address}")
        self.system_ip_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Expand window size
        self.master.geometry("450x200")  # Adjust height for options
        threading.Thread(target=self.start_server, daemon=True).start()

    def clear_options(self):
        """Clear the options frame before showing new options."""
        for widget in self.options_frame.winfo_children():
            widget.grid_forget()

    def select_file_dialog(self, event):
        """Open file dialog when the drag and drop area is clicked."""
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            for file_path in file_paths:
                self.send_file(file_path)

    def on_drop(self, event):
        """Handle files dropped into the drop area."""
        file_paths = event.data.split()  # Split the dropped data
        for file_path in file_paths:
            self.send_file(file_path)

    def send_file(self, file_path):
        """Send a single file to the specified IP address."""
        ip_address = self.ip_entry.get()
        if not ip_address:
            messagebox.showerror("Error", "Please enter an IP address.")
            return

        # Get the original filename
        original_filename = os.path.basename(file_path)
        modified_filename = f"{original_filename}_YOU_ARE_SEND_IT"
        port = 5001  # Make sure this matches the server port

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((ip_address, port))

                # Send the modified filename first
                s.send(modified_filename.encode('utf-8'))

                # Get the file size
                file_size = os.path.getsize(file_path)
                self.progress_bar['maximum'] = file_size  # Set the maximum value of the progress bar

                # Now send the file data
                with open(file_path, 'rb') as f:
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        s.send(data)
                        self.progress_bar['value'] += len(data)  # Update the progress bar
                        self.master.update_idletasks()  # Refresh the GUI

                messagebox.showinfo("Success", "📤 File sent successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"❌ Failed to send file: {e}")
            finally:
                # Reset the progress bar after the upload is complete
                self.progress_bar['value'] = 0

    def start_server(self):
        """Start the server to receive files."""
        port = 5001  # Change port as needed
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', port))
        server_socket.listen(1)

        while True:
            conn, addr = server_socket.accept()
            print(f"Connection from {addr} established.")

            # Receive the modified filename first
            modified_filename = conn.recv(1024).decode('utf-8')
            print(f"Receiving file as: {modified_filename}")

            with open(modified_filename, 'wb') as f:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    f.write(data)

            print("File received successfully.")
            self.message_label.configure(text="🟢 File received successfully!", fg='green')
            conn.close()

    def get_ip_address(self):
        """Get the local DHCP IP address of the system."""
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            try:
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    ip_info = addrs[netifaces.AF_INET][0]
                    # Check if it's a valid DHCP IP (not localhost)
                    if ip_info['addr'] != '127.0.0.1':
                        return ip_info['addr']
            except ValueError:
                continue
        return "Unable to retrieve IP"

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FileTransferApp(root)
    root.mainloop()