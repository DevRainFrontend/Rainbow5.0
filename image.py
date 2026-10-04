import asyncio
import io

from PIL import Image

MAX_DIMENSION = 1024
MAX_OUTPUT_BYTES = 8 * 1024 * 1024


def _remove_background_sync(image_bytes: bytes) -> bytes:
    from rembg import remove

    img = Image.open(io.BytesIO(image_bytes))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    width, height = img.size
    if max(width, height) > MAX_DIMENSION:
        ratio = MAX_DIMENSION / max(width, height)
        img = img.resize(
            (int(width * ratio), int(height * ratio)),
            Image.Resampling.LANCZOS,
        )

    output = remove(img)
    buf = io.BytesIO()
    output.save(buf, format="PNG", optimize=True)
    result = buf.getvalue()

    if len(result) > MAX_OUTPUT_BYTES:
        raise ValueError("Çıktı dosyası çok büyük.")

    return result


async def remove_background(image_bytes: bytes) -> bytes:
    return await asyncio.to_thread(_remove_background_sync, image_bytes)
