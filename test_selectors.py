import scrapy
from scrapy.crawler import CrawlerProcess

class TestSpider(scrapy.Spider):
    name = "test"
    start_urls = ["https://www.gob.mx/sep/archivo/prensa"]
    
    custom_settings = {
        'LOG_LEVEL': 'INFO',
    }
    
    def parse(self, response):
        # Guardar el HTML para inspección
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("\n=== INSPECCIONANDO ESTRUCTURA ===")
        
        # Buscar todos los enlaces
        all_links = response.css('a::attr(href)').getall()
        article_links = [link for link in all_links if 'articulo' in link or 'prensa' in link]
        
        print(f"\nTotal enlaces encontrados: {len(all_links)}")
        print(f"Enlaces con 'articulo' o 'prensa': {len(article_links)}")
        print(f"\nPrimeros 10 enlaces de artículos:")
        for link in article_links[:10]:
            print(f"  - {link}")
        
        # Buscar elementos de noticias
        print("\n=== BUSCANDO ESTRUCTURA DE NOTICIAS ===")
        
        # Intentar varios selectores comunes
        selectors = [
            ('article', response.css('article')),
            ('.noticia', response.css('.noticia')),
            ('.article', response.css('.article')),
            ('.card', response.css('.card')),
            ('.item', response.css('.item')),
            ('h2 a', response.css('h2 a')),
            ('h3 a', response.css('h3 a')),
        ]
        
        for name, elements in selectors:
            if elements:
                print(f"\n'{name}' encontrados: {len(elements)}")
                if elements:
                    first = elements[0]
                    print(f"  Primer elemento HTML (primeros 200 chars):")
                    print(f"  {first.get()[:200]}")

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(TestSpider)
    process.start()
