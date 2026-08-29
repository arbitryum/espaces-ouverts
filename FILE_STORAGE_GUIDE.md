# File Storage Configuration - Espaces Ouverts

This document describes how file storage is configured for the Espaces Ouverts project, supporting both local development and AWS S3 production storage.

## Overview

The project uses Django's pluggable storage backend system to support:
- **Development**: Local filesystem storage (no external dependencies)
- **Production**: AWS S3 storage (scalable, CDN-friendly)

## Storage Configuration

### Development (Default)

Files are stored locally in the `media/` directory within the project.

**Settings:**
```python
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    }
}
```

**Media Files Structure:**
```
media/
└── spaces/
    └── YYYY/MM/
        └── spaces/
            ├── space_image_1.jpg
            ├── space_image_2.jpg
            └── ...
```

### Production (AWS S3)

For production, set the `USE_S3` environment variable to enable S3 storage.

**Enable S3 Storage:**
```bash
export USE_S3=True
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_STORAGE_BUCKET_NAME=espaces-ouverts
export AWS_S3_REGION_NAME=us-east-1
```

**Settings:**
```python
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        'OPTIONS': {
            'bucket_name': os.environ.get('AWS_STORAGE_BUCKET_NAME'),
            'region_name': os.environ.get('AWS_S3_REGION_NAME'),
            'access_key': os.environ.get('AWS_ACCESS_KEY_ID'),
            'secret_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        }
    }
}
```

## Space Model - Image Fields

The `Space` model includes two image-related fields:

### ImageField

```python
image = models.ImageField(
    upload_to='spaces/%Y/%m/',
    null=True,
    blank=True,
    help_text="Photo of the space"
)
```

- **Automatically stored** in `MEDIA_ROOT/spaces/2026/08/` (date-based organization)
- **Supports both** local filesystem and S3 backends
- **Optional** - spaces can exist without images

### Alt Text Field

```python
image_alt_text = models.CharField(
    max_length=500,
    blank=True,
    default="",
    help_text="Alternative text for the image"
)
```

- Stores accessibility text for screen readers
- Used in templates as: `<img alt="{{ space.image_alt_text }}" />`

## Accessing Images in Templates

### Direct URL
```django
<img src="{{ space.image.url }}" alt="{{ space.image_alt_text }}" />
```

### With Fallback
```django
{% if space.image %}
  <img src="{{ space.image.url }}" alt="{{ space.image_alt_text }}" class="space-photo" />
{% else %}
  <img src="{% static 'images/placeholder.png' %}" alt="No image available" />
{% endif %}
```

### With Image Styling
```django
<figure>
  <img src="{{ space.image.url }}" alt="{{ space.image_alt_text }}" />
  <figcaption>{{ space.name }} - {{ space.care_home.name }}</figcaption>
</figure>
```

## Seeding Database with Images

The `seed_database` management command automatically links downloaded images to spaces.

```bash
python manage.py seed_database
```

**Process:**
1. Creates 9 care homes
2. Creates 12 spaces
3. **Automatically uploads images** from `spaces/media/images/` to media storage
4. Links images to corresponding spaces
5. Sets alt text for accessibility

**Output:**
```
✓ Created: Salle d'animation fermée (Alice Prin) + Image
✓ Created: Bibliothèque (La Cascade) + Image
...
```

## File Size and Image Optimization

### Recommended Image Specifications

- **Format**: JPEG or WebP
- **Maximum Size**: 5MB per file
- **Recommended Dimensions**: 1024x768 or 16:9 aspect ratio
- **Optimization**: Compress before upload

### Storage Limits

| Backend | Max Storage | Cost | Notes |
|---------|------------|------|-------|
| Local FS | Unlimited | None | Limited by disk space |
| AWS S3 | Unlimited | ~$0.023 per GB/month | Scales automatically |

## Accessing Storage Programmatically

### In Django Views or Management Commands

```python
from django.core.files.base import ContentFile
from spaces.models import Space

# Save image from file
with open('path/to/image.jpg', 'rb') as f:
    space = Space.objects.get(id=1)
    space.image.save(
        'spaces/image.jpg',
        ContentFile(f.read()),
        save=True
    )
```

### Via Django Admin

1. Go to `/admin/spaces/space/`
2. Edit any space
3. Use the file upload widget to select an image
4. Image is automatically saved to storage backend

## Environment Variables

Create a `.env.local` file (copied from `.env.template`):

```bash
# Local Storage (Development)
USE_S3=False

# Or for S3 (Production)
USE_S3=True
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=espaces-ouverts
AWS_S3_REGION_NAME=us-east-1
```

Load environment variables:
```bash
export $(cat .env.local | grep -v '#' | xargs)
```

Or use `python-dotenv`:
```python
# In settings.py
from dotenv import load_dotenv
load_dotenv('.env.local')
```

## Media URLs

### Development
- Files: `http://localhost:8000/media/spaces/2026/08/spaces/image.jpg`
- Django serves files automatically via `urlpatterns`

### Production (S3)
- Files: `https://espaces-ouverts.s3.us-east-1.amazonaws.com/media/spaces/2026/08/spaces/image.jpg`
- CloudFront CDN recommended for faster delivery

## Troubleshooting

### Images Not Appearing

**Problem**: Images linked in database but not loading
**Solution**: 
1. Check `MEDIA_ROOT` and `MEDIA_URL` settings
2. Verify file permissions on local filesystem
3. Check S3 bucket permissions if using S3

### Upload Fails

**Problem**: "Could not read image data" error
**Solution**:
1. Verify file is valid JPEG/PNG
2. Check file size doesn't exceed limits
3. Test with `django-admin shell`:
   ```python
   from django.core.files.base import ContentFile
   from spaces.models import Space
   # Test upload
   ```

### S3 Connection Issues

**Problem**: "Unable to connect to AWS S3"
**Solution**:
1. Verify AWS credentials are correct
2. Check IAM permissions on S3 bucket
3. Verify bucket name and region match

## Migration to S3

To migrate existing local files to S3:

```python
# In Django shell
from django.core.files.storage import default_storage
from spaces.models import Space

for space in Space.objects.filter(image__isnull=False):
    # File will be re-uploaded to new storage backend
    space.image.name = space.image.name  # Trigger save
    space.save(update_fields=['image'])
```

## Security Considerations

- **Local Storage**: Ensure `media/` directory is not web-accessible without Django
- **S3 Storage**: 
  - Use IAM policies to restrict bucket access
  - Enable bucket versioning for recovery
  - Consider S3 encryption at rest

## Further Reading

- [Django File Storage Documentation](https://docs.djangoproject.com/en/6.1/topics/files/)
- [Django Storages Library](https://django-storages.readthedocs.io/)
- [AWS S3 Storage Guide](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)
