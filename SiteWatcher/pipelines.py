# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import log
import os
import sqlite3
import smtplib


class SitewatcherPipeline(object):
    def __init__(self, settings):
        self.new_titles = []

        self.settings = settings

        root_dir = settings['ROOT_DIR']
        path = os.path.join(root_dir, 'sitewatcher.db')

        self.conn = sqlite3.connect(path)
        log.msg('Using database %s' % path)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS
                             games(title TEXT PRIMARY KEY)''')

    def process_item(self, item, spider):
        title = item['title']
        count = self.conn.execute('SELECT count(*) FROM games WHERE title = ?',
                                  (title,)).fetchone()[0]
        if count == 0:
            log.msg('New game %s found.' % title)
            self.new_titles.append(title)
            with self.conn:
                self.conn.execute('INSERT INTO games VALUES(?)', (title,))
        else:
            log.msg('%s was previously seen.' % title)

        return item

    def sendemail(self, from_addr, to_addrs,
                  subject, message,
                  login, password,
                  smtpserver='smtp.gmail.com:587'):
        log.msg('Alerting %s about new items' % ', '.join(to_addrs))

        header = 'From: %s\n' % from_addr
        header += 'To: %s\n' % ', '.join(to_addrs)
        header += 'Subject: %s\n\n' % subject
        message = header + message

        server = smtplib.SMTP(smtpserver)
        server.starttls()
        server.login(login, password)
        problems = server.sendmail(from_addr, to_addrs, message)
        if problems:
            log.msg('Problem sending email %s' % problems, level=log.ERROR)
        else:
            log.msg('Email sent successfully')

        server.quit()

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

        if self.new_titles:
            self.sendemail(
                from_addr=self.settings['MAIL_FROM'],
                to_addrs=self.settings.getlist('STATUSMAILER_RECIPIENTS'),
                subject='New Xbox Games!',
                message='\n'.join(self.new_titles),
                login=self.settings['MAIL_USER'],
                password=self.settings['MAIL_PASS'])

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings)
