from PIL import Image
from io import BytesIO
from fastapi import UploadFile


async def add_watermark_and_save(upload_file: UploadFile, watermark_image_path: str, output_path: str,
                                 position=(0, 0), transparency=0.3):
    base_image = Image.open(BytesIO(await upload_file.read())).convert("RGBA")
    watermark = Image.open(watermark_image_path).convert("RGBA")
    watermark = watermark.resize((100, 100), Image.LANCZOS)
    alpha = watermark.split()[3]
    alpha = alpha.point(lambda p: p * transparency)
    watermark.putalpha(alpha)
    base_image.paste(watermark, position, watermark)
    base_image.save(output_path, format="PNG")
