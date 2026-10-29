from PIL import Image
import os

# تمہارے assets کا راستہ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


def remove_and_crop(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # سفید / ہلکا background ہٹانا (jpeg میں white background ہوتا ہے)
        if item[0] > 220 and item[1] > 220 and item[2] > 220:
            new_data.append((255, 255, 255, 0))  # transparent
        else:
            new_data.append(item)

    img.putdata(new_data)

    # Auto-crop - خالی جگہ کاٹ دو
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    # سائز چھوٹا کرو - 3 pack format کے لیے 128x128 میں
    img.thumbnail((128, 128), Image.LANCZOS)

    img.save(output_path, "PNG")
    print(f"Done: {output_path}")


# 9 obstacles کے لیے loop
for i in range(1, 10):
    for ext in [".jpeg", ".jpg", ".png", ".webp"]:
        in_path = os.path.join(ASSETS_DIR, f"obs{i}{ext}")
        if os.path.exists(in_path):from PIL import Image
import os

# تمہارے assets کا راستہ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


def remove_and_crop(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # سفید / ہلکا background ہٹانا (jpeg میں white background ہوتا ہے)
        if item[0] > 220 and item[1] > 220 and item[2] > 220:
            new_data.append((255, 255, 255, 0))  # transparent
        else:
            new_data.append(item)

    img.putdata(new_data)

    # Auto-crop - خالی جگہ کاٹ دو
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    # سائز چھوٹا کرو - 3 pack format کے لیے 128x128 میں
    img.thumbnail((128, 128), Image.LANCZOS)

    img.save(output_path, "PNG")
    print(f"Done: {output_path}")


# 9 obstacles کے لیے loop
for i in range(1, 10):
    for ext in [".jpeg", ".jpg", ".png", ".webp"]:
        in_path = os.path.join(ASSETS_DIR, f"obs{i}{ext}")
        if os.path.exists(in_path):
            out_path = os.path.join(ASSETS_DIR, f"obs{i}.png")  # سب کو PNG بنا دوں گی
            remove_and_crop(in_path, out_path)
            # پرانی jpeg ڈیلیٹ کرنی ہے تو یہ لائن کھول دو
            # os.remove(in_path)
            break

print("سب 9 obstacles صاف ہو گئے!")
            out_path = os.path.join(ASSETS_DIR, f"obs{i}.png")  # سب کو PNG بنا دوں گی
            remove_and_crop(in_path, out_path)
            # پرانی jpeg ڈیلیٹ کرنی ہے تو یہ لائن کھول دو
            # os.remove(in_path)
            break

print("سب 9 obstacles صاف ہو گئے!")