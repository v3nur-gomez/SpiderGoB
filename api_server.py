from flask import Flask, jsonify, request
import json
import os
import threading
from run_scraper import IncrementalScraperRunner

app = Flask(__name__)

scraper_status = {'running': False, 'last_error': None}

def run_scraper_bg(mode='incremental', max_pages=None):
    global scraper_status
    scraper_status['running'] = True
    scraper_status['last_error'] = None
    try:
        runner = IncrementalScraperRunner()
        runner.run(mode=mode, max_pages=max_pages)
    except Exception as e:
        scraper_status['last_error'] = str(e)
    finally:
        scraper_status['running'] = False

@app.route('/')
def home():
    return jsonify({
        'service': 'GOB.MX Scraper API',
        'version': '1.0',
        'endpoints': {
            'GET /health': 'Health check',
            'POST /scraper/run': 'Execute scraper',
            'GET /scraper/status': 'Get scraper status',
            'GET /news': 'Get all news',
            'GET /news/new': 'Get only new news',
            'GET /news/latest': 'Get latest news info'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'gobmx-scraper'})

@app.route('/scraper/run', methods=['POST'])
def run_scraper():
    if scraper_status['running']:
        return jsonify({'error': 'Scraper already running'}), 409
    
    data = request.json or {}
    mode = data.get('mode', 'incremental')
    max_pages = data.get('max_pages', None)
    
    thread = threading.Thread(target=run_scraper_bg, args=(mode, max_pages))
    thread.start()
    
    return jsonify({
        'status': 'started',
        'mode': mode,
        'max_pages': max_pages
    }), 202

@app.route('/scraper/status')
def get_status():
    return jsonify(scraper_status)

@app.route('/news')
def get_news():
    try:
        runner = IncrementalScraperRunner()
        news = runner.load_existing_news()
        
        limit = request.args.get('limit', type=int)
        date_from = request.args.get('date_from')
        
        if date_from:
            news = [n for n in news if n.get('date', '') >= date_from]
        
        if limit:
            news = news[:limit]
        
        return jsonify({
            'total': len(news),
            'data': news
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/news/new')
def get_new():
    try:
        runner = IncrementalScraperRunner()
        
        if os.path.exists(runner.last_run_file):
            with open(runner.last_run_file, 'r', encoding='utf-8') as f:
                last_run = json.load(f)
            
            new_count = last_run.get('new_items', 0)
            news = runner.load_existing_news()
            
            return jsonify({
                'total': len(news),
                'new_items': new_count,
                'last_run': last_run,
                'data': news[:new_count] if new_count > 0 else []
            })
        
        return jsonify({
            'new_items': 0,
            'data': [],
            'message': 'No previous run found'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/news/latest')
def get_latest():
    try:
        runner = IncrementalScraperRunner()
        last_news = runner.get_last_news_info()
        
        if last_news:
            return jsonify(last_news)
        else:
            return jsonify({'message': 'No news found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f' API del Scraper iniciada en puerto {port}')
    print('\nEndpoints disponibles:')
    print('  GET  /              - Info de la API')
    print('  GET  /health        - Health check')
    print('  POST /scraper/run   - Ejecutar scraper')
    print('  GET  /scraper/status - Ver estado')
    print('  GET  /news          - Todas las noticias')
    print('  GET  /news/new      - Solo noticias nuevas')
    print('  GET  /news/latest   - Última noticia\n')
    
    app.run(host='0.0.0.0', port=port, debug=False)
