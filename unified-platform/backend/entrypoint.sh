#!/bin/sh

# Wait for DB
# (Add wait-for-it logic here if needed)

# Run Migrations
python manage.py migrate

# Create Superuser (Idempotent)
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

# Run Integrity Check and Self-Heal (Only for Web)
if [ "$SERVICE_TYPE" = "web" ]; then
    python scripts/self_heal.py
    python manage.py collectstatic --noinput
fi

# Start Server
exec "$@"
