import scrapy


class NoticiasGobSpider(scrapy.Spider):
    name = "noticias_gob"
    allowed_domains = ["gob.mx"]
    start_urls = [
        "https://www.gob.mx/sep/archivo/prensa",
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,  # Delay entre requests
        'CONCURRENT_REQUESTS': 4,  # Reducir solicitudes concurrentes
    }

    def parse(self, response):
        """Parse the main page and extract news from articles."""
        # Extraer información directamente de los artículos en la página de archivo
        articles = response.css('article')
        
        for article in articles:
            # Extraer datos del listado
            title = article.css('h2::text').get()
            link = article.css('a.small-link::attr(href)').get()
            date = article.css('time::attr(datetime)').get()
            category = article.css('.tag-presses::text').get()
            image = article.css('img::attr(src)').get()
            
            if title and link:
                # Opción 1: Guardar datos del listado
                yield {
                    'title': title.strip() if title else '',
                    'url': response.urljoin(link) if link else '',
                    'date': date.strip() if date else '',
                    'category': category.strip() if category else '',
                    'image': image if image else '',
                    'preview': '',  # No hay preview en el listado
                }
                
                # Opción 2: Si quieres el contenido completo, descomentar esto:
                # yield response.follow(link, self.parse_article, 
                #                      meta={'title': title, 'date': date, 'category': category})
        
        # Seguir paginación
        next_page = response.css('a[href*="page="]::attr(href)').getall()
        if next_page:
            # Tomar el último enlace que suele ser "página siguiente"
            last_page_link = next_page[-1]
            if 'page=' in last_page_link:
                yield response.follow(last_page_link, self.parse)
    
    def parse_article(self, response):
        """Parse individual article pages to get full content."""
        # Extraer contenido completo del artículo
        content_paragraphs = response.css('article p::text, article div p::text').getall()
        content = ' '.join([p.strip() for p in content_paragraphs if p.strip()])
        
        yield {
            'title': response.meta.get('title', response.css('h1::text').get()),
            'url': response.url,
            'date': response.meta.get('date', response.css('time::attr(datetime)').get()),
            'category': response.meta.get('category', response.css('.tag-presses::text').get()),
            'content': content,
        }
