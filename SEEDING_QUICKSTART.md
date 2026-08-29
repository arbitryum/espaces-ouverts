# Quick Start - Seeding the Database

## One-Command Setup

```bash
cd /Users/sgara/GitHub/espaces-ouverts
python manage.py seed_database
```

That's it! This will populate your database with:
- ✓ 9 Care Homes (Alice Prin, La Cascade, EHPAD PEAN, etc.)
- ✓ 12 Spaces (various rooms, libraries, salons, etc.)
- ✓ 10+ Space images (automatically linked to database)

## What Was Collected

### Data Source
- **Website:** https://espace-ouvert.softr.app/associations
- **Collection Method:** Web scraping + browser automation
- **Date Collected:** 2026-08-29

### Spaces Dataset (12 entries)
1. Alice Prin - Salle d'animation fermée
2. La Cascade - Bibliothèque  
3. EHPAD PEAN - Salle polyvalente
4. EHPAD PEAN - Bureau
5. Marcel Bou - Bibliothèque
6. Marcel Bou - Salle de Gym
7. Gourlet Bontemps - Salon des familles
8. Marcel Bou - Salle de restauration
9. Résidence Beauregard - Salon
10. Villa Renée - Grand salon
11. Jardins de Montmartre - Salle d'animation
12. JEAN BAPTISTE CARPEAUX - Salon du 3ème étage

### Images (10 files)
- **Automatically linked** to spaces in database
- **Stored locally** in `media/spaces/YYYY/MM/spaces/` during development
- **Can be stored on S3** for production by setting `USE_S3=True`
- **Optimized for web** - JPEG format, ~1MB each

## Files Created

### Database & Fixtures
- [spaces/fixtures/seed_database.py](spaces/fixtures/seed_database.py) - Python seed script
- [spaces/fixtures/seed_spaces.sql](spaces/fixtures/seed_spaces.sql) - SQL seed commands
- [spaces/fixtures/spaces_data.json](spaces/fixtures/spaces_data.json) - Django JSON fixture
- [spaces/management/commands/seed_database.py](spaces/management/commands/seed_database.py) - Django management command ⭐ (Recommended)

### Configuration & Documentation
- [FILE_STORAGE_GUIDE.md](FILE_STORAGE_GUIDE.md) - Complete file storage setup
- [spaces/fixtures/README.md](spaces/fixtures/README.md) - Database seeding reference
- [.env.template](.env.template) - Environment configuration template

### Images & Media
- `spaces/media/images/space_image_*.jpg` - Original downloaded images (source)
- `media/spaces/YYYY/MM/spaces/` - Processed images linked to database (storage)

## File Storage Setup

### Development (Default)
Files are stored locally on your filesystem:

```
media/
└── spaces/
    └── 2026/08/
        └── spaces/
            ├── space_image_1.jpg
            ├── space_image_2.jpg
            └── ...
```

**No configuration needed** - just run the seed command!

### Production (AWS S3)
For production deployment, images can be automatically stored on AWS S3:

```bash
export USE_S3=True
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_STORAGE_BUCKET_NAME=espaces-ouverts
export AWS_S3_REGION_NAME=us-east-1
```

See [FILE_STORAGE_GUIDE.md](FILE_STORAGE_GUIDE.md) for detailed S3 configuration.

## Model Structure

### Space Model (with Images)
```python
class Space(models.Model):
    care_home = models.ForeignKey(CareHome, on_delete=models.CASCADE)
    name = models.TextField()
    availability = models.CharField(max_length=200)
    pub_date = models.DateTimeField()
    description = models.TextField()
    image = models.ImageField(upload_to='spaces/%Y/%m/', null=True, blank=True)
    image_alt_text = models.CharField(max_length=500, blank=True)
```

## Next Steps

1. **Run the seed command:**
   ```bash
   python manage.py seed_database
   ```

2. **View the data in Django admin:**
   ```bash
   python manage.py runserver
   # Visit http://localhost:8000/admin
   ```

3. **Display spaces with images in templates:**
   ```django
   {% for space in spaces %}
     <div class="card">
       {% if space.image %}
         <img src="{{ space.image.url }}" alt="{{ space.image_alt_text }}" />
       {% endif %}
       <h3>{{ space.name }}</h3>
       <p>{{ space.description }}</p>
     </div>
   {% endfor %}
   ```

## Usage Examples

### In Django Templates
```django
{% for space in spaces %}
  <article class="space-card">
    {% if space.image %}
      <img src="{{ space.image.url }}" alt="{{ space.image_alt_text }}" />
    {% endif %}
    <h2>{{ space.name }}</h2>
    <p>{{ space.description }}</p>
    <p class="meta">{{ space.care_home.name }}</p>
  </article>
{% endfor %}
```

### In Django Views
```python
from spaces.models import Space, CareHome

# Get all spaces with images
spaces = Space.objects.filter(image__isnull=False)

# Get spaces by care home
care_home = CareHome.objects.get(name="Alice Prin")
spaces = care_home.space_set.all()

# Filter by availability and get paginated results
from django.core.paginator import Paginator
available = Space.objects.filter(availability="Disponible")
paginator = Paginator(available, 12)  # 12 per page
page_obj = paginator.get_page(request.GET.get('page'))
```

### Access Images Programmatically
```python
space = Space.objects.get(id=1)

# Get image URL
if space.image:
    url = space.image.url  # /media/spaces/2026/08/spaces/image.jpg
    path = space.image.path  # Full filesystem path
    size = space.image.size  # File size in bytes
    name = space.image.name  # Stored filename
```

## Troubleshooting

**Q: Images not appearing in admin?**  
A: Run `python manage.py collectstatic` and ensure `MEDIA_ROOT` is configured correctly.

**Q: "ModuleNotFoundError: No module named 'storages'"**  
A: Install dependencies: `pip install -r requirements.txt`

**Q: Images uploaded but not persisting?**  
A: Check that `.gitignore` includes `media/` so files aren't accidentally deleted.

**Q: Want to use S3 instead of local storage?**  
A: See [FILE_STORAGE_GUIDE.md](FILE_STORAGE_GUIDE.md) for production S3 setup.

## Reference

- [FILE_STORAGE_GUIDE.md](FILE_STORAGE_GUIDE.md) - Complete file storage documentation
- [spaces/fixtures/README.md](spaces/fixtures/README.md) - Database seeding reference
- [spaces/models.py](spaces/models.py) - Space model definition
