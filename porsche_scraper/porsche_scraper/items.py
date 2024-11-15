"""
Module to define scraping items in the Porsche Project

Authors: Lucas SALI--ORLIANGE, Apollinaire TEXIER
Date: November 2024
"""

import scrapy


class PorscheScraperItem(scrapy.Item):
    porsche_price   = scrapy.Field()
    porsche_name    = scrapy.Field()
    acceleration    = scrapy.Field()
    top_speed       = scrapy.Field()
    image_url       = scrapy.Field()
    l_100_min       = scrapy.Field()
    l_100_max       = scrapy.Field()
    power_ch        = scrapy.Field()
    power_kw        = scrapy.Field()