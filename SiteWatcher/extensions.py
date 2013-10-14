# Addapted from http://stackoverflow.com/questions/16260753/emailing-items-and-logs-with-scrapy

import gzip
import datetime

from scrapy import signals
from scrapy.mail import MailSender
from scrapy.exceptions import NotConfigured
from scrapy.utils.serialize import ScrapyJSONEncoder

from collections import defaultdict

try:
    from cStringIO import cStringIO as StringIO
except ImportError:
    from StringIO import StringIO


def format_size(size):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)

        size /= 1024.0


class GzipCompressor(gzip.GzipFile):
    extension = '.gz'
    mimetype = 'application/gzip'

    def __init__(self):
        super(GzipCompressor, self).__init__(fileobj=PlainCompressor(),
                                             mode='w')
        self.read = self.fileobj.read


class PlainCompressor(StringIO):
    extension = ''
    mimetype = 'text/plain'

    def read(self, *args, **kwargs):
        self.seek(0)

        return StringIO.read(self, *args, **kwargs)

    @property
    def size(self):
        return len(self.getvalue())


class StatusMailer(object):
    def __init__(self, recipients, mail, compressor, crawler):
        self.recipients = recipients
        self.mail = mail
        self.encoder = ScrapyJSONEncoder(crawler=crawler)
        self.files = defaultdict(compressor)

        self.num_items = 0
        self.num_errors = 0

    @classmethod
    def from_crawler(cls, crawler):
        recipients = crawler.settings.getlist('STATUSMAILER_RECIPIENTS')
        compression = crawler.settings.get('STATUSMAILER_COMPRESSION')

        if not compression:
            compressor = PlainCompressor
        elif compression.lower().startswith('gz'):
            compressor = GzipCompressor
        else:
            raise NotConfigured

        if not recipients:
            raise NotConfigured

        mail = MailSender.from_settings(crawler.settings)
        instance = cls(recipients, mail, compressor, crawler)

        # Default to False
        instance.mail_items = crawler.settings.get('STATUSMAILER_MAIL_ITEMS',
                                                   False)
        if instance.mail_items:
            crawler.signals.connect(instance.item_scraped,
                                    signal=signals.item_scraped)
        instance.mail_requests = crawler.settings.get(
            'STATUSMAILER_MAIL_REQUESTS',
            False)
        if instance.mail_requests:
            crawler.signals.connect(instance.request_received,
                                    signal=signals.request_received)

        # Default to True
        instance.mail_errors = crawler.settings.get(
            'STATUSMAILER_MAIL_ERRORS',
            True)
        if instance.mail_errors:
            crawler.signals.connect(instance.spider_error,
                                    signal=signals.spider_error)

        if (instance.mail_items or instance.mail_requests or
                instance.mail_errors):
            crawler.signals.connect(instance.spider_closed,
                                    signal=signals.spider_closed)

        return instance

    def item_scraped(self, item, response, spider):
        self.files[spider.name + '-items.json'].write(
            self.encoder.encode(item))
        self.num_items += 1

    def spider_error(self, failure, response, spider):
        self.files[spider.name + '-errors.log'].write(failure.getTraceback())
        self.num_errors += 1

    def request_received(self, request, spider):
        self.files[spider.name + '-requests.log'].write(str(request) + '\n')

    def spider_closed(self, spider, reason):
        files = []

        for name, compressed in self.files.items():
            files.append((name + compressed.extension,
                          compressed.mimetype, compressed))

        body_items = ['Crawl statistics:\n\n'
                      ' - Spider name: {}\n'
                      ' - Spider finished at: {}'
                      .format(spider.name, datetime.datetime.now())]

        if self.mail_items:
            try:
                size = self.files[spider.name + '-items.json'].size
            except KeyError:
                size = 0
            body_items.append('\n - Number of items scraped: {}'
                              '\n - Size of scraped items: {}'
                              .format(self.num_items, format_size(size)))

        if self.mail_errors:
            body_items.append('\n - Number of errors: {}'
                              .format(self.num_errors))

        body = ''.join(body_items)

        return self.mail.send(
            to=self.recipients,
            subject='Crawler for %s: %s' % (spider.name, reason),
            body=body,
            attachs=files
        )
