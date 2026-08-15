"""Pull a few JPEG stills from a recording. OpenAI vision does not take raw video."""

from __future__ import annotations

import tempfile


def extract_jpeg_frames(
    data: bytes,
    content_type: str = "",
    count: int = 8,
    max_side: int = 720,
) -> list[bytes]:
    if not data:
        return []
    ct = (content_type or "").lower()
    if _looks_like_image(data, ct):
        framed = _downscale_bytes(data, max_side)
        return [framed] if framed else []
    return _from_video(data, ct, count, max_side)


def _looks_like_image(data: bytes, content_type: str) -> bool:
    if "jpeg" in content_type or "jpg" in content_type or "png" in content_type:
        return True
    return data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n"


def _from_video(data: bytes, content_type: str, count: int, max_side: int) -> list[bytes]:
    try:
        import cv2
    except ImportError:
        return []

    suffix = ".mp4" if "mp4" in content_type else ".webm"
    frames: list[bytes] = []
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(data)
        tmp.flush()
        cap = cv2.VideoCapture(tmp.name)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if total <= 0:
            ok, image = cap.read()
            cap.release()
            if not ok:
                return []
            encoded = _encode(image, max_side)
            return [encoded] if encoded else []

        picks = _even_indices(total, count)
        for idx in picks:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, image = cap.read()
            if not ok:
                continue
            encoded = _encode(image, max_side)
            if encoded:
                frames.append(encoded)
        cap.release()
    return frames


def _even_indices(total: int, count: int) -> list[int]:
    if total <= count:
        return list(range(total))
    if count == 1:
        return [total // 2]
    step = (total - 1) / (count - 1)
    return [int(i * step) for i in range(count)]


def _encode(image, max_side: int) -> bytes | None:
    import cv2

    h, w = image.shape[:2]
    long_side = max(h, w)
    if long_side > max_side:
        scale = max_side / long_side
        image = cv2.resize(image, (int(w * scale), int(h * scale)))
    ok, buf = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    if not ok:
        return None
    return buf.tobytes()


def _downscale_bytes(data: bytes, max_side: int) -> bytes | None:
    try:
        import cv2
        import numpy as np
    except ImportError:
        return data
    arr = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        return data
    return _encode(image, max_side)
