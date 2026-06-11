"""
social-trends CLI — viral trend scraping, hashtag optimization,
account auditing, and theme page strategy for YouTube and TikTok.

Usage:
    social-trends trends youtube --region US --limit 20
    social-trends trends tiktok --limit 25
    social-trends trends music --platform both
    social-trends trends all --region US

    social-trends hashtags trending --platform both
    social-trends hashtags generate --niche fitness
    social-trends hashtags analyze "#fitness #gym #workout"
    social-trends hashtags build-set --niche fitness --platform tiktok

    social-trends accounts audit --platform tiktok --followers 5000 --avg-likes 250
    social-trends accounts tiktok-stats @username
    social-trends accounts monetize --platform tiktok --followers 12000 --engagement-rate 4.2
    social-trends accounts best-times --platform tiktok
    social-trends accounts project-growth --followers 2000 --weekly-gain 300

    social-trends theme-pages list-niches
    social-trends theme-pages blueprint luxury_lifestyle
    social-trends theme-pages calendar fitness_motivation --frequency 5x_week
    social-trends theme-pages hooks finance_hustle
    social-trends theme-pages conversions
    social-trends theme-pages analyze-competitor @username --platform tiktok --followers 50000
"""
import click
from social_trends.commands.trends import trends
from social_trends.commands.hashtags import hashtags
from social_trends.commands.accounts import accounts
from social_trends.commands.theme_pages import theme_pages


@click.group()
@click.version_option("1.0.0", prog_name="social-trends")
def cli():
    """
    social-trends — viral trend intelligence for YouTube & TikTok.

    \b
    Modules:
      trends       Fetch trending videos and music
      hashtags     Analyze and generate optimal hashtag sets
      accounts     Audit and optimize social media accounts
      theme-pages  Plan and launch converting niche theme pages

    \b
    Quick start:
      social-trends trends all --region US
      social-trends hashtags generate --niche fitness --platform tiktok
      social-trends theme-pages blueprint luxury_lifestyle
    """


cli.add_command(trends)
cli.add_command(hashtags)
cli.add_command(accounts)
cli.add_command(theme_pages)


if __name__ == "__main__":
    cli()
