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

searchname = 'Barack Obama'  #  the name we are looking for


class ContactItem(Item):
    name = Field()


class AlsoviewedSpider(Spider):
    name = 'alsoviewed'    
    allowed_domains = ["www.linkedin.com"]

    USER_NAME = 'Barack Obama'

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
            global searchname
            return FormRequest.from_response(
                response, formname='commonSearch', formdata={'type': 'people', 'keywords': searchname},
                callback=self.after_search
            )
    
    def after_search(self, response):
        # get users urls
        urls = response.xpath('//*[@id="voltron_srp_main-content"]/comment()').re(r'"link_nprofile_view_3":"([^"]+)')
        if not urls:
            logging.log("User not found", logging.ERROR)
        else:
            return Request(urls[0], callback=self.save_details)

    def save_details(self, response):
        for name in response.xpath('//*[@class="insights-browse-map"]//li/h4/a/text()').extract():
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
    process.crawl(AlsoviewedSpider)
    process.start()

if __name__ == "__main__":
    main(sys.argv[1:])

