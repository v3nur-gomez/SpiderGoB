import scrapy
from scrapy.exceptions import CloseSpider


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
    
    def __init__(self, stop_at_url=None, max_pages=None, *args, **kwargs):
        """
        Inicializa el spider con opciones para modo incremental
        
        Args:
            stop_at_url: URL de la última noticia conocida (detiene al encontrarla)
            max_pages: Número máximo de páginas a procesar
        """
        super(NoticiasGobSpider, self).__init__(*args, **kwargs)
        self.stop_at_url = stop_at_url
        self.max_pages = int(max_pages) if max_pages else None
        self.pages_processed = 0
        self.items_scraped = 0
        self.found_last_news = False

    def parse(self, response):
        """Parse the main page and extract news from articles."""
        self.pages_processed += 1
        
        # Verificar límite de páginas
        if self.max_pages and self.pages_processed > self.max_pages:
            self.logger.info(f"⚠️  Límite de páginas alcanzado: {self.max_pages}")
            raise CloseSpider(f'Límite de {self.max_pages} páginas alcanzado')
        
        self.logger.info(f"📄 Procesando página {self.pages_processed}...")
        
        # Extraer información directamente de los artículos en la página de archivo
        articles = response.css('article')
        
        for article in articles:
            # Verificar si ya encontramos la última noticia conocida
            if self.found_last_news:
                self.logger.info("🛑 Ya se encontró la última noticia conocida. Deteniendo...")
                raise CloseSpider('Última noticia conocida encontrada')
            
            # Extraer datos del listado
            title = article.css('h2::text').get()
            link = article.css('a.small-link::attr(href)').get()
            date = article.css('time::attr(datetime)').get()
            category = article.css('.tag-presses::text').get()
            image = article.css('img::attr(src)').get()
            
            if title and link:
                full_url = response.urljoin(link)
                
                # Verificar si esta es la última noticia conocida ANTES de procesarla
                if self.stop_at_url and full_url == self.stop_at_url:
                    self.logger.info(f"✅ Encontrada última noticia conocida: {title.strip()[:50]}...")
                    self.logger.info(f"🛑 Deteniendo búsqueda. Se procesaron {self.items_scraped} noticias nuevas")
                    self.found_last_news = True
                    raise CloseSpider('Última noticia conocida encontrada')
                
                # Solo guardar si NO es la última noticia conocida
                self.items_scraped += 1
                yield {
                    'title': title.strip() if title else '',
                    'url': full_url,
                    'date': date.strip() if date else '',
                    'category': category.strip() if category else '',
                    'image': image if image else '',
                    'preview': '',  # No hay preview en el listado
                    'files': []  # Campo para compatibilidad
                }
        
        # Seguir paginación solo si no hemos encontrado la última noticia
        if not self.found_last_news:
            next_page = response.css('a[href*="page="]::attr(href)').getall()
            if next_page:
                # Tomar el último enlace que suele ser "página siguiente"
                last_page_link = next_page[-1]
                if 'page=' in last_page_link:
                    self.logger.info(f"➡️  Siguiente página...")
                    yield response.follow(last_page_link, self.parse)
            else:
                self.logger.info("✅ No hay más páginas para procesar")
    
    def closed(self, reason):
        """Se ejecuta cuando el spider termina"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"🏁 Spider cerrado. Razón: {reason}")
        self.logger.info(f"📊 Páginas procesadas: {self.pages_processed}")
        self.logger.info(f"📊 Noticias extraídas: {self.items_scraped}")
        self.logger.info(f"{'='*60}\n")
    
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
