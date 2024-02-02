from bs4 import BeautifulSoup as bs
import scrapy
from scrapy.http.response.text import TextResponse
# from scrapy.selector.unified import Selector


class MoviesSpider(scrapy.Spider):
    name = "movies"
    allowed_domains = ["ru.wikipedia.org"]
    start_urls = ["https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83"]
    # start_urls = ["https://ru.wikipedia.org/w/index.php?title=%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83&subcatfrom=Z&filefrom=Z&pageuntil=Z"]

    def parse(self, response: TextResponse, recurse=True):
        links = response.css("div#mw-pages div.mw-category-group ul li a ::attr(href)").getall()
        for i, movie in enumerate(links):
            # print(f"#{i} {movie}")
            yield response.follow(movie, callback=self.parse_movie)
            # if i > 20:
            #     break # debug 
        # yield response.follow()
        if recurse:
            next_page = response.css("div#mw-pages a ::attr(href)").getall()[-1]
            yield response.follow(next_page, callback=self.parse, cb_kwargs={"recurse": True})

    def parse_movie(self, response: TextResponse):
        page = bs(response.body, "lxml")
        article_name = page.select_one("h1.firstHeading").text
        infobox = page.select_one("table.infobox")
        if infobox is None:
            return {"url": response.url, "article_name": article_name}

        if name := infobox.select_one("tr th"):
            name = name.text.strip()

        infobox_dict = {}
        for row in infobox.select("tr"):
            key = row.select_one("th")
            value = row.select_one("td")
            if key and value:
                infobox_dict[key.text.lower().strip()] = value.text.strip()

        genre = infobox_dict.get("жанр") or infobox_dict.get("жанры")
        director = infobox_dict.get("режиссёр")
        country = infobox_dict.get("страна") or infobox_dict.get("страны")
        year = infobox_dict.get("год")
        return {
            "url": response.url,
            "article_name": article_name,
            "name": name,
            "genre": genre,
            "director": director,
            "country": country,
            "year": year,
        }
