import qrcode

url = input("Enter your url: ")

file_path = r"C:\Users\ANKAN SEN\Desktop\PythonProject Folder\QR_CODE_GENERATOR_PROJECT/qrcode.png"

qr = qrcode.QRCode()
qr.add_data(url)
image = qr.make_image()
image.save(file_path)
print("QR code saved at:", file_path)
