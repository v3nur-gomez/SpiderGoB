# Scraper de Noticias - gob.mx/sep

Este proyecto es un scraper para obtener noticias del portal de la Secretaría de Educación Pública de México (gob.mx/sep).

## 🚀 Características

- ✅ **Modo Incremental**: Solo descarga noticias nuevas después de la última ejecución
- ✅ **Modo Completo**: Descarga todas las noticias disponibles
- ✅ **Ejecutable desde Python**: No requiere comandos de Scrapy
- ✅ **Tracking automático**: Guarda la última noticia procesada
- ✅ **Control de paginación**: Limita el número de páginas a procesar

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

1. **Instalar las dependencias:**
```bash
pip install -r requirements.txt
```

2. **Instalar los navegadores de Playwright:**
```bash
playwright install chromium
```

## 🎯 Uso

### Modo Incremental (Recomendado)
Ejecuta el scraper y solo descarga noticias nuevas:

```bash
python run_scraper.py
```

o explícitamente:

```bash
python run_scraper.py --mode incremental
```

### Modo Completo
Descarga todas las noticias desde el inicio:

```bash
python run_scraper.py --mode full
```

### Limitar Páginas
Procesa solo las primeras N páginas:

```bash
python run_scraper.py --max-pages 3
```

### Combinaciones
```bash
# Modo completo, solo 5 páginas
python run_scraper.py --mode full --max-pages 5

# Modo incremental, máximo 10 páginas
python run_scraper.py --max-pages 10
```

## 📁 Archivos Generados

- **`gobmx_scraper/noticias.json`**: Contiene todas las noticias descargadas
- **`gobmx_scraper/last_run.json`**: Guarda información de la última ejecución

## 📊 Estructura de Datos

Cada noticia contiene:
```json
{
  "title": "Título de la noticia",
  "url": "https://www.gob.mx/sep/prensa/...",
  "date": "2025-11-25 18:21:00",
  "category": "Comunicado",
  "image": "https://www.gob.mx/cms/uploads/...",
  "preview": "",
  "files": []
}
```

## 🔄 Flujo de Trabajo Recomendado

1. **Primera ejecución** (modo completo):
   ```bash
   python run_scraper.py --mode full
   ```

2. **Ejecuciones posteriores** (modo incremental):
   ```bash
   python run_scraper.py
   ```
   Esto solo descargará noticias nuevas, ahorrando tiempo y recursos.

3. **Revisión periódica**:
   - Ejecuta el script diariamente o según tus necesidades
   - Las noticias nuevas se agregarán automáticamente al inicio del archivo JSON

## ⚙️ Configuración Avanzada

### Modificar settings del spider

Edita `gobmx_scraper/settings.py` para cambiar:
- `DOWNLOAD_DELAY`: Tiempo entre peticiones (default: 2 segundos)
- `CONCURRENT_REQUESTS`: Peticiones simultáneas (default: 4)

### Personalizar output

```bash
python run_scraper.py --output mi_archivo.json
```

## 🐛 Solución de Problemas

### Error: Playwright no instalado
```bash
playwright install chromium
```

### Error: Módulo no encontrado
```bash
pip install -r requirements.txt
```

### Las noticias se duplican
- El modo incremental previene duplicados automáticamente
- Si necesitas limpiar duplicados manualmente, ejecuta:
  ```bash
  python run_scraper.py --mode full
  ```

## 📝 Notas

- El scraper respeta un delay de 2 segundos entre peticiones para no sobrecargar el servidor
- Las noticias se ordenan de más reciente a más antigua
- El modo incremental se detiene al encontrar la última noticia conocida

## 🤝 Contribuciones

Este proyecto fue desarrollado para el HackaNACIONAL.

## 📄 Licencia

Este proyecto es de código abierto para fines educativos.
