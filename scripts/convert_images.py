import os
from PIL import Image

def convert_to_webp(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(root, file)
                webp_path = os.path.splitext(filepath)[0] + '.webp'
                
                if not os.path.exists(webp_path):
                    try:
                        with Image.open(filepath) as img:
                            img.save(webp_path, 'WEBP', quality=85)
                            print(f"Converted {file} to {os.path.basename(webp_path)}")
                    except Exception as e:
                        print(f"Error converting {file}: {e}")

if __name__ == "__main__":
    static_images = r'c:\Users\J. Shivani Divyaansh\Downloads\Computer projects\school project\static\images'
    convert_to_webp(static_images)
