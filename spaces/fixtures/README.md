# Database Seeding Guide - Espaces Ouverts

This directory contains all the scripts and data needed to seed the Espaces Ouverts database with care homes and spaces from the reference website.

## Files in this Directory

### Seed Scripts

- **`seed_database.py`** - Django management command to seed the database
  - Location: `spaces/management/commands/seed_database.py`
  - Contains all care homes and spaces data
  - Includes proper error handling and status output

- **`seed_data.py`** - Alternative Python seed script
  - Can be run directly: `python manage.py shell < spaces/fixtures/seed_data.py`

### Data Files

- **`spaces_data.json`** - Django JSON fixture
  - Use with: `python manage.py loaddata spaces/fixtures/spaces_data.json`
  - Includes all care homes and spaces

- **`seed_spaces.sql`** - SQL migration script
  - Direct SQL seed file for database

- **`image_manifest.json`** - Mapping of spaces to their images
  - Documents which image files correspond to which spaces

## Data Sourced From

Data was scraped from: **https://espace-ouvert.softr.app/associations**

### Spaces Included (12 total)

1. **Alice Prin** - Salle d'animation fermée
2. **La Cascade** - Bibliothèque
3. **EHPAD PEAN** - Salle polyvalente
4. **EHPAD PEAN** - Bureau
5. **Marcel Bou** - Bibliothèque
6. **Marcel Bou** - Salle de Gym
7. **Gourlet Bontemps** - Salon des familles
8. **Marcel Bou** - Salle de restauration
9. **Résidence Beauregard** - Salon
10. **Villa Renée** - Grand salon
11. **Jardins de Montmartre** - Salle d'animation
12. **JEAN BAPTISTE CARPEAUX** - Salon du 3ème étage

### Care Homes (9 total)

- Alice Prin
- La Cascade
- EHPAD PEAN
- Marcel Bou
- Gourlet Bontemps
- Résidence Beauregard
- Villa Renée
- Jardins de Montmartre
- JEAN BAPTISTE CARPEAUX

## Images

**Location:** `spaces/media/images/`

- Downloaded 10+ space images from the reference website
- Images are stored as JPEG files: `space_image_1.jpg`, `space_image_2.jpg`, etc.
- Image manifest maps spaces to their corresponding image files

## How to Seed the Database

### Option 1: Using Django Management Command (Recommended)

```bash
cd /Users/sgara/GitHub/espaces-ouverts
python manage.py seed_database
```

This will:
- Clear existing care homes and spaces
- Create all 9 care homes
- Create all 12 spaces
- Display progress and confirmation messages

### Option 2: Using Django JSON Fixture

```bash
python manage.py loaddata spaces/fixtures/spaces_data.json
```

### Option 3: Using Django Shell Script

```bash
python manage.py shell < spaces/fixtures/seed_data.py
```

### Option 4: Direct SQL

Execute the SQL commands from `spaces/fixtures/seed_spaces.sql` directly in your database.

## Model Structure

### CareHome Model
```python
class CareHome(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
```

### Space Model
```python
class Space(models.Model):
    care_home = models.ForeignKey(CareHome, on_delete=models.CASCADE)
    name = models.TextField()
    availability = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    description = models.TextField(default="")
```

## Customization

To modify the seed data:

1. **Edit the management command:** `spaces/management/commands/seed_database.py`
   - Update `care_homes_data` list for care homes
   - Update `spaces_data` list for spaces

2. **Regenerate JSON fixture:**
   ```bash
   python manage.py dumpdata spaces > spaces/fixtures/spaces_data.json
   ```

## Notes

- All data is seeded with Paris, France as default address
- Publication dates are set to the current time
- All spaces have "Disponible" (Available) status by default
- Images are downloaded from Airtable URLs and stored locally
- The seed script uses `timezone.now()` for publication dates

## Future Enhancements

Consider adding:
- ImageField to the Space model to store image references
- More detailed space information (capacity, amenities, contact, etc.)
- Filter options (department, city, establishment type)
- Additional metadata from the source website

## Troubleshooting

### Issue: ModuleNotFoundError
Make sure you're in the virtual environment:
```bash
cd /Users/sgara/GitHub/espaces-ouverts
source .venv/bin/activate
```

### Issue: Database errors
Ensure migrations are applied:
```bash
python manage.py migrate
```

### Issue: Images not loading
Verify image files exist in `spaces/media/images/` and check `IMAGE_MANIFEST.json` for correct mappings.
