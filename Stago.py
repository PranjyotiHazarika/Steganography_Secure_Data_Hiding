import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
import cv2
import hashlib


def generate_key_hash(key):
    return hashlib.sha256(key.encode()).hexdigest()[:16]  # 16-character hash


def encode_message(image_path, message, key):
    key_hash = generate_key_hash(key)
    message = key_hash + message  # Embed key hash for authentication
    message += "@@@"  # Delimiter to detect end of message

    img = cv2.imread(image_path)
    flat_img = img.flatten()

    bin_message = ''.join(format(ord(c), '08b') for c in message)

    if len(bin_message) > len(flat_img):
        messagebox.showerror("Error", "Message too large for the selected image.")
        return

    for i in range(len(bin_message)):
        flat_img[i] = (flat_img[i] & ~1) | int(bin_message[i])

    encoded_img = flat_img.reshape(img.shape)
    save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
    if save_path:
        cv2.imwrite(save_path, encoded_img)
        messagebox.showinfo("Success", "Message encoded and saved successfully!")


def decode_message(image_path, key):
    key_hash = generate_key_hash(key)

    img = cv2.imread(image_path)
    flat_img = img.flatten()

    bits = [str(flat_img[i] & 1) for i in range(len(flat_img))]

    chars = [chr(int(''.join(bits[i:i + 8]), 2)) for i in range(0, len(bits), 8)]
    decoded_message = ''.join(chars)

    if key_hash not in decoded_message:
        messagebox.showerror("Error", "Incorrect key or no hidden message found.")
        return

    decoded_message = decoded_message.split('@@@')[0]
    decoded_message = decoded_message.replace(key_hash, '')

    messagebox.showinfo("Decoded Message", decoded_message)


def select_image(operation):
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not file_path:
        return

    if operation == "encode":
        message = message_entry.get()
        key = key_entry.get()
        if not message or not key:
            messagebox.showwarning("Warning", "Please enter a message and a key.")
            return
        encode_message(file_path, message, key)
    elif operation == "decode":
        key = key_entry.get()
        if not key:
            messagebox.showwarning("Warning", "Please enter a key.")
            return
        decode_message(file_path, key)


# GUI Setup
root = tk.Tk()
root.title("Steganography Tool")
root.geometry("400x300")

tk.Label(root, text="Secret Key:").pack()
key_entry = tk.Entry(root, show="*")
key_entry.pack()

tk.Label(root, text="Message:").pack()
message_entry = tk.Entry(root)
message_entry.pack()

tk.Button(root, text="Select Image & Encode", command=lambda: select_image("encode")).pack(pady=5)
tk.Button(root, text="Select Image & Decode", command=lambda: select_image("decode")).pack(pady=5)

root.mainloop()