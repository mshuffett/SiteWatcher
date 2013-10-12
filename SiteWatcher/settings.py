# Scrapy settings for SiteWatcher project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'SiteWatcher'

SPIDER_MODULES = ['SiteWatcher.spiders']
NEWSPIDER_MODULE = 'SiteWatcher.spiders'

ITEM_PIPELINES = ['SiteWatcher.pipelines.SitewatcherPipeline']
ROOT_DIR = '/home/michael/Dropbox/ws/SiteWatcher'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'SiteWatcher (+http://www.yourdomain.com)'
