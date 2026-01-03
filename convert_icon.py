from PIL import Image
import sys
import os

def convert_to_ico(input_path, output_path):
    try:
        img = Image.open(input_path).convert("RGBA")
        # Resize to standard icon sizes
        img.save(output_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print(f"Successfully converted {input_path} to {output_path}")
    except Exception as e:
        print(f"Error converting icon: {e}")
        sys.exit(1)

if __name__ == "__main__":
    convert_to_ico("icon_bgremoved2.png", "icon.ico")
