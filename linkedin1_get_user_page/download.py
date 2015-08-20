import sys
import getopt
import logging
from scrapy import Spider
from scrapy.http import FormRequest, Request
from scrapy.crawler import CrawlerProcess

# credentials for login to linkedin site
LOGIN = '{Linkedin user email}'
PASSWORD = '{Linkedin user password}'  

searchname = 'Barack Obama'  #  the name we are looking for

# script arguments:
outfile = None  # output HTML file

class GetuserSpider(Spider):
    name = "getuser"
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
        # save html
        global outfile
        with open(outfile, 'w+') as f:
            f.write(response.body)
        
def usage():
    print 'download.py -p <output.html>'
    
def main(argv):
    try:
        opts, args = getopt.getopt(argv,"p:",["page="])
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
        elif opt in ("-p", "--page"):
            global outfile
            outfile = arg
     
    process = CrawlerProcess({'DOWNLOAD_DELAY': 0.5})
    process.crawl(GetuserSpider)
    process.start()

if __name__ == "__main__":
    main(sys.argv[1:])

