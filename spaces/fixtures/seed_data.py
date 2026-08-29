"""
Database seeding script for Espaces Ouverts
Run with: python manage.py shell < spaces/fixtures/seed_data.py
"""
from spaces.models import CareHome, Space
from django.utils import timezone

# Clear existing data
CareHome.objects.all().delete()
Space.objects.all().delete()

# Care Homes data
care_homes_data = [
    {"name": "Alice Prin", "address": "Paris, France"},
    {"name": "La Cascade", "address": "Paris, France"},
    {"name": "EHPAD PEAN", "address": "Paris, France"},
    {"name": "Marcel Bou", "address": "Paris, France"},
    {"name": "Gourlet Bontemps", "address": "Paris, France"},
    {"name": "Résidence Beauregard", "address": "Paris, France"},
    {"name": "Villa Renée", "address": "Paris, France"},
    {"name": "Jardins de Montmartre", "address": "Paris, France"},
    {"name": "JEAN BAPTISTE CARPEAUX", "address": "Paris, France"},

]

# Spaces data (mapping to care homes by name)
spaces_data = [
    {
        "care_home": "Alice Prin",
        "name": "Salle d'animation fermée",
        "availability": "Disponible",
        "description": "Salle d'animation fermée disponible pour les associations"
    },
    {
        "care_home": "La Cascade",
        "name": "Bibliothèque",
        "availability": "Disponible",
        "description": "Bibliothèque moderne avec accès pour associations"
    },
    {
        "care_home": "EHPAD PEAN",
        "name": "Salle polyvalente",
        "availability": "Disponible",
        "description": "Salle polyvalente très spacieuse"
    },
    {
        "care_home": "EHPAD PEAN",
        "name": "Bureau",
        "availability": "Disponible",
        "description": "Bureau équipé pour meetings"
    },
    {
        "care_home": "Marcel Bou",
        "name": "Bibliothèque",
        "availability": "Disponible",
        "description": "Bibliothèque calme et bien équipée"
    },
    {
        "care_home": "Marcel Bou",
        "name": "Salle de Gym",
        "availability": "Disponible",
        "description": "Salle de gym moderne avec équipement"
    },
    {
        "care_home": "Gourlet Bontemps",
        "name": "Salon des familles",
        "availability": "Disponible",
        "description": "Salon chaleureux pour réunions familiales"
    },
    {
        "care_home": "Marcel Bou",
        "name": "Salle de restauration",
        "availability": "Disponible",
        "description": "Salle de restauration équipée de cuisine"
    },
    {
        "care_home": "Résidence Beauregard",
        "name": "Salon",
        "availability": "Disponible",
        "description": "Salon élégant avec vue"
    },
    {
        "care_home": "Villa Renée",
        "name": "Grand salon",
        "availability": "Disponible",
        "description": "Grand salon lumineux"
    },
    {
        "care_home": "Jardins de Montmartre",
        "name": "Salle d'animation",
        "availability": "Disponible",
        "description": "Salle d'animation moderne"
    },
    {
        "care_home": "JEAN BAPTISTE CARPEAUX",
        "name": "Salon du 3 ème étage",
        "availability": "Disponible",
        "description": "Salon au 3ème étage avec vue panoramique"
    },

]

# Create care homes
for ch_data in care_homes_data:
    CareHome.objects.create(name=ch_data["name"], address=ch_data["address"])

# Create spaces
for space_data in spaces_data:
    care_home = CareHome.objects.get(name=space_data["care_home"])
    Space.objects.create(
        care_home=care_home,
        name=space_data["name"],
        availability=space_data["availability"],
        pub_date=timezone.now(),
        description=space_data["description"]
    )

print(f"✓ Seeded {CareHome.objects.count()} care homes")
print(f"✓ Seeded {Space.objects.count()} spaces")
