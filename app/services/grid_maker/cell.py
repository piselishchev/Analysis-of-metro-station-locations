from app.utils import osmnx_helper
import osmnx as ox
import geopandas as gpd
import pyproj
import pandas as pd
import numpy as np
from shapely.geometry import Point, box
from shapely.ops import transform
from geopy.distance import geodesic
from app.config import Config
import os
import json

class Cell:
    """Одна ячейка сетки 1×1 км. Хранит данные о зданиях и умеет считать население и расстояния."""
    _size = 1000  # сторона квадрата в метрах
    _data = None
    _buildings = None          # геометрии зданий и их этажность
    _project_to_utm = None     # функция перевода координат из градусов в метры
    _people_per_sqm = 0.02     # сколько человек живёт на 1 м² жилья
    _cache_loaded = False      # флаг, что данные уже загружены

    _center_distance_map = None
    _airport_distance_map = None
    _metro_distance_map = {}
    _train_distance_map = {}
    
    def __init__(self, ID):
        self.ID = ID
        self.middle = None              # [lat, lon] центр ячейки
        self.population = None      
        self.center_distance = None
        self.airport_distance = None
        self.metro_distance = None
        self.train_distance = None

    @classmethod
    def load_json(cls, data):
        if data == None:
            print(f"Failed to get json file.")
            return
        cls._data = data
    
    @classmethod
    def load_buildings(cls, cache_file="buildings_cache.json"):
        """Загружает здания (из кэша или OSM) и готовит их для быстрых расчётов."""
        
        print("Loading buildings...")
        if cls._cache_loaded:
            return

        if cls._data == None:
            print(f"Failed to read json file.")
            return
        city_name = cls._data["city"]
        utm_crs = cls._data["utm"]
        
        cache_dir = Config.DATA_DIR / "osmnx_cache" / cache_file
        
        if cache_dir.exists():
            print("!!!")
            cls._buildings = gpd.read_file(cache_dir)
            print("!!!")
            if cls._buildings.crs is None:
                cls._buildings = cls._buildings.set_crs(utm_crs)
        else:
            print("!!!!!")
            # Качаем все здания из OSM
            buildings_raw = ox.features_from_place(city_name, {"building": True})
            buildings_raw = buildings_raw.to_crs(utm_crs)

            # Оставляем только геометрию и этажность
            cols = ['geometry']
            if 'building:levels' in buildings_raw.columns:
                cols.append('building:levels')
            cls._buildings = buildings_raw[cols].copy()

            # Превращаем этажность в числа (берём первое число, если нет — 3)
            if 'building:levels' in cls._buildings.columns:
                cls._buildings['building:levels'] = (
                    cls._buildings['building:levels']
                    .fillna(3)
                    .astype(str)
                    .str.extract(r'(\d+)')[0]
                    .fillna(3)
                    .astype(float)
                )
            else:
                cls._buildings['building:levels'] = 3.0

            # Упрощаем геометрию для скорости (точность 1 метр — глазом не видно)
            cls._buildings['geometry'] = cls._buildings['geometry'].simplify(1.0)

            # Сохраняем на диск, чтобы в следующий раз не качать
            cls._buildings.to_file(cache_dir, driver="GeoJSON")

        # Функция перевода из градусов в метры (UTM)
        cls._project_to_utm = pyproj.Transformer.from_crs(
            "EPSG:4326", utm_crs, always_xy=True
        ).transform
        cls._cache_loaded = True
        print("Done")

    @staticmethod
    def _safe_extract_floor(val):
        """Запасной метод, сейчас не используется."""
        # оставлен на случай, если понадобится другой способ обработки этажности
        pass

    def estimate_population(self):
        """Считает население в ячейке, используя загруженные здания."""
        if self.middle is None:
            return None

        # Если данные ещё не загружены — загружаем
        if not type(self)._cache_loaded:
            type(self).load_buildings()

        # Переводим центр в метры (UTM) — меняем порядок координат для Shapely
        point_wgs = Point(self.middle[1], self.middle[0])
        point_utm = transform(type(self)._project_to_utm, point_wgs)

        # Строим квадрат вокруг центра (половина стороны = 500 м)
        half = self.SIZE / 2
        cell_poly = box(
            point_utm.x - half,
            point_utm.y - half,
            point_utm.x + half,
            point_utm.y + half
        )

        # Быстрый поиск зданий через пространственный индекс (R-tree)
        buildings = type(self)._buildings
        possible_idx = list(buildings.sindex.intersection(cell_poly.bounds))
        if not possible_idx:
            self.population = 0
            return 0

        possible = buildings.iloc[possible_idx]
        # Отсеиваем те, которые только задели границу по bounding box, но реально не пересекаются
        possible = possible[possible.intersects(cell_poly)]

        if possible.empty:
            self.population = 0
            return 0

        # Площади пересечений зданий с квадратом
        intersected = possible.geometry.intersection(cell_poly)
        areas = intersected.area

        # Этажность (уже числа)
        floors = possible['building:levels'].values

        # Эффективная жилая площадь = сумма(площадь × этажность)
        effective_area = (areas * floors).sum()
        self.population = round(effective_area * type(self)._people_per_sqm, 0)
        return self.population

    def find_center_distance(self, graph):
        """Расстояние от ячейки до центра города по дорогам."""
        if self.middle is None:
            return
        if self._data is None:
            return
        center_coords = type(self)._data["coords"]["center"]
        if type(self)._center_distance_map is None:
            type(self)._center_distance_map = osmnx_helper.build_distance_map_to_target(graph, center_coords)
            
        node = ox.distance.nearest_nodes(graph, X=self.middle[1], Y=self.middle[0])
        self.center_distance = self._center_distance_map.get(node)

    def find_airport_distance(self, graph):
        """Расстояние до аэропорта."""
        if self.middle is None:
            return
        if self._data is None:
            return
        airport_coords = type(self)._data["coords"]["airport"]
        if type(self)._airport_distance_map is None:
            type(self)._airport_distance_map = osmnx_helper.build_distance_map_to_target(graph, airport_coords)
        
        node = ox.distance.nearest_nodes(graph, X=self.middle[1], Y=self.middle[0])
        self.airport_distance = type(self)._airport_distance_map.get(node)

    def find_metro_station_distances(self, graph):
        """Расстояние до ближайшего метро."""
        if self.middle is None:
            return
        if self._data is None:
            return
        
        stations = self._data["coords"].get("metro_stations", [])
        
        if len(type(self)._metro_distance_map) == 0:
            for idx, station_coords in enumerate(stations):
                type(self)._metro_distance_map[idx] = osmnx_helper.build_distance_map_to_target(graph, station_coords)
            
        closest_station = stations[0]
        index = 0
        closest_dist = geodesic(self.middle, closest_station).meters
        
        
        for idx, station_coords in enumerate(stations):
            dist = geodesic(self.middle, station_coords).meters
            if closest_dist > dist:
                closest_dist = dist
                closest_station = station_coords
                index = idx
        
        node = ox.distance.nearest_nodes(graph, X=self.middle[1], Y=self.middle[0])
        self.metro_distance = (type(self)._metro_distance_map[index]).get(node)
        

    def find_train_station_distances(self, graph):
        """Расстояние до ближайшего ж/д станций."""
        if self.middle is None:
            return
        if self._data is None:
            return
        
        stations = self._data["coords"].get("train_stations", [])
        
        if len(type(self)._train_distance_map) == 0:
            for idx, station_coords in enumerate(stations):
                type(self)._train_distance_map[idx] = osmnx_helper.build_distance_map_to_target(graph, station_coords)
            
        closest_station = stations[0]
        index = 0
        closest_dist = geodesic(self.middle, closest_station).meters
        
        
        for idx, station_coords in enumerate(stations):
            dist = geodesic(self.middle, station_coords).meters
            if closest_dist > dist:
                closest_dist = dist
                closest_station = station_coords
                index = idx
        
        node = ox.distance.nearest_nodes(graph, X=self.middle[1], Y=self.middle[0])
        self.train_distance = type(self)._train_distance_map[index].get(node)