"""Module for web scraping Porsche's website and connecting to the MongoDB
database to store scraped data.

Authors: Lucas SALI--ORLIANGE
Date: January 2024
"""
import scrapy
import re

from ..items import PorscheScraperItem


class PorscheFranceSpider(scrapy.Spider):
    """
    Class Docstring: Spider for web scraping Porsche's website to retrieve
    various information about available Porsche models.

    Attributes:
        name (str): Name of the spider.
        allowed_domains (list): List of allowed domains to crawl.
        start_urls (list): List of starting URLs for the spider.
    """
    name = 'porsche_france'
    allowed_domains = ['www.porsche.com']
    start_urls = ['https://www.porsche.com/france/models/']

    def parse(self, response) -> None:
        """
        Parses the first web page to retrieve different types of Porsche models.
        :param response: Link to the site containing Porsche models.
        """
        # Retrieve different types of possible models
        models_dividers = response.css('.m-14-model-series-divider')

        # For each type (Models 718, 718 Cayman GT4 RS, etc.)
        for divider in models_dividers:
            model_type_url = divider.css('a::attr(href)').get()

            # If the link exists, access the page containing related models
            if model_type_url:
                # Open the mentioned page
                yield response.follow(
                    model_type_url,
                    callback=self.parse_informations
                )

    def parse_informations(self, models_response) -> None:
        """
        Accesses various information and stores it in the database.
        :param models_response: Link leading to a Porsche category.
        """
        # Retrieve all containers for each model of that type
        models = models_response.css('.m-364-module-specs-content')

        # For each available model
        for model in models:
            # Retrieve all desired information
            dict_details = self.parse_details(model)

            yield PorscheScraperItem(
                acceleration=dict_details['acceleration'],
                top_speed=dict_details['top_speed'],
                image_url=self.parse_url_image(model),
                porsche_price=self.parse_price(model),
                porsche_name=self.parse_name(model),
                l_100_min=self.parse_l100(model),
                power_ch=dict_details['power'],
            )

    @staticmethod
    def parse_name(model_response) -> str:
        """
        Retrieves the model name from a name with multiple elements.
        :param model_response: Contains the response containing the name.
        :return: Model's name as a string.
        """
        # Retrieve the model's name
        model_name_parts = model_response.css(
            '.m-364-module-headline--title *::text').getall()

        # Clean and retrieve the complete name
        full_model_name = ' '.join(
            part.strip() for part in model_name_parts if
            part.strip())

        return full_model_name

    @staticmethod
    def parse_price(model_response) -> str:
        """
        Retrieves the model's price from a price with multiple elements.
        :param model_response: Contains the response containing the price.
        :return: Model's price.
        """
        price = ''.join(re.findall(r'\d+', (model_response.css(
            '.m-364-module-headline--copy::text').get())))[:-2]

        return price

    @staticmethod
    def parse_l100(model_response) -> str:
        """
        Retrieves the value of liters per 100 km.
        :param model_response: Contains the response containing l/100.
        :return: L/100 as a string.
        """
        return model_response.css('span.b-eco__value::text').get()

    @staticmethod
    def parse_url_image(model_response) -> str:
        """
        Retrieves the Porsche image.
        :param model_response: Contains the response containing the image URL.
        :return: Image URL as a string.
        """
        return model_response.css(
            'img.m-364-module-image::attr(data-image-src)').get()

    @staticmethod
    def parse_details(model_response):
        """
        Retrieves power, acceleration, and maximum speed.
        :param model_response: Contains all three pieces of information.
        :return: A dictionary with three values.
        """
        # Retrieve all information
        infos = model_response.css(
            '.m-364-techspecs-center .m-364-module-specs')

        return {
            # Retrieve power
            'power': infos.css('.m-364-module-specs-data--title::text').get(),
            # Retrieve acceleration
            'acceleration': infos.css(
                '.m-364-module-specs-data:nth-child(2) '
                '.m-364-module-specs-data--title::text').get(),
            # Retrieve maximum speed
            'top_speed': infos.css(
                '.m-364-module-specs-data:nth-child(3) '
                '.m-364-module-specs-data--title::text').get()
        }