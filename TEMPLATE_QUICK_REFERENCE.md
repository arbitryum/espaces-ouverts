# Template Quick Reference - Image Display

## Image Display in Templates

### Current Template Usage (spaces/templates/spaces/index.html)
```django
{% if space.image %}
  <img 
    src="{{ space.image.url }}" 
    alt="{{ space.image_alt_text }}"
    class="w-full h-full object-cover">
{% else %}
  <div class="w-full h-full flex items-center justify-center">
    <svg class="w-24 h-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
    </svg>
  </div>
{% endif %}
```

## Template Variables

### Space Object
```python
space.id                  # Primary key
space.name                # Space name (e.g., "Salle d'animation fermée")
space.care_home.name      # Care home name (e.g., "Alice Prin")
space.description         # Space description
space.availability        # Availability status
space.pub_date            # Publication date
space.image               # ImageField object
space.image.url           # Full image URL path
space.image.name          # Stored filename
space.image.size          # File size in bytes
space.image_alt_text      # Accessibility alt text
```

## Usage Examples

### Display Single Space
```django
<figure>
  {% if space.image %}
    <img src="{{ space.image.url }}" alt="{{ space.image_alt_text }}" />
  {% endif %}
</figure>

<h1>{{ space.name }}</h1>
<p>{{ space.care_home.name }}</p>
<p>{{ space.description }}</p>
```

### Display List of Spaces
```django
{% for space in space_list %}
  <div class="space-card">
    {% if space.image %}
      <img src="{{ space.image.url }}" alt="{{ space.image_alt_text }}" />
    {% endif %}
    <h2>{{ space.name }}</h2>
  </div>
{% endfor %}
```

### With Responsive Image
```django
<img 
  src="{{ space.image.url }}" 
  alt="{{ space.image_alt_text }}"
  class="w-full h-auto object-cover"
/>
```

### Picture Element (Multiple Formats)
```django
<picture>
  <source media="(min-width: 1024px)" srcset="{{ space.image.url }}?size=lg">
  <source media="(min-width: 768px)" srcset="{{ space.image.url }}?size=md">
  <img src="{{ space.image.url }}?size=sm" alt="{{ space.image_alt_text }}" />
</picture>
```

## CSS Classes Reference

### Image Styling
```css
/* Full container fit */
.w-full .h-full .object-cover

/* Responsive width */
.w-full .h-auto

/* Fixed aspect ratio */
.aspect-video  /* 16:9 */
.aspect-square /* 1:1 */
.aspect-auto   /* auto */

/* Hover effects */
.hover:opacity-90
.hover:scale-105
.transition-all .duration-300
```

## Responsive Image Heights

| Breakpoint | Classes | Use Case |
|-----------|---------|----------|
| Mobile | `h-32` | 128px |
| Mobile | `h-40` | 160px |
| Mobile | `h-48` | 192px (current) |
| Tablet | `md:h-56` | 224px |
| Desktop | `lg:h-64` | 256px |

## Common Patterns

### Card with Image
```django
<div class="card bg-base-200">
  <div class="h-48 overflow-hidden">
    {% if space.image %}
      <img src="{{ space.image.url }}" alt="{{ space.image_alt_text }}" class="w-full h-full object-cover" />
    {% endif %}
  </div>
  <div class="card-body">
    <h2 class="card-title">{{ space.name }}</h2>
  </div>
</div>
```

### Gallery Grid
```django
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  {% for space in space_list %}
    <div class="space-card">
      {% if space.image %}
        <img src="{{ space.image.url }}" alt="{{ space.image_alt_text }}" class="w-full h-48 object-cover" />
      {% endif %}
    </div>
  {% endfor %}
</div>
```

### Image with Caption
```django
<figure>
  {% if space.image %}
    <img src="{{ space.image.url }}" alt="{{ space.image_alt_text }}" />
  {% endif %}
  <figcaption>{{ space.name }} - {{ space.care_home.name }}</figcaption>
</figure>
```

## Image URLs

### Development (Local Storage)
```
{{ space.image.url }}
→ /media/spaces/2026/08/spaces/space_image_1.jpg
```

### Production (AWS S3)
```
{{ space.image.url }}
→ https://espaces-ouverts.s3.us-east-1.amazonaws.com/media/spaces/2026/08/spaces/space_image_1.jpg
```

## Troubleshooting

### Image Not Displaying
1. Check `space.image` exists: `{{ space.image|default:"No image" }}`
2. Check URL: `{{ space.image.url }}`
3. Verify file exists in media directory
4. Check browser console for 404 errors

### Image Path Wrong
```django
{# Wrong - missing .url #}
<img src="{{ space.image }}" />

{# Right #}
<img src="{{ space.image.url }}" />
```

### Alt Text Missing
```django
{# Should have alt text for accessibility #}
<img src="{{ space.image.url }}" alt="{{ space.image_alt_text }}" />
```

### Image Stretched/Distorted
```django
{# Wrong - stretches image #}
<img src="{{ space.image.url }}" class="w-full h-64" />

{# Right - maintains aspect ratio #}
<img src="{{ space.image.url }}" class="w-full h-64 object-cover" />
```

## Styling Options

### Image Filters
```django
<img 
  src="{{ space.image.url }}" 
  alt="{{ space.image_alt_text }}"
  class="w-full h-full object-cover grayscale hover:grayscale-0"
/>
```

### Image Overlays
```django
<div class="relative w-full h-48 overflow-hidden">
  {% if space.image %}
    <img src="{{ space.image.url }}" alt="{{ space.image_alt_text }}" class="w-full h-full object-cover" />
  {% endif %}
  <div class="absolute inset-0 bg-black bg-opacity-40 hover:bg-opacity-0 transition-all"></div>
</div>
```

### Lazy Loading
```django
<img 
  src="{{ space.image.url }}" 
  alt="{{ space.image_alt_text }}"
  loading="lazy"
  class="w-full h-full object-cover"
/>
```

## Performance Tips

1. **Use `object-cover`** - Prevents upscaling small images
2. **Set fixed heights** - Prevents layout shift
3. **Use lazy loading** - `loading="lazy"`
4. **Compress images** - Keep file sizes reasonable
5. **Use srcset** - Different sizes for different devices

## Current Implementation Status

✅ Database images fully integrated
✅ Template displays images with fallback
✅ Responsive design implemented
✅ Accessibility features added
✅ Hover effects working
✅ Empty state handled
✅ Production ready

## Need Help?

See full documentation:
- `TEMPLATE_UPDATE.md` - Complete update details
- `FILE_STORAGE_GUIDE.md` - Storage configuration
- `SEEDING_QUICKSTART.md` - Database seeding
