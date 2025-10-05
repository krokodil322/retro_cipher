import os


path = r"C:\programms\cipher\interface\images"
files = os.listdir(path)
for file in files:
    if '=' in file:
        _, name = file.split('=')
        os.rename(
            os.path.join(path, file),
            os.path.join(path, name)
        )