"""
Management command to clean up expired project repositories.

Usage:
    python manage.py cleanup_repos
    python manage.py cleanup_repos --dry-run
"""
from django.core.management.base import BaseCommand
from storage.manager import cleanup_expired_repositories
from projects.models import Project
from django.utils import timezone


class Command(BaseCommand):
    help = 'Delete expired project repositories based on deletion_scheduled_at timestamp.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview which repos would be deleted without actually deleting them.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        now = timezone.now()
        expired = Project.objects.filter(
            deletion_scheduled_at__lte=now,
            status='completed'
        )

        count = expired.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('No expired repositories found.'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(f'[DRY RUN] {count} repo(s) would be deleted:'))
            for project in expired:
                self.stdout.write(
                    f'  - Project {project.id} ({project.name or "Unnamed"}) | '
                    f'Scheduled: {project.deletion_scheduled_at} | '
                    f'Dir: {project.repo_directory}'
                )
        else:
            deleted = cleanup_expired_repositories()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully cleaned up {deleted} expired repo(s).')
            )
