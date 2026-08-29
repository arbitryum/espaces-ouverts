# Quick Reference - Multiple Images Changes

## Model Changes

### Before (Old)
```python
class Space(models.Model):
    care_home = models.ForeignKey(CareHome, on_delete=models.CASCADE)
    name = models.TextField()
    availability = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    description = models.TextField(default="")
    image = models.ImageField(                    # ❌ Removed
        upload_to='spaces/%Y/%m/',
        null=True,
        blank=True,
        help_text="Photo of the space"
    )
    image_alt_text = models.CharField(            # ❌ Removed
        max_length=500,
        blank=True,
        default="",
        help_text="Alternative text for the image"
    )
```

### After (New)
```python
class Space(models.Model):
    care_home = models.ForeignKey(CareHome, on_delete=models.CASCADE)
    name = models.TextField()
    availability = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    description = models.TextField(default="")
    
    def get_first_image(self):                    # ✅ Added
        """Returns the first image for this space, or None if no images exist."""
        return self.images.first()


class SpaceImage(models.Model):                   # ✅ New Model
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='spaces/%Y/%m/',
        help_text="Photo of the space"
    )
    alt_text = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Alternative text for the image"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order (lower numbers appear first)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.space.name} - Image {self.order}"
```

## Template Changes

### Before
```django
{% if space.image %}
  <img 
    src="{{ space.image.url }}" 
    alt="{{ space.image_alt_text }}"
    class="w-full h-full object-cover">
{% else %}
  <div class="w-full h-full flex items-center justify-center">
    <svg class="w-24 h-24 text-gray-400" ...>
      <!-- Picture frame icon -->
    </svg>
  </div>
{% endif %}
```

### After
```django
{% with first_image=space.get_first_image %}
  {% if first_image %}
    <img 
      src="{{ first_image.image.url }}" 
      alt="{{ first_image.alt_text }}"
      class="w-full h-full object-cover">
  {% else %}
    <div class="w-full h-full flex items-center justify-center">
      <svg class="w-24 h-24 text-gray-400" ...>
        <!-- Picture frame icon -->
      </svg>
    </div>
  {% endif %}
{% endwith %}
```

## Seed Script Changes

### Before
```python
from spaces.models import CareHome, Space

# In space creation loop:
space = Space.objects.create(
    care_home=care_home,
    name=space_data["name"],
    availability=space_data["availability"],
    pub_date=timezone.now(),
    description=space_data["description"],
    image_alt_text=space_data["image_alt"]  # ❌ Removed
)

# Image attachment:
with open(image_path, 'rb') as f:
    space.image.save(                        # ❌ Changed
        f'spaces/{space_data["image"]}',
        ContentFile(f.read()),
        save=True
    )
```

### After
```python
from spaces.models import CareHome, Space, SpaceImage  # ✅ Added SpaceImage

# In space creation loop:
space = Space.objects.create(
    care_home=care_home,
    name=space_data["name"],
    availability=space_data["availability"],
    pub_date=timezone.now(),
    description=space_data["description"],
    # ✅ No image_alt_text here
)

# Image attachment:
with open(image_path, 'rb') as f:
    space_image = SpaceImage.objects.create(  # ✅ Create SpaceImage
        space=space,
        alt_text=space_data["image_alt"],
        order=0
    )
    space_image.image.save(                   # ✅ Save to SpaceImage
        f'spaces/{space_data["image"]}',
        ContentFile(f.read()),
        save=True
    )
```

## Python Usage Changes

### Before
```python
# Get image
space.image              # ImageFieldFile object or None
space.image.url         # URL string
space.image_alt_text    # Alt text string

# Check if has image
if space.image:
    print(space.image.url)
```

### After
```python
# Get first image
first_img = space.get_first_image()  # SpaceImage object or None
first_img.image.url                  # URL string
first_img.alt_text                   # Alt text string

# Check if has image
if space.get_first_image():
    print(space.get_first_image().image.url)

# Or more concise:
first = space.images.first()
if first:
    print(first.image.url)

# Get all images
for img in space.images.all():
    print(img.order, img.image.url, img.alt_text)

# Count images
space.images.count()  # Returns: 1 (currently all have 1)
```

## Database Changes

### Before
```sql
-- Space table with 2 image columns:
CREATE TABLE spaces_space (
    id BIGINT PRIMARY KEY,
    care_home_id INT,
    name TEXT,
    availability VARCHAR(200),
    pub_date DATETIME,
    description TEXT,
    image VARCHAR(200),              -- ❌ Removed
    image_alt_text VARCHAR(500),     -- ❌ Removed
    ...
);
```

### After
```sql
-- Space table (image columns removed):
CREATE TABLE spaces_space (
    id BIGINT PRIMARY KEY,
    care_home_id INT,
    name TEXT,
    availability VARCHAR(200),
    pub_date DATETIME,
    description TEXT,
    ...
);

-- New SpaceImage table:              ✅ Created
CREATE TABLE spaces_spaceimage (
    id BIGINT PRIMARY KEY,
    space_id BIGINT,
    image VARCHAR(200),
    alt_text VARCHAR(500),
    order INT DEFAULT 0,
    created_at DATETIME,
    FOREIGN KEY (space_id) REFERENCES spaces_space(id)
);

CREATE INDEX spaces_spaceimage_space_id ON spaces_spaceimage(space_id);
CREATE INDEX spaces_spaceimage_order ON spaces_spaceimage(order);
```

## API/Django Admin Changes

### Before
```
Space Admin:
├─ Fields: id, care_home, name, availability, image, image_alt_text, ...
└─ Image: Upload field for single image

Query:
space.image                    # Access image
space.image_alt_text           # Access alt text
```

### After
```
Space Admin:
├─ Fields: id, care_home, name, availability, ...
└─ Inline: SpaceImage (multiple records, sortable by order)

SpaceImage Admin:
├─ Fields: id, space, image, alt_text, order, created_at
└─ Upload: Multiple images per space

Query:
space.images.all()             # Get all SpaceImage records
space.get_first_image()        # Get first SpaceImage
space.images.filter(order=0)   # Get by order
```

## Migration Path

### For Custom Code

**If you had this code**:
```python
# ❌ No longer works
space.image
space.image.url
space.image_alt_text
if space.image:
    ...
```

**Update to this**:
```python
# ✅ Updated code
first_img = space.get_first_image()
first_img.image.url
first_img.alt_text
if first_img:
    ...
```

**Or use related manager**:
```python
# ✅ Also valid
space.images.first()
space.images.filter(order=0).first()
space.images.count()
for img in space.images.all():
    ...
```

## Backward Compatibility

✅ **Fully backward compatible if using convenience method**:
```django
{# Old: space.image #}
{# New: space.get_first_image() #}

{# Works the same way #}
```

⚠️ **Breaking change if directly accessing old fields**:
```python
# ❌ These no longer exist:
space.image
space.image_alt_text

# ✅ Use these instead:
space.get_first_image()
space.images.all()
```

## Summary of Changes

| What | Before | After | Status |
|------|--------|-------|--------|
| Single image field | `Space.image` | Removed | ✅ Removed |
| Alt text field | `Space.image_alt_text` | Removed | ✅ Removed |
| Multiple images | Not supported | `Space.images` relation | ✅ Supported |
| First image | `space.image` | `space.get_first_image()` | ✅ Added |
| SpaceImage model | Didn't exist | New model | ✅ Created |
| Image ordering | N/A | `SpaceImage.order` | ✅ Added |
| Migration | N/A | 0005_*.py | ✅ Applied |
| Seed script | Old format | New format | ✅ Updated |
| Template | Old syntax | New syntax | ✅ Updated |

## Testing Commands

```bash
# Check migration applied
python manage.py showmigrations spaces

# Run shell to test
python manage.py shell

# In shell:
>>> from spaces.models import Space, SpaceImage
>>> Space.objects.count()        # Should be 12
>>> SpaceImage.objects.count()   # Should be 12
>>> space = Space.objects.first()
>>> space.get_first_image()      # Should return SpaceImage
>>> space.images.count()         # Should be 1
>>> first = space.get_first_image()
>>> print(first.image.url)       # Should print URL
>>> print(first.alt_text)        # Should print alt text

# Test template
python manage.py runserver
# Visit http://localhost:8000/spaces/
```
