"""
Management command to initialize job sources.
"""

from django.core.management.base import BaseCommand
from apps.jobs.models import JobSource


class Command(BaseCommand):
    help = 'Initialize job sources'

    def handle(self, *args, **options):
        sources = [
            {
                'name': 'LinkedIn',
                'base_url': 'https://www.linkedin.com/jobs',
                'is_active': True
            },
            {
                'name': 'Indeed',
                'base_url': 'https://www.indeed.com',
                'is_active': True
            },
            {
                'name': 'Glassdoor',
                'base_url': 'https://www.glassdoor.com',
                'is_active': True
            },
            {
                'name': 'RemoteOK',
                'base_url': 'https://remoteok.com',
                'is_active': True
            }
        ]

        created_count = 0
        for source_data in sources:
            source, created = JobSource.objects.get_or_create(
                name=source_data['name'],
                defaults=source_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created job source: {source.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Job source already exists: {source.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully initialized {created_count} job sources')
        )
