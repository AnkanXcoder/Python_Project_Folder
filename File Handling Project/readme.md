# 🗂️ File Handling Project (Python)

## 📄 Overview
This project demonstrates **basic file handling operations in Python**, allowing users to:
- Create files
- Read file content
- Update or rename files
- Delete files  
It uses the built-in **os** and **pathlib** modules for easy file management.

---

## ⚙️ Features
✅ View all files and folders in the directory  
✅ Create a new file and write custom data  
✅ Read existing files  
✅ Update (rename, overwrite, or append) a file  
✅ Delete any existing file safely  

---

## 🧠 Functions Explained

### `readfileandfolder()`
Lists all files and directories recursively using `Path.rglob('*')`.

### `createfile()`
Creates a new file and writes user-input data into it.  
Prevents overwriting an existing file.

### `readfile()`
Reads and prints the contents of a file if it exists.

### `updatefile()`
Offers three options:
1. Rename a file  
2. Overwrite file data  
3. Append new data to the file

### `deletefile()`
Deletes a selected file if it exists.

---------------

🧑‍💻 Author

### `Ankan Sen`
Built for learning and practicing Python file handling concepts.

----------------
