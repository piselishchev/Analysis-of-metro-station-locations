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

def create_grid(city, grid_size=1000):
    data = json_helper.get_data(city)
    if data is None:
        print(f"Failed to create grid: could not load {city}.json.")
        return

    city_fullname = data["city"]

    Cell._size = grid_size

    print("Loading city boundaries...")
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

    n_cols = len(x_coords)
    n_rows = len(y_coords)

    transformer = Transformer.from_crs(utm_crs, original_crs, always_xy=True)

    print("Loading graph...")
    G = osmnx_helper.load_graph(city)
    graph = ox.truncate.largest_component(G, strongly=True)
    print("Done!")

    index = 0
    # Создаём пустую матрицу
    grid_matrix = [[None for _ in range(n_cols)] for _ in range(n_rows)]

    Cell.load_json(data)

    for j, x in enumerate(x_coords):
        for i, y in enumerate(y_coords):
            cell_polygon = box(x, y, x + grid_size, y - grid_size)
            if not cell_polygon.intersects(city_boundary):
                continue

            print("Creating object...")
            cell = Cell(index)
            index += 1

            # Можно сохранить координаты в атрибуты ячейки (опционально)
            cell.row = i
            cell.col = j

            cx = x + grid_size / 2
            cy = y - grid_size / 2
            lon, lat = transformer.transform(cx, cy)
            cell.middle = [round(lat, 6), round(lon, 6)]

            print("1")
            cell.estimate_population()
            print("2")
            cell.find_center_distance(graph)
            print("3")
            cell.find_airport_distance(graph)
            print("4")
            cell.find_metro_station_distances(graph)
            print("5")
            cell.find_train_station_distances(graph)
            print("Done")

            grid_matrix[i][j] = cell

    return grid_matrix

'''grid = create_grid(CITIES.N_NOVGOROD)
print("СЕТКА СОЗДАНА!!")
sum = 0
for cell in grid:
    print(f"Cell ID: {cell.ID}.   Airport dist: {int(cell.airport_distance)}.   Center dist: {int(cell.center_distance)}.   Population: {int(cell.population)}.")
    print(f"                                                                             Metro dist: {int(cell.metro_distance)}.   Train dist: {int(cell.train_distance)}.")
    sum += 1
print("TOTAL: ", sum)
'''