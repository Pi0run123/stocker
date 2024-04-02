import customtkinter as ctk
import tkinter.messagebox as tkmb
import subprocess
from pymongo import MongoClient

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("600x600")

reg_user_entry = None
reg_pass_entry = None
confirm_pass_entry = None



def login():
    username = user_entry.get()
    password = user_pass.get()
    connection = MongoClient("localhost", 27017)
    db = connection.stock
    collection = db.login
    user_data = collection.find_one({'username': username, 'password': password})
    if user_data:
        tkmb.showinfo(title="Login Successful", message="You have logged in Successfully")
        open_stock_py()
    else:
        tkmb.showerror(title="Login Failed", message="Invalid Username or Password")
def open_stock_py():
    subprocess.Popen(["python", "stock.py"])

def register():
    global reg_user_entry, reg_pass_entry, confirm_pass_entry
    username = reg_user_entry.get()
    password = reg_pass_entry.get()
    confirm_password = confirm_pass_entry.get()
    connection = MongoClient("localhost", 27017)
    db = connection.stock
    collection = db.login
    data = {"username": username, "password": password}
    collection.insert_one(data)
    if password != confirm_password:
        tkmb.showerror(title="Registration Failed", message="Passwords do not match.")
    else:
        tkmb.showinfo(title="Registration Successful", message="You have registered Successfully")


label = ctk.CTkLabel(app, text="Stocker Login Page")
label.pack(pady=20)

frame = ctk.CTkFrame(master=app)
frame.pack(pady=20, padx=40, fill='both', expand=True)
label.pack(pady=12, padx=10)

user_entry = ctk.CTkEntry(master=frame, placeholder_text="Username")
user_entry.pack(pady=12, padx=10)

user_pass = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
user_pass.pack(pady=12, padx=10)

button = ctk.CTkButton(master=frame, text='Login', command=login)
button.pack(pady=12, padx=10)

checkbox = ctk.CTkCheckBox(master=frame, text='Remember Me')
checkbox.pack(pady=12, padx=10)

register_button = ctk.CTkButton(master=frame, text='Register', command=lambda: open_registration_window())
register_button.pack(pady=12, padx=10)


def open_registration_window():
    global reg_user_entry, reg_pass_entry, confirm_pass_entry
    registration_window = ctk.CTkToplevel(app)
    registration_window.title("Registration")

    reg_user_label = ctk.CTkLabel(master=registration_window, text="Username")
    reg_user_label.pack(pady=5)
    reg_user_entry = ctk.CTkEntry(master=registration_window)
    reg_user_entry.pack(pady=5)

    reg_pass_label = ctk.CTkLabel(master=registration_window, text="Password")
    reg_pass_label.pack(pady=5)
    reg_pass_entry = ctk.CTkEntry(master=registration_window, show="*")
    reg_pass_entry.pack(pady=5)

    confirm_pass_label = ctk.CTkLabel(master=registration_window, text="Confirm Password")
    confirm_pass_label.pack(pady=5)
    confirm_pass_entry = ctk.CTkEntry(master=registration_window, show="*")
    confirm_pass_entry.pack(pady=5)

    register_button = ctk.CTkButton(master=registration_window, text="Register", command=register)
    register_button.pack(pady=10)


app.mainloop()
