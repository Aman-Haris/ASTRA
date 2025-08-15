-- 1. Get all potentially hazardous asteroids
SELECT * FROM asteroids 
WHERE hazardous = TRUE
ORDER BY close_approach_date;

-- 2. Get close approaches within the next year
SELECT name, close_approach_date, miss_distance_km 
FROM asteroids
WHERE close_approach_date BETWEEN NOW() AND NOW() + INTERVAL '1 year'
ORDER BY miss_distance_km ASC;

-- 3. Get asteroids with unusual orbits (comet-like)
SELECT name, orbital_eccentricity, orbital_inclination 
FROM asteroids
WHERE orbital_eccentricity > 0.9 OR orbital_inclination > 20;

-- 4. Get training dataset for GNN
SELECT 
    id, name,
    diameter_km, orbital_eccentricity, orbital_inclination,
    orbital_semi_major_axis, tisserand, palermo_scale,
    miss_distance_km, velocity_km_s,
    close_approach_date
FROM asteroids
WHERE 
    miss_distance_km IS NOT NULL AND
    velocity_km_s IS NOT NULL;

-- 5. Update threat scores (run after preprocessing)
UPDATE asteroids a
SET 
    palermo_scale = p.palermo_scale,
    torino_scale = p.torino_scale
FROM processed_asteroids p
WHERE a.id = p.id;