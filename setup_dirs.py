import os

def setup():
    directories = [
        "assets",
        "logs",
        "audioexample",
        "audioexample/output",
        "vdio",
        "vdio/output",
        "output_files"
    ]
    
    for d in directories:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"Created directory: {d}")
        else:
            print(f"Directory already exists: {d}")

    # Create dummy READMEs in asset folders
    with open("assets/README.txt", "w", encoding="utf-8") as f:
        f.write("วางไฟล์ logo.png หรือ myicon.ico ที่นี่")

if __name__ == "__main__":
    setup()
