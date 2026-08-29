-- Seed data for Espaces Ouverts
-- Care Homes

INSERT INTO spaces_carehome (id, name, address) VALUES (1, 'Alice Prin', 'Paris, France');

INSERT INTO spaces_carehome (id, name, address) VALUES (2, 'La Cascade', 'Paris, France');

INSERT INTO spaces_carehome (id, name, address) VALUES (3, 'EHPAD PEAN', 'Paris, France');

INSERT INTO spaces_carehome (id, name, address) VALUES (4, 'Marcel Bou', 'Paris, France');

INSERT INTO spaces_carehome (id, name, address) VALUES (5, 'Gourlet Bontemps', 'Paris, France');

INSERT INTO spaces_carehome (id, name, address) VALUES (6, 'Résidence Beauregard', 'Paris, France');

INSERT INTO spaces_carehome (id, name, address) VALUES (7, 'Villa Renée', 'Paris, France');

INSERT INTO spaces_carehome (id, name, address) VALUES (8, 'Jardins de Montmartre', 'Paris, France');

INSERT INTO spaces_carehome (id, name, address) VALUES (9, 'JEAN BAPTISTE CARPEAUX', 'Paris, France');

INSERT INTO spaces_space (
    id, 
    care_home_id, 
    name, 
    availability, 
    pub_date, 
    description
) VALUES (
    1, 
    1, 
    'Salle d'animation fermée', 
    'Disponible',
    '2026-08-29T10:02:18.867828',
    'Salle d'animation fermée disponible pour les associations'
);
INSERT INTO spaces_space (
    id, 
    care_home_id, 
    name, 
    availability, 
    pub_date, 
    description
) VALUES (
    2, 
    2, 
    'Bibliothèque', 
    'Disponible',
    '2026-08-29T10:02:18.867840',
    'Bibliothèque moderne avec accès pour associations'
);
INSERT INTO spaces_space (
    id, 
    care_home_id, 
    name, 
    availability, 
    pub_date, 
    description
) VALUES (
    3, 
    3, 
    'Salle polyvalente', 
    'Disponible',
    '2026-08-29T10:02:18.867846',
    'Salle polyvalente très spacieuse'
);
INSERT INTO spaces_space (
    id, 
    care_home_id, 
    name, 
    availability, 
    pub_date, 
    description
) VALUES (
    4, 
    3, 
    'Bureau', 
    'Disponible',
    '2026-08-29T10:02:18.867850',
    'Bureau équipé pour meetings'
);
INSERT INTO spaces_space (
    id, 
    care_home_id, 
    name, 
    availability, 
    pub_date, 
    description
) VALUES (
    5, 
    4, 
    'Bibliothèque', 
    'Disponible',
    '2026-08-29T10:02:18.867853',
    'Bibliothèque calme et bien équipée'
);
INSERT INTO spaces_space (
    id, 
    care_home_id, 
    name, 
    availability, 
    pub_date, 
    description
) VALUES (
    6, 
    4, 
    'Salle de Gym', 
    'Disponible',
    '2026-08-29T10:02:18.867855',
    'Salle de gym moderne avec équipement'
);
INSERT INTO spaces_space (
    id, 
    care_home_id, 
    name, 
    availability, 
    pub_date, 
    description
) VALUES (
    7, 
    5, 
    'Salon des familles', 
    'Disponible',
    '2026-08-29T10:02:18.867858',
    'Salon chaleureux pour réunions familiales'
);
INSERT INTO spaces_space (
    id, 
    care_home_id, 
    name, 
    availability, 
    pub_date, 
    description
) VALUES (
    8, 
    4, 
    'Salle de restauration', 
    'Disponible',
    '2026-08-29T10:02:18.867860',
    'Salle de restauration équipée de cuisine'
);
INSERT INTO spaces_space (
    id, 
    care_home_id, 
    name, 
    availability, 
    pub_date, 
    description
) VALUES (
    9, 
    6, 
    'Salon', 
    'Disponible',
    '2026-08-29T10:02:18.867862',
    'Salon élégant avec vue'
);
INSERT INTO spaces_space (
    id, 
    care_home_id, 
    name, 
    availability, 
    pub_date, 
    description
) VALUES (
    10, 
    7, 
    'Grand salon', 
    'Disponible',
    '2026-08-29T10:02:18.867863',
    'Grand salon lumineux'
);
INSERT INTO spaces_space (
    id, 
    care_home_id, 
    name, 
    availability, 
    pub_date, 
    description
) VALUES (
    11, 
    8, 
    'Salle d'animation', 
    'Disponible',
    '2026-08-29T10:02:18.867866',
    'Salle d'animation moderne'
);
INSERT INTO spaces_space (
    id, 
    care_home_id, 
    name, 
    availability, 
    pub_date, 
    description
) VALUES (
    12, 
    9, 
    'Salon du 3 ème étage', 
    'Disponible',
    '2026-08-29T10:02:18.867868',
    'Salon au 3ème étage avec vue panoramique'
);