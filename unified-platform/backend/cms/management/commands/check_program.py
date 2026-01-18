from django.core.management.base import BaseCommand
from cms.models import ProgramPage
from wagtail.models import Site


class Command(BaseCommand):
    help = 'Check a specific program status'

    def handle(self, *args, **options):
        site = Site.objects.get(is_default_site=True)

        prog = ProgramPage.objects.filter(title__icontains='Stated Income').first()
        if prog:
            self.stdout.write(f"Program: {prog.title}")
            self.stdout.write(f"ID: {prog.id}")
            parent = prog.get_parent()
            self.stdout.write(f"Parent: {parent.title} (ID: {parent.id})")
            self.stdout.write(f"Parent Type: {parent.content_type}")
            self.stdout.write(f"Under site root: {prog.is_descendant_of(site.root_page)}")
            self.stdout.write(f"Published: {prog.live}")
        else:
            self.stdout.write("No program found")
