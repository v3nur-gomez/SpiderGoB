#!/usr/bin/env python
"""
Script principal para ejecutar el scraper de noticias de gob.mx
Permite ejecutar en modo completo o incremental (solo noticias nuevas)
"""
import json
import os
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from gobmx_scraper.spiders.noticias import NoticiasGobSpider


class IncrementalScraperRunner:
    """Ejecuta el scraper en modo incremental o completo"""
    
    def __init__(self, output_file='gobmx_scraper/noticias.json', 
                 last_run_file='gobmx_scraper/last_run.json'):
        self.output_file = output_file
        self.last_run_file = last_run_file
        
    def get_last_news_info(self):
        """Obtiene información de la última noticia procesada"""
        if not os.path.exists(self.output_file):
            return None
            
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data and len(data) > 0:
                    # La primera noticia es la más reciente
                    return {
                        'title': data[0].get('title', ''),
                        'url': data[0].get('url', ''),
                        'date': data[0].get('date', ''),
                        'timestamp': datetime.now().isoformat()
                    }
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        
        return None
    
    def save_last_run_info(self, last_news_info):
        """Guarda información de la última ejecución"""
        if last_news_info:
            with open(self.last_run_file, 'w', encoding='utf-8') as f:
                json.dump(last_news_info, f, ensure_ascii=False, indent=2)
    
    def load_existing_news(self):
        """Carga las noticias existentes"""
        if not os.path.exists(self.output_file):
            return []
            
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def merge_news(self, new_news, existing_news):
        """Combina noticias nuevas con existentes, evitando duplicados"""
        # Crear un set de URLs existentes para búsqueda rápida
        existing_urls = {item['url'] for item in existing_news if 'url' in item}
        
        # Filtrar noticias nuevas que no existen
        unique_new_news = [item for item in new_news if item.get('url') not in existing_urls]
        
        # Combinar: nuevas primero, luego existentes
        merged = unique_new_news + existing_news
        
        return merged, len(unique_new_news)
    
    def run(self, mode='incremental', max_pages=None):
        """
        Ejecuta el scraper
        
        Args:
            mode: 'incremental' para solo nuevas noticias, 'full' para todas
            max_pages: Número máximo de páginas a procesar (None = todas)
        """
        print(f"\n🚀 Iniciando scraper en modo: {mode.upper()}")
        print("=" * 60)
        
        # Obtener información de la última noticia
        last_news = self.get_last_news_info()
        
        if mode == 'incremental' and last_news:
            print(f"📰 Última noticia conocida:")
            print(f"   Título: {last_news['title'][:70]}...")
            print(f"   Fecha: {last_news['date']}")
            print(f"   URL: {last_news['url']}")
            print(f"\n🔍 Buscando solo noticias más recientes...\n")
        else:
            print(f"🔍 Ejecutando scraping completo...\n")
            last_news = None
        
        # Configurar settings
        settings = get_project_settings()
        settings.set('FEEDS', {
            self.output_file: {
                'format': 'json',
                'encoding': 'utf-8',
                'overwrite': False,
                'indent': 2,
            }
        })
        
        # Cargar noticias existentes antes del scraping
        existing_news = self.load_existing_news()
        print(f"📊 Noticias existentes: {len(existing_news)}")
        
        # Crear proceso de scraping
        process = CrawlerProcess(settings)
        
        # Configurar el spider con parámetros
        spider_kwargs = {
            'stop_at_url': last_news['url'] if last_news else None,
            'max_pages': max_pages
        }
        
        # Ejecutar spider
        process.crawl(NoticiasGobSpider, **spider_kwargs)
        process.start()
        
        # Cargar las noticias después del scraping
        all_news = self.load_existing_news()
        
        # Calcular noticias nuevas
        new_count = len(all_news) - len(existing_news)
        
        print(f"\n" + "=" * 60)
        print(f"✅ Scraping completado!")
        print(f"📊 Noticias nuevas encontradas: {new_count}")
        print(f"📊 Total de noticias: {len(all_news)}")
        
        # Guardar información de la última ejecución
        if all_news:
            last_info = {
                'title': all_news[0].get('title', ''),
                'url': all_news[0].get('url', ''),
                'date': all_news[0].get('date', ''),
                'timestamp': datetime.now().isoformat(),
                'mode': mode,
                'new_items': new_count
            }
            self.save_last_run_info(last_info)
            print(f"💾 Información guardada en: {self.last_run_file}")
        
        print(f"📁 Resultados guardados en: {self.output_file}")
        print("=" * 60 + "\n")
        
        return all_news


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scraper de noticias de gob.mx/sep',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_scraper.py                    # Modo incremental (por defecto)
  python run_scraper.py --mode full       # Scraping completo
  python run_scraper.py --max-pages 3     # Solo primeras 3 páginas
  python run_scraper.py --mode full --max-pages 5
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['incremental', 'full'],
        default='incremental',
        help='Modo de ejecución: incremental (solo nuevas) o full (todas)'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=None,
        help='Número máximo de páginas a procesar'
    )
    
    parser.add_argument(
        '--output',
        default='gobmx_scraper/noticias.json',
        help='Archivo de salida para las noticias'
    )
    
    args = parser.parse_args()
    
    # Crear y ejecutar el runner
    runner = IncrementalScraperRunner(output_file=args.output)
    runner.run(mode=args.mode, max_pages=args.max_pages)


if __name__ == '__main__':
    main()
