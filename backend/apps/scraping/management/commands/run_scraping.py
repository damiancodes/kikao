"""
Management command to run job scraping.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.scraping.tasks import scrape_jobs_task
from apps.scraping.models import ScrapingSession
from apps.jobs.models import JobSource


class Command(BaseCommand):
    help = 'Run job scraping for specified parameters'

    def add_arguments(self, parser):
        parser.add_argument(
            '--query',
            type=str,
            default='Data Analyst',
            help='Job search query (default: Data Analyst)'
        )
        parser.add_argument(
            '--location',
            type=str,
            default='USA',
            help='Job search location (default: USA)'
        )
        parser.add_argument(
            '--max-results',
            type=int,
            default=50,
            help='Maximum number of results to scrape (default: 50)'
        )
        parser.add_argument(
            '--sources',
            type=str,
            nargs='+',
            help='Specific sources to scrape (e.g., indeed glassdoor)'
        )
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run scraping asynchronously using Celery'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )

    def handle(self, *args, **options):
        query = options['query']
        location = options['location']
        max_results = options['max_results']
        sources = options.get('sources', [])
        run_async = options['async']
        verbose = options['verbose']

        if verbose:
            self.stdout.write(
                self.style.SUCCESS(f'Starting scraping with parameters:')
            )
            self.stdout.write(f'  Query: {query}')
            self.stdout.write(f'  Location: {location}')
            self.stdout.write(f'  Max Results: {max_results}')
            self.stdout.write(f'  Sources: {sources if sources else "All active sources"}')
            self.stdout.write(f'  Async: {run_async}')

        # Get active sources
        if sources:
            active_sources = JobSource.objects.filter(
                name__in=sources,
                is_active=True
            )
            if not active_sources.exists():
                raise CommandError(f'No active sources found for: {sources}')
        else:
            active_sources = JobSource.objects.filter(is_active=True)
            if not active_sources.exists():
                raise CommandError('No active sources found. Please add sources first.')

        if verbose:
            self.stdout.write(f'  Active sources: {[s.name for s in active_sources]}')

        # Create scraping session
        session = ScrapingSession.objects.create(
            query=query,
            location=location,
            max_results=max_results,
            status='pending'
        )

        if verbose:
            self.stdout.write(f'Created scraping session: {session.id}')

        if run_async:
            # Run asynchronously using Celery
            task = scrape_jobs_task.delay(
                query=query,
                location=location,
                max_results=max_results,
                source_ids=list(active_sources.values_list('id', flat=True))
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Scraping task queued with ID: {task.id}')
            )
            self.stdout.write(f'Session ID: {session.id}')
            self.stdout.write('Use "docker-compose logs -f celery" to monitor progress')
        else:
            # Run synchronously
            self.stdout.write('Running scraping synchronously...')
            try:
                result = scrape_jobs_task(
                    query=query,
                    location=location,
                    max_results=max_results,
                    source_ids=list(active_sources.values_list('id', flat=True))
                )
                
                if result:
                    self.stdout.write(
                        self.style.SUCCESS(f'Scraping completed successfully!')
                    )
                    self.stdout.write(f'Jobs found: {result.get("jobs_found", 0)}')
                    self.stdout.write(f'Errors: {result.get("errors", 0)}')
                else:
                    self.stdout.write(
                        self.style.WARNING('Scraping completed but no results returned')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Scraping failed: {str(e)}')
                )
                raise CommandError(f'Scraping failed: {str(e)}')

        # Show recent sessions
        if verbose:
            self.stdout.write('\nRecent scraping sessions:')
            recent_sessions = ScrapingSession.objects.order_by('-created_at')[:5]
            for sess in recent_sessions:
                status_color = {
                    'completed': self.style.SUCCESS,
                    'failed': self.style.ERROR,
                    'running': self.style.WARNING,
                    'pending': self.style.NOTICE,
                }.get(sess.status, self.style.NOTICE)
                
                self.stdout.write(
                    f'  {sess.id}: {sess.query} - {status_color(sess.status)} '
                    f'({sess.jobs_found} jobs)'
                )
