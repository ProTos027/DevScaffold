"""
Management command to set up GitHub OAuth SocialApp from environment variables.
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
from allauth.socialaccount.models import SocialApp
from decouple import config


class Command(BaseCommand):
    help = 'Setup GitHub OAuth SocialApp using credentials from .env'

    def handle(self, *args, **options):
        # Configure the current site
        site = Site.objects.get_current()
        site.domain = settings.SITE_DOMAIN
        site.name = settings.SITE_NAME
        site.save()
        self.stdout.write(f'Site configured: {site.domain}')

        # Read real credentials from environment
        client_id = config('GITHUB_CLIENT_ID', default='').strip()
        client_secret = config('GITHUB_CLIENT_SECRET', default='').strip()

        if not client_id or not client_secret:
            self.stdout.write(self.style.ERROR(
                'GITHUB_CLIENT_ID or GITHUB_CLIENT_SECRET not set in .env — cannot configure OAuth.'
            ))
            return

        # Create or update GitHub SocialApp with real credentials
        github_app, created = SocialApp.objects.get_or_create(provider='github', defaults={'name': 'GitHub'})
        github_app.name = 'GitHub'
        github_app.client_id = client_id
        github_app.secret = client_secret
        github_app.save()

        # Associate with site
        github_app.sites.add(site)

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{action} GitHub SocialApp with client_id: {client_id[:8]}...'
        ))
