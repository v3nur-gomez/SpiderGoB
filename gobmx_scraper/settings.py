BOT_NAME = "gobmx_scraper"

SPIDER_MODULES = ["gobmx_scraper.spiders"]
NEWSPIDER_MODULE = "gobmx_scraper.spiders"

ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 4

DOWNLOAD_HANDLERS = {
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_BROWSER_TYPE = "chromium"

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000

# ITEM_PIPELINES desactivado - no se descargan archivos
# ITEM_PIPELINES = {
#     "scrapy.pipelines.files.FilesPipeline": 1,
# }

LOG_LEVEL = "INFO"
