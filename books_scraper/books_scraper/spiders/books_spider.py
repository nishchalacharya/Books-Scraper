import scrapy
from datetime import date 


class BooksSpider(scrapy.Spider):
    name = "books"  # used to run spider with this name 
    allowed_domains = ["books.toscrape.com"]    
    start_urls = ["https://books.toscrape.com"]  # entry point 


    # Map word ratings to numbers
    RATING_MAP = {
        "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
    }

    def parse(self, response):
        """Parse a listing page — follow each book link, then go to next page."""
        
        # --- Visit each book detail page ---
        for book_url in response.css("article.product_pod h3 a::attr(href)").getall():
            absolute_url = response.urljoin(book_url)
            yield response.follow(absolute_url, callback=self.parse_book)

        # --- Pagination: find the "next" button ---
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        """Extract all required fields from a book detail page."""
 
        # Helper to pull a table row value by its header label
        def get_table_value(label):
            return response.xpath(
                f"//table//th[text()='{label}']/following-sibling::td/text()"
            ).get(default="").strip()
        

        # Rating: stored as a CSS class like "star-rating Three"
        rating_word = response.css("p.star-rating::attr(class)").get("")
        rating_word = rating_word.replace("star-rating", "").strip()
        rating = self.RATING_MAP.get(rating_word, 0)

        # Description: the <p> after the product description <div>
        description = response.css("article.product_page > p::text").get(default="").strip()


        # Availability: clean up whitespace
        availability = response.xpath(
            "normalize-space((//p[contains(@class,'availability')])[1])"
        ).get(default="").strip()

        yield {
                "name":response.css("h1::text").get(default="").strip(),
                "url":response.url,
                "scrape_date":date.today().isoformat(),
                "description":description,
                "price":response.css("p.price_color::text").get(default="").strip(),
                "tax":get_table_value("Tax"),
                "availability":availability,
                "upc":get_table_value("UPC"),
                "rating":rating,

            }   

 