# Backend Recovery & Self-Healing Guide

This document outlines how to recover the Unified Platform backend content (Loan Programs, Menu, etc.) if the database is reset or content is lost.

## 1. Automated Self-Healing
The system is configured to check for core content on every startup via `entrypoint.sh`. 

If it detects an "empty" state (no Navigation Menu or no Program Index), it will automatically run:
1. `import_wordpress` (Imports legacy content)
2. `populate_navigation` (Rebuilds headers)
3. `populate_home_features` (Seeds home page data)
4. `seed_sample_cities` (Seeds SEO location data)
5. `create_program_shells` (Ensures 2025 program hierarchy exists)

## 2. Manual Recovery Commands
If you need to manually force a full rebuild, run the following commands inside the backend container:

```bash
# Wipe and re-import everything
python manage.py import_wordpress --wipe
python manage.py populate_navigation
python manage.py populate_home_features
python manage.py seed_sample_cities
python manage.py create_program_shells
```

## 3. Data Integrity Verification
To verify the system is healthy, run the Sanity Check:

```bash
python scripts/sanity_check.py
```

This test checks:
- [x] Program Index Page exists
- [x] At least 60+ Programs are live
- [x] Main Header Navigation Menu is populated
- [x] SEO Cities are seeded

## 4. Troubleshooting Missing Menu
If the frontend shows a pulse/loading state or error in the header, first check the API endpoint:
`URL: /api/v1/navigation/Main Header/`

If it returns `[]` or `404`, run:
```bash
python manage.py populate_navigation
```

## 5. Deployment Persistence
Ensure the Docker volume for the database is persistent. In `docker-compose.yml`, the database service should mount a volume to `/var/lib/postgresql/data`.
