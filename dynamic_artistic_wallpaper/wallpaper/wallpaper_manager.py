from PIL import Image
import os
import glob
import ctypes

def cut_generated_image(image_path, output_path="cut_image.png"):
    """Resize and crop the generated image to fit a 1920x1080 background."""
    target_width = 1920
    target_height = 1080

    # Open the original image
    with Image.open(image_path) as img:
        original_width, original_height = img.size

        # Calculate the target aspect ratio and the original aspect ratio
        target_ratio = target_width / target_height
        original_ratio = original_width / original_height

        # Resize the image to maintain aspect ratio
        if original_ratio > target_ratio:
            # If the original image is wider than the target, scale by height
            new_height = target_height
            new_width = int(original_ratio * new_height)
        else:
            # If the original image is taller than the target, scale by width
            new_width = target_width
            new_height = int(new_width / original_ratio)

        img = img.resize((new_width, new_height), Image.ANTIALIAS)

        # Calculate cropping coordinates to center the crop
        left = (new_width - target_width) / 2
        top = (new_height - target_height) / 2
        right = (new_width + target_width) / 2
        bottom = (new_height + target_height) / 2

        # Crop the image
        img = img.crop((left, top, right, bottom))

        # Save the cropped image
        img.save(output_path)

    return output_path

def cleanup_old_images(directory, pattern="*.png", max_files=5):
    """Deletes old images to free up space, keeping the most recent files."""
    files = glob.glob(os.path.join(directory, pattern))
    files.sort(key=os.path.getmtime, reverse=True)  # Newest files first

    for file in files[max_files:]:
        os.remove(file)
        print(f"Deleted old image: {file}")

def set_wallpaper_windows(image_path):
    """Sets the desktop wallpaper on Windows using SystemParametersInfo."""

    SPI_SETDESKWALLPAPER = 0x0014
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    try:
        # Set the desktop wallpaper
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
        print('Wallpaper set successfully\n')
    except Exception as e:
        print(f'Error: {e}')