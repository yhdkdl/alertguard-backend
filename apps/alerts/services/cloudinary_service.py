import cloudinary
import cloudinary.uploader
from django.conf import settings


def configure_cloudinary():
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )


def upload_photo(file, folder: str = "alertguard/alerts") -> str | None:
    """
    Upload a photo file to Cloudinary.
    Returns the secure URL string on success, None on failure.
    """
    try:
        configure_cloudinary()
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="image",
        )
        return result.get("secure_url")
    except Exception as e:
        print(f"[Cloudinary] Upload failed: {e}")
        return None