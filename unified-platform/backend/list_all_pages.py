from cms.models import ProgramPage, LocalProgramPage, LegacyRecreatedPage, City
from django.db.models import Count

def get_verbose_list():
    print("## 🏫 Main Program Pages (Legacy Imports & Core)")
    programs = ProgramPage.objects.all().order_by('title')
    print(f"Total: {programs.count()}")
    print("| Title | Slug | Type |")
    print("| :--- | :--- | :--- |")
    for p in programs:
        print(f"| {p.title} | {p.slug} | {p.program_type} |")
    
    print("\n## 🏺 Legacy Recreated Pages")
    legacy = LegacyRecreatedPage.objects.all().order_by('title')
    print(f"Total: {legacy.count()}")
    print("| Title | Slug | Source URL |")
    print("| :--- | :--- | :--- |")
    for l in legacy:
        print(f"| {l.title} | {l.slug} | {l.source_url} |")

    print("\n## 🤖 Programmatic Local Pages (Phase F.6)")
    local = LocalProgramPage.objects.all().order_by('slug')
    print(f"Total: {local.count()}")
    print("| Slug | Program | City | Office |")
    print("| :--- | :--- | :--- | :--- |")
    for lp in local:
        office_name = lp.assigned_office.name if lp.assigned_office else "None"
        print(f"| {lp.slug} | {lp.program.slug} | {lp.city.name} | {office_name} |")

    print("\n## 📍 Available Cities (Targets for Generation)")
    cities = City.objects.all().order_by('-population')[:20]
    print(f"Total Cities: {City.objects.count()}")
    print("Top 20 by Population:")
    print("| City | Population | Slug |")
    print("| :--- | :--- | :--- |")
    for c in cities:
        print(f"| {c.name}, {c.state} | {c.population or 'N/A'} | {c.slug} |")

if __name__ == "__main__":
    get_verbose_list()
