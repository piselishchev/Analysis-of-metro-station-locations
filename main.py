from app import create_app
from app.config import Config
import osmnx as ox

cache_dir = Config.DATA_DIR / "osmnx_cache"
ox.settings.use_cache = True
ox.settings.cache_folder = str(cache_dir)
    
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

