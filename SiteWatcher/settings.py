# Scrapy settings for SiteWatcher project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
# Crawl responsibly by identifying yourself
# (and your website) on the user-agent
# USER_AGENT = 'SiteWatcher (+http://www.yourdomain.com)'

from scrapy import log

BOT_NAME = 'SiteWatcher'

SPIDER_MODULES = ['SiteWatcher.spiders']
NEWSPIDER_MODULE = 'SiteWatcher.spiders'

ITEM_PIPELINES = ['SiteWatcher.pipelines.SitewatcherPipeline']
EXTENSIONS = {'SiteWatcher.extensions.StatusMailer': 80}
ROOT_DIR = '/home/michael/Dropbox/ws/SiteWatcher'

# user_settings takes precedence over these settings
try:
    from user_settings import *
except ImportError as e:
    log.msg("No user_settings.py file present. Using default settings.",
            level=log.WARNING)
