"""
Module to define the Settings of the Scraping in a Porsche project

Authors: Lucas SALI--ORLIANGE, Apollinaire TEXIER
Date: November 2024
"""
import os

BOT_NAME = "porsche_scraper"

SPIDER_MODULES = ["porsche_scraper.spiders"]
NEWSPIDER_MODULE = "porsche_scraper.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure item pipelines
ITEM_PIPELINES = {
    # Add pipelines processing for items
    "porsche_scraper.pipelines.TextPipeline": 100,
    # Add pipeline processing for PostgresSQL
   "porsche_scraper.pipelines.PostgresPipeline": 1,
}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Handle Timeouts
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

# Define a logging level to retrieve warnings and errors
LOG_LEVEL = "INFO"