"""
Module to define the pipelines within the Porsche Project

Authors: Lucas SALI--ORLIANGE, Apollinaire TEXIER
Date: November 2024
"""

from dotenv             import load_dotenv
from typing             import Tuple, Any
from scrapy.exceptions  import DropItem
from scrapy             import Item
from psycopg2           import sql

import psycopg2
import os
import re

# Retrieve the environment variables
DOTENV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../fastapi_app/.env')
)

load_dotenv(DOTENV_PATH)

# Access the PostgresSQL URI from the .env file
POSTGRES_URI = os.getenv("POSTGRES_URI")

def get_power(power_string) -> tuple[int, int]:
    """
    Retrieve both kW and ch power
    :param power_string: '200 kW/300 ch'
    :return: (200, 300)
    """
    list_power = power_string.split(sep='/')
    list_to_return = []

    for power in list_power:
        power_value = re.findall(r'\d+', power)
        list_to_return.extend(int(number) for number in power_value)

    if len(list_to_return) != 2:
        raise ValueError(f"Invalid power string: {power_string}")

    return list_to_return[0], list_to_return[1]

def get_l100(l100_string) -> tuple[float, float]:
    """
    Retrieve both minimum and maximum l/100 consumption value
    :param l100_string: '8.5 - 9.3'
    :return: (8.5, 9.3)
    """
    if '-' in l100_string:
        min_value, max_value = l100_string.split('-')
        min_value = float(min_value.replace(',', '.').strip())
        max_value = float(max_value.replace(',', '.').strip())
        return min_value, max_value
    else:
        list_l_100 = re.findall(r'\d+,\d+', l100_string)
        if not list_l_100:
            raise DropItem(f"Invalid l/100 value: {l100_string}")

        list_to_return = [float(value.replace(',', '.')) for value in
                          list_l_100]
        return list_to_return[0], list_to_return[0]

def get_top_speed(top_speed_string) -> int:
    """
    Retrieve the maximum speed on track without 'km/h'
    :param top_speed_string: '275 km/h'
    :return: 275
    """
    return int(re.findall(r'\d+', top_speed_string)[0])

def get_acceleration(acceleration_string) -> float:
    """
    Retrieve the time required to go from 0 to 100 km/h
    :param acceleration_string: '5,1 s'
    :return: 5,1
    """
    return float(re.findall(
        r'\d+,\d+', acceleration_string)[0].replace(',', '.'))

class TextPipeline(object):
    """
    Edit some items in the scraping process
    """
    def process_item(self, item) -> Item:
        if item.get('power_ch'):
            item['power_kw'], item['power_ch'] = (
                get_power(item.get('power_ch')))
        else:
            raise DropItem({item})

        if item.get('l_100_min'):
            item['l_100_min'], item['l_100_max'] = (
                get_l100(item.get('l_100_min')))
        else:
            raise DropItem({item})

        if item.get('porsche_price'):
            item['porsche_price'] = int(item.get('porsche_price'))
        else:
            raise DropItem({item})

        if item.get('top_speed'):
            item['top_speed'] = get_top_speed(item.get('top_speed'))
        else:
            raise DropItem({item})

        if item.get('acceleration'):
            item['acceleration'] = get_acceleration(item.get('acceleration'))
        else:
            raise DropItem({item})
        return item

class PostgresPipeline:
    def __init__(self):
        self.cursor = None
        self.connection = None

    def open_spider(self, spider) -> None:
        """
        Open a connection with the Postgres database when the Spider starts
        :param spider: spider for the Porsche project
        """
        self.connection = psycopg2.connect(POSTGRES_URI)
        self.cursor     = self.connection.cursor()
        self.create_table()

    def close_spider(self, spider) -> None:
        """
        Close the connection to the Postgres database when the Spider finishes
        :param spider: spider for the Porsche project
        """
        self.cursor.close()
        self.connection.close()

    def create_table(self):
        """
        Create the table in PostgreSQL if it doesn't already exist.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS porsche_data (
                id SERIAL PRIMARY KEY,
                porsche_price INT,
                porsche_name TEXT,
                acceleration FLOAT,
                top_speed INT,
                image_url TEXT,
                l_100_min FLOAT,
                l_100_max FLOAT,
                power_ch INT,
                power_kw INT
            );
        """)
        self.connection.commit()

    def process_item(self, item, spider):
        """
        Process and insert scraped items into the database.
        """
        try:
            self.cursor.execute(
                sql.SQL("""
                    INSERT INTO porsche_data (porsche_price, porsche_name, 
                    acceleration, top_speed, image_url, l_100_min, l_100_max, 
                    power_ch, power_kw)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """),
                (
                    item.get("porsche_price"),
                    item.get("porsche_name"),
                    item.get("acceleration"),
                    item.get("top_speed"),
                    item.get("image_url"),
                    item.get("l_100_min"),
                    item.get("l_100_max"),
                    item.get("power_ch"),
                    item.get("power_kw")
                )
            )
            self.connection.commit()
        except psycopg2.IntegrityError as e:
            spider.logger.error(
                f"Integrity error while inserting into database: {e}")
            raise DropItem(f"Integrity error: {e}")
        except psycopg2.Error as e:
            spider.logger.error(f"Database error: {e}")
            raise DropItem(f"Database insert error: {e}")
        return item