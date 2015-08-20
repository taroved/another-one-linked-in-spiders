import sys
import getopt
import logging
from scrapy import Spider, Item, Field
from scrapy.http import FormRequest, Request
from scrapy.crawler import CrawlerProcess
from w3lib import url

# credentials for login to linkedin site
LOGIN = '{Place For Login@Mail}'
PASSWORD = '{Place For Password}'  


class ContactItem(Item):
    name = Field()


class GetcontactsSpider(Spider):
    name = "getcontacts"
    allowed_domains = ["www.linkedin.com"]

    CONTACTS_URL = 'https://www.linkedin.com/vsearch/f?pt=people&page_num=1'
    PAGE_SIZE = 10
    MAX_PAGE_COUNT = 100

    current_page = 0
    
    start_urls = (
        'https://www.linkedin.com/uas/login',
    )

    def parse(self, response):
        global LOGIN
        global PASSWORD
        return FormRequest.from_response(
            response,
            formdata={'session_key': LOGIN,
                      'session_password': PASSWORD},
            callback=self.after_login
        )

    def after_login(self, response):
        # check login succeed before going on
        if "wrong_password" in response.body:
            logging.log("Login failed", logging.ERROR)
            return
        else:
            # get user contacts
            return Request(self.CONTACTS_URL,
                           meta={'dont_filter': True},
                           callback=self.parse_first_page
                           )

    def parse_first_page(self, response):
        total = int(response.xpath('//*[@id="voltron_srp_main-content"]/comment()').re(r'"formattedResultCount":"([\d,]+)"')[0].replace(",",""))
        page_count = total / self.PAGE_SIZE

        if page_count > self.MAX_PAGE_COUNT:
            page_count = self.MAX_PAGE_COUNT
        
        
        # parse first page
        for item in self.parse_page(response):
            yield item
        
        for i in xrange(page_count-1):
            u = url.add_or_replace_parameter(
                self.CONTACTS_URL, 'page_num', i+2)
            yield Request(u, callback=self.parse_page)

    def parse_page(self, response):
        for name in response.xpath('//*[@id="voltron_srp_main-content"]/comment()').re(r'"fmt_name":"([^"]+)"'):
            item = ContactItem()
            item['name'] = name
            yield item

        
def usage():
    print 'download.py -o <output.json>'
    
def main(argv):
    try:
        opts, args = getopt.getopt(argv,"o:",["output="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    else:
        if not opts:
            usage()
            sys.exit(2)
         
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-o", "--output"):
            outfile = arg
     
    process = CrawlerProcess({'DOWNLOAD_DELAY': 0.5, 'FEED_URI': outfile})
    process.crawl(GetcontactsSpider)
    process.start()

if __name__ == "__main__":
    main(sys.argv[1:])

