import time
import numpy as np
import osmnx as ox
from pyproj import Transformer
from shapely.geometry import box
from pathlib import Path
from .cell import Cell
from app.utils import json_helper, osmnx_helper
from app.utils.cities import CITIES
from app.config import Config

def create_grid(city, grid_size = 1000):
    # REMOVE AFTER ALL TESTING!
    ######################################################
    cache_dir = Config.DATA_DIR / "osmnx_cache"
    ox.settings.use_cache = True
    ox.settings.cache_folder = str(cache_dir)
    ######################################################
    
    data = json_helper.get_data(city)
    if data == None:
        print(f"Failed to create grid: could not load {city}.json.")
        return
    
    city_fullname = data["city"]
      
    Cell.SIZE = grid_size
    
    print("Loadind city boundaries...")
    
    city_gdf = ox.geocode_to_gdf(city_fullname)
    original_crs = city_gdf.crs
    utm_crs = city_gdf.estimate_utm_crs()
    city_gdf = city_gdf.to_crs(utm_crs)
    city_boundary = city_gdf.geometry.iloc[0]
    
    print("Done!")
    
    minx, miny, maxx, maxy = city_boundary.bounds
    
    print("City CRS:", city_gdf.crs)
    print("Bounding box (minx, miny, maxx, maxy), km:", minx / 1000, miny / 1000, maxx / 1000, maxy / 1000)
    print("Width (km):", (maxx - minx) / 1000)
    print("Height (km):", (maxy - miny) / 1000)
    print("City area (km²):", city_boundary.area / 1e6)
    
    x_coords = np.arange(minx, maxx + grid_size, grid_size)
    y_coords = np.arange(maxy, miny - grid_size, -grid_size)
    
    transformer = Transformer.from_crs(
        utm_crs,
        original_crs,
        always_xy=True
    )
    
    print("Loading graph...")
    G = osmnx_helper.load_graph(city)
    print("Done!")
    
    start_time = time.perf_counter()
    print("Loading buildings...")
    buildings = ox.features_from_place(city_fullname, tags={"building": True})
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Done! Elapsed time: {elapsed_time:.6f} seconds")
    
    index = 0
    grid_cells = []
    for x in x_coords:
        for y in y_coords:
            cell_polygon = box(x, y, x + grid_size, y - grid_size)
            if not cell_polygon.intersects(city_boundary):
                continue
            cell = Cell(index)
            index += 1
            cx = x + grid_size / 2
            cy = y - grid_size / 2
            lon, lat = transformer.transform(cx, cy)
            cell.middle = [lat, lon]
            
            cell.estimate_population(buildings)
            cell.find_center_distance(data, G)
            cell.find_airport_distance(data, G)
            cell.find_metro_station_distances(data, G)
            cell.find_train_station_distances(data, G)
            
            grid_cells.append(cell)
    
    return grid_cells


grid = create_grid(CITIES.N_NOVGOROD)
sum = 0
for cell in grid:
    if (not isinstance(cell, Cell)):
        print("Error!")
    if (cell.ID % 50 == 0):
        print(cell.ID, cell.middle)
    sum += 1
print(sum)
