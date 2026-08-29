# File Storage Configuration

This project supports both local filesystem storage (development) and S3-compatible object storage (production).

## Development (Local Storage)

By default, uploaded files are stored in the `media/` directory at the project root:

```
espaces-ouverts/
├── media/
│   ├── spaces/
│   │   ├── 2026/
│   │   │   ├── 08/
│   │   │   │   ├── image1.jpg
│   │   │   │   └── image2.jpg
```

The `SpaceImage` model uses the `upload_to='spaces/%Y/%m/'` parameter to organize images by year and month.

### Usage

Upload images through:
- The Django admin interface at `/admin/`
- Programmatically via the Django ORM:

```python
from spaces.models import Space, SpaceImage

space = Space.objects.first()
image = SpaceImage.objects.create(
    space=space,
    image='path/to/image.jpg',
    alt_text='A description of the space'
)
```

Files are served by Django during development (when `DEBUG=True`) via the URL pattern `/media/<path>`.

## Production (S3-Compatible Storage)

In production, upload files are stored on S3 or any S3-compatible service (DigitalOcean Spaces, MinIO, etc.).

### Environment Variables

To enable S3 storage, set these environment variables:

```bash
# Trigger S3 storage (optional if AWS_ACCESS_KEY_ID is set)
USE_S3=True

# AWS S3 credentials
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=eu-west-1

# Optional: S3-compatible endpoint (for MinIO, DigitalOcean Spaces, etc.)
AWS_S3_ENDPOINT_URL=https://your-endpoint.example.com

# Optional: use HTTPS (default: True)
AWS_S3_USE_SSL=True

# Optional: custom CDN domain for serving files
AWS_S3_CUSTOM_DOMAIN=cdn.example.com

# Optional: custom MEDIA_URL (defaults to bucket URL)
MEDIA_URL=https://cdn.example.com/media/
```

### S3 Bucket Structure

When using S3, the bucket structure will be:

```
s3://your-bucket-name/
├── spaces/
│   ├── 2026/
│   │   ├── 08/
│   │   │   ├── image1.jpg
│   │   │   └── image2.jpg
```

### Scalingo Deployment

For Scalingo deployments with S3:

1. **Create or configure an S3 bucket** (e.g., with AWS, DigitalOcean, or similar)

2. **Set environment variables** via Scalingo dashboard or CLI:

```bash
scalingo --app your-app env-set \
  USE_S3=True \
  AWS_ACCESS_KEY_ID=your-key \
  AWS_SECRET_ACCESS_KEY=your-secret \
  AWS_STORAGE_BUCKET_NAME=your-bucket \
  AWS_S3_REGION_NAME=eu-west-1
```

3. **Deploy** - the application will automatically use S3 for file storage

### S3-Compatible Services

The application works with any S3-compatible service:

#### DigitalOcean Spaces

```bash
scalingo --app your-app env-set \
  USE_S3=True \
  AWS_ACCESS_KEY_ID=your-access-key \
  AWS_SECRET_ACCESS_KEY=your-secret-key \
  AWS_STORAGE_BUCKET_NAME=your-space-name \
  AWS_S3_REGION_NAME=nyc3 \
  AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com \
  AWS_S3_CUSTOM_DOMAIN=your-space-name.nyc3.cdn.digitaloceanspaces.com
```

#### MinIO (self-hosted)

```bash
scalingo --app your-app env-set \
  USE_S3=True \
  AWS_ACCESS_KEY_ID=minioadmin \
  AWS_SECRET_ACCESS_KEY=minioadmin \
  AWS_STORAGE_BUCKET_NAME=espaces-ouverts \
  AWS_S3_REGION_NAME=us-east-1 \
  AWS_S3_ENDPOINT_URL=https://minio.example.com \
  AWS_S3_USE_SSL=True
```

## How It Works

The Django `default` storage backend is configured in `app/settings.py`:

- **Development**: Uses `FileSystemStorage` to store files locally
- **Production**: Uses `S3Boto3Storage` from django-storages to store files on S3

The `SpaceImage.image` field uses the `default` storage backend automatically:

```python
class SpaceImage(models.Model):
    image = models.ImageField(
        upload_to='spaces/%Y/%m/',
        # storage backend is inherited from DEFAULT_FILE_STORAGE
    )
```

When a new image is uploaded:
1. Django validates the image (format, size)
2. The file is saved using the configured storage backend
3. The database stores the file path (relative to storage root)
4. In templates, use `{{ image.image.url }}` to get the full URL

## URL Generation

- **Development**: `/media/spaces/2026/08/image.jpg` → Served by Django
- **Production (S3)**: `https://bucket.s3.region.amazonaws.com/media/spaces/2026/08/image.jpg`
- **Production (Custom CDN)**: `https://cdn.example.com/media/spaces/2026/08/image.jpg`

## Troubleshooting

### "No such file or directory" in production

If you see this error, ensure:
1. S3 bucket exists and is accessible
2. AWS credentials are correctly set
3. `AWS_STORAGE_BUCKET_NAME` is correct

### Files not appearing after upload

Check:
1. The upload completed without errors (check application logs)
2. S3 permissions allow the application to write files
3. Verify `MEDIA_URL` is correctly generated for your domain

### Performance

For better performance:
- Use a CDN in front of your S3 bucket
- Set `AWS_S3_CUSTOM_DOMAIN` to your CDN domain
- Enable S3 static website hosting if desired

## Local Testing with MinIO

To test S3 configuration locally with MinIO:

```bash
# Install MinIO
docker run -it -p 9000:9000 -p 9001:9001 \
  minio/minio server /data --console-address ":9001"

# Set environment variables
export USE_S3=True
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export AWS_STORAGE_BUCKET_NAME=test-bucket
export AWS_S3_ENDPOINT_URL=http://localhost:9000

# Create bucket via MinIO console at http://localhost:9001
# Then run Django normally
python manage.py runserver
```
