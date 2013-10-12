# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import log
import os
import sqlite3


class SitewatcherPipeline(object):
    def __init__(self, root_dir):
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
            with self.conn:
                self.conn.execute('INSERT INTO games VALUES(?)', (title,))
        else:
            log.msg('%s was previously seen.' % title)

        return item

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        root_dir = settings['ROOT_DIR']
        return cls(root_dir)
