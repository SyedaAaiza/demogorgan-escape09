import os
from PIL import Image


def convert_jpg_to_transparent_png(input_jpg_path, output_png_path, threshold=230):
    """
    Converts a JPG image into a PNG and removes near-white background pixels.

    :param input_jpg_path: Path to the source JPEG file.
    :param output_png_path: Path where the converted PNG will be saved.
    :param threshold: RGB brightness threshold (0-255) above which pixels are treated as white background.
    """
    if not os.path.exists(input_jpg_path):
        print(f"Error: Could not find image at {input_jpg_path}")
        return

    try:
        # Open image and convert to RGBA (Red, Green, Blue, Alpha)
        img = Image.open(input_jpg_path).convert("RGBA")
        datas = img.getdata()

        new_data = []
        for pixel in datas:
            r, g, b, a = pixel
            # Check if the pixel is white/near-white background
            if r > threshold and g > threshold and b > threshold:
                new_data.append((255, 255, 255, 0))  # Make pixel transparent
            else:
                new_data.append((r, g, b, 255))  # Keep original pixel color

        img.putdata(new_data)
        img.save(output_png_path, "PNG")
        print(f"Success! Saved transparent PNG to: {output_png_path}")

    except Exception as e:
        print(f"Conversion failed: {e}")


if __name__ == "__main__":
    # Resolve project assets directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")

    # Paths for coin.jpg and output coin.png
    jpg_path = os.path.join(assets_dir, "coin.jpg")
    png_path = os.path.join(assets_dir, "coin.png")

    convert_jpg_to_transparent_png(jpg_path, png_path)