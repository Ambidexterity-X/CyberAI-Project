from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

# EXIF tag IDs
_TAG_DATETIME_ORIGINAL = 36867   # DateTimeOriginal
_GPS_IFD_TAG = 0x8825            # GPSInfo pointer

_EXIF_DT_FMT = "%Y:%m:%d %H:%M:%S"


def extract_captured_at(path: Path) -> datetime:
    """Return the photo's capture time as a UTC-aware datetime.

    Strategy:
    1. EXIF tag 36867 (DateTimeOriginal) — real capture time for photos.
    2. Fallback: file modification time (st_mtime).
    """
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            raw = exif.get(_TAG_DATETIME_ORIGINAL)
            if raw:
                # EXIF stores local time with no timezone; treat as UTC for
                # consistency across devices.
                return datetime.strptime(raw, _EXIF_DT_FMT).replace(tzinfo=timezone.utc)
    except Exception:
        pass

    mtime = path.stat().st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc)


def _dms_to_decimal(dms, ref: str) -> float:
    """Convert a GPS DMS tuple ((d,1),(m,1),(s,e3)) and hemisphere ref to decimal degrees."""
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0
    value = degrees + minutes + seconds
    if ref in ("S", "W"):
        value = -value
    return value


def extract_gps(path: Path) -> tuple[float, float] | None:
    """Return (latitude, longitude) in decimal degrees from EXIF GPS tags, or None.

    Returns None when:
    - The image has no EXIF data.
    - The GPSInfo IFD is absent.
    - Any required GPS tag (lat, lat-ref, lon, lon-ref) is missing or malformed.
    """
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            gps_ifd = exif.get_ifd(_GPS_IFD_TAG)
            if not gps_ifd:
                return None

            # IFD tag IDs (not names)
            lat_dms = gps_ifd.get(2)   # GPSLatitude
            lat_ref = gps_ifd.get(1)   # GPSLatitudeRef
            lon_dms = gps_ifd.get(4)   # GPSLongitude
            lon_ref = gps_ifd.get(3)   # GPSLongitudeRef

            if not all([lat_dms, lat_ref, lon_dms, lon_ref]):
                return None

            lat = _dms_to_decimal(lat_dms, lat_ref)
            lon = _dms_to_decimal(lon_dms, lon_ref)
            return lat, lon
    except Exception:
        return None
