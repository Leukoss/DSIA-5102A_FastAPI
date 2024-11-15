"""Module for web scraping Porsche's website

Authors: Lucas SALI--ORLIANGE, Apollinaire TEXIER
Date: November 2024
"""
import scrapy
import re

from ..items import PorscheScraperItem


class PorscheSpider(scrapy.Spider):
    """
    Class Docstring: Spider for web scraping Porsche's website

    Attributes:
        name (str): Name of the spider.
        allowed_domains (list): List of allowed domains to crawl.
        start_urls (list): List of starting URLs for the spider.
    """
    name = 'porsche_spider'
    allowed_domains = ['www.porsche.com']
    start_urls = ['https://www.porsche.com/france/models/']
    list_id_model_classic = [
        's718-models', 's718-cayman-gt4-rs', 's718-spyder-rs', 's911-turbo-50',
        's911-turbo-models', 's911-gt3-rs', 's911-dakar', 's911-st'
    ]

    def parse(self, response) -> None:
        """
        Parses the first web page to retrieve different types of Porsche models.
        :param response: Link to the site containing Porsche models.

        Retrieve the dividers related to the different types of Porsche models
        "Modèles 718", "718 Cayman GT4 RS", ..., "Modèles Cayenne Coupé"
        """
        # Retrieve all the possible dividers that contain one or more model
        models_dividers = response.css('.m-14-model-series-divider visible')

        # For loop checking each possible category
        for divider in models_dividers:
            # Retrieve the url of each model category
            model_type_url = divider.css('a::attr(href)').get()

            # Retrieve the id of the model category
            model_id = divider.css('a::attr(id)').get()

            # If the url can be retrieved, we dive into the url
            if model_type_url:
                # According to the model category, apply a different scraping
                if model_id in self.list_id_model_classic:
                    yield response.follow(
                        model_type_url, callback=self.parse_classic_model
                    )
                # When the model is not classic, another set of links is needed
                else:
                    continue

    def parse_classic_model(self, model_response) -> None:
        """
        Realise the classic parsing to add in the pipeline values for the
        Porsche items
        :param model_response: response that contains several vehicles
        """
        # Retrieve all containers for the specific model (contains vehicles)
        vehicles = model_response.css('.m-364-module-specs-content')

        # Look all vehicles
        for vehicle in vehicles:
            # Retrieve 'power', 'acceleration', 'max_speed'
            dict_details = self.parse_classic_details(vehicle)

            # Retrieve picture url
            img_url = self.parse_classic_url_image(vehicle)

            # Retrieve the name of the vehicle
            vehicle_name = self.parse_classic_name(vehicle)

            # Retrieve the price of the vehicle
            vehicle_price = self.parse_classic_price(vehicle)

            # Retrieve l/100
            vehicle_l100 = self.parse_classic_l100(vehicle)

            yield PorscheScraperItem(
                acceleration    = dict_details['acceleration'],
                top_speed       = dict_details['top_speed'],
                power_ch        = dict_details['power'],
                porsche_price   = vehicle_price,
                porsche_name    = vehicle_name,
                l_100_min       = vehicle_l100,
                image_url       = img_url,
            )

    @staticmethod
    def parse_classic_details(vehicle) -> dict:
        """
        Retrieve the 'power', 'acceleration' (from 0 to 100 km/h), and 'maximum
        speed' (on track)
        :param vehicle: container for a vehicle
        :return: dictionary{'power':...,'acceleration':...,'max_speed':...}
        """
        # Contains the 'power', 'acceleration', and 'maximum speed'
        infos = vehicle.css('.m-364-module-specs')

        return {
            # Each node contains different information

            # Retrieve both power ch/kw processed in the pipelines
            'power':
                infos.css(
                    '.m-364-module-specs-data:nth-child(1) '
                    '.m-364-module-specs-data--title::text').get(),
            # Retrieve 'X.XX s' processed in the pipelines for 'X.XX'
            'acceleration':
                infos.css(
                    '.m-364-module-specs-data:nth-child(2) '
                    '.m-364-module-specs-data--title::text').get(),
            # Retrieve 'XXX km/h' processed in the pipelines for 'XXX'
            'max_speed':
                infos.css(
                    '.m-364-module-specs-data:nth-child(3) '
                    '.m-364-module-specs-data--title::text').get()
        }

    @staticmethod
    def parse_classic_url_image(vehicle) -> str:
        """
        Retrieve the Porsche image
        :param vehicle: contains the response's image URL
        :return: image URL as a string
        """
        return vehicle.css(
            'img.m-364-module-image::attr(data-image-src)').get()

    @staticmethod
    def parse_classic_name(vehicle) -> str:
        """
        Retrieve the model name
        :param vehicle: contains the response's vehicle name
        :return: model's name as a string.
        """
        # Retrieve all the elements in the vehicle name tag
        model_name_parts = vehicle.css('.m-364-module-headline--title '
                                       '*::text').getall()

        # Clean and retrieve the complete name
        full_model_name = ' '.join(
            part.strip() for part in model_name_parts if part.strip()
        )

        return full_model_name

    @staticmethod
    def parse_classic_price(vehicle) -> str:
        """
        Retrieve the price of the vehicle
        :param vehicle: contains the response containing the price
        :return: vehicle price
        """
        # Extract the price text and extract the numerical part
        price_text = vehicle.css('.m-364-module-headline--copy::text').get()

        return price_text

    @staticmethod
    def parse_classic_l100(vehicle) -> dict:
        """
        Retrieve liters per 100 km
        :param vehicle: contain the response containing l/100 of the vehicle
        :return: dictionary with the minimum and maximum range l/100
        """
        # Retrieve the minimum and maximum consumption range
        l100_str = vehicle.css('span.b-eco__value::text').get()

        return l100_str