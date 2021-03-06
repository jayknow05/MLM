# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class PlayerItem(Item):
    name = Field()
    position = Field()
    salary = Field(default=99999)
    projection = Field()
    gradient = Field()
    pass