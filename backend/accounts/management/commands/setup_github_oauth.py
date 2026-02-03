"""
Management command to set up GitHub OAuth without needing credentials.
For development, we'll create a placeholder SocialApp.
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Setup GitHub OAuth SocialApp for development (placeholder)'

    def handle(self, *args, **options):
        # Get or create the current site
        site = Site.objects.get_current()
        site.domain = 'localhost:8000'
        site.name = 'DevScaffold'
        site.save()
        
        self.stdout.write(f'Site configured: {site.domain}')
        
        # Create or update GitHub SocialApp
        github_app, created = SocialApp.objects.get_or_create(
            provider='github',
            defaults={
                'name': 'GitHub',
                'client_id': 'placeholder_client_id',
                'secret': 'placeholder_secret',
            }
        )
        
        if not created:
            github_app.client_id = 'placeholder_client_id'
            github_app.secret = 'placeholder_secret'
            github_app.save()
        
        # Associate with site
        github_app.sites.add(site)
        
        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{action} GitHub SocialApp (placeholder - configure with real credentials in .env)'
        ))
        
        self.stdout.write(self.style.WARNING(
            '\nTo use GitHub OAuth, add your credentials to .env:'
        ))
        self.stdout.write('GITHUB_CLIENT_ID=your_client_id')
        self.stdout.write('GITHUB_CLIENT_SECRET=your_client_secret')
