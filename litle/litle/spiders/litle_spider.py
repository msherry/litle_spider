import csv
import re

from scrapy.http import FormRequest
from scrapy.selector import Selector
from scrapy.spider import Spider

FIELDNAMES = [u'BIN', u'Phone Number', u'Processing Bank BIN', u'Fax Number', u'Method of Payment', u'Contact Title', u'Last Updated', u'Bank Name', u'Country', u'Issuing Bank BIN', u'Contact Name', u'Card Usage', u'Issuing Bank Name', u'Address']

class LitleSpider(Spider):
    name = 'litle'
    allowed_domains = ['litle.com']
    start_urls = [
        'https://reports.litle.com/ui/reports/binlookup',
    ]

    def __init__(self, binfile=None, outfile='output.csv',
                 username=None, password=None):
        super(LitleSpider, self).__init__()
        self.bins = open(binfile)
        self.outfile = open(outfile, 'w')
        self.username = username
        self.password = password
        self.writer = csv.DictWriter(self.outfile, fieldnames=FIELDNAMES)
        self.writer.writeheader()

    def parse(self, response):
        if 'login' in response.url:
            return [FormRequest.from_response(
                response,
                formdata={'j_username': self.username,
                          'j_password': self.password},
                callback=self.after_login)]

    def after_login(self, response):
        if 'BIN Lookup' in response.body:
            for binnum in self.bins:
                binnum = binnum.strip()
                yield FormRequest.from_response(
                    response, formdata={'search': binnum},
                    callback=self.got_bin)

    def got_bin(self, response):
        sel = Selector(response)
        data = dict(
            zip(
                [re.sub(r'\n +', '',
                        x.replace('<label>', '').replace('</label>', ''))
                 for x in sel.xpath('//td/label').extract()],
                [re.sub(r'\n +', '', x.replace('<p>', '').replace('</p>', ''))
                 for x in sel.xpath('//td/p').extract()]))
        self.writer.writerow(data)
