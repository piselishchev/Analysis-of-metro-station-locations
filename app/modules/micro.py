import osmnx as ox
import geopandas as gpd
import numpy as np
from shapely.geometry import box, Point
from pyproj import Transformer
from app.services.grid_maker.cell import Cell
from app.utils import json_helper, osmnx_helper
from app.utils.cities import CITIES

def find_coords(macro_cell, graph, micro_step=100):
    """
    Анализирует макро-квадрат (обычно 1х1 км) на микро-уровне.
    Ищет пересечения дорог и плотность дорожной сети.
    
    :param macro_cell: Объект класса Cell из cell.py
    :param micro_step: Размер микро-шага в метрах (по умолчанию 10м)
    :return: (list_of_results, cluster_center_lat_lon)
    """
    lat, lon = macro_cell.middle
    print(lat, lon)
    # 1. Загружаем дорожный граф вокруг центра макро-ячейки
    # Используем фильтр, чтобы не учитывать дворовые проезды (только важные дороги)
    custom_filter = '["highway"~"motorway|trunk|primary|secondary|tertiary|residential|unclassified|service"]'
    
    """try:
        # Радиус 750м, чтобы гарантированно покрыть квадрат 1000х1000м
        graph = ox.graph_from_point((lat, lon), dist=750, custom_filter=custom_filter)
    except Exception as e:
        print(f"   [!] Ошибка OSMnx для ячейки {macro_cell.ID}: {e}")
        return (round(lat, 6), round(lon, 6))"""

    # 2. Подготовка геоданных в метрической системе (UTM)
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(graph)
    utm_crs = gdf_edges.estimate_utm_crs()
    gdf_nodes = gdf_nodes.to_crs(utm_crs)
    gdf_edges = gdf_edges.to_crs(utm_crs)
    
    print(1)
    # Трансформеры для перевода координат обратно в Lat/Lon для сайта
    transformer_to_latlon = Transformer.from_crs(utm_crs, "EPSG:4326", always_xy=True)
    transformer_to_utm = Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True)

    # Определяем границы макро-квадрата в UTM
    center_x, center_y = transformer_to_utm.transform(lon, lat)
    half_size = macro_cell._size / 2  # так как макро-квадрат 1000м
    
    min_x, max_x = center_x - half_size, center_x + half_size
    min_y, max_y = center_y - half_size, center_y + half_size
    
    macro_box = box(min_x, min_y, max_x, max_y)
    gdf_edges_local = gdf_edges[gdf_edges.intersects(macro_box)].copy()
    gdf_nodes_local = gdf_nodes[gdf_nodes.intersects(macro_box)].copy()
    
    micro_results = []

    print(2)
    # 3. Сканируем макро-квадрат микро-шагами (например, по 10 метров)
    # Для оптимизации можно увеличить micro_step до 20-30, если работает медленно
    x_coords = np.arange(min_x, max_x, micro_step)
    y_coords = np.arange(min_y, max_y, micro_step)

    print(len(x_coords))
    print(len(y_coords))
    for x in x_coords:
        for y in y_coords:
            # Создаем микро-бокс
            micro_box = box(x, y, x + micro_step, y + micro_step)
            
            m_score = 0
            
            # А) Считаем длину дорог внутри этого микро-квадрата
            intersecting_edges = gdf_edges_local[gdf_edges_local.intersects(micro_box)]
            for _, edge in intersecting_edges.iterrows():
                intersection = edge.geometry.intersection(micro_box)
                m_score += intersection.length # 1 метр дороги = 1 балл
            
            # Б) Считаем перекрестки (узлы, где сходится более 2 дорог)
            intersecting_nodes = gdf_nodes_local[gdf_nodes_local.intersects(micro_box)]
            for node_id, node in intersecting_nodes.iterrows():
                if graph.degree(node_id) > 2:
                    m_score += 15 # Перекресток дает существенный бонус к "удачности" места
            
            if m_score > 0:
                micro_results.append({
                    "pos_utm": (x + micro_step/2, y + micro_step/2),
                    "score": m_score
                })

    if not micro_results:
        return None

    # 4. Поиск "центра притяжения"
    # Сортируем результаты по убыванию баллов
    micro_results.sort(key=lambda x: x['score'], reverse=True)
    x = micro_results[0]["pos_utm"][0]
    y = micro_results[0]["pos_utm"][1]

    # Конвертируем финальную точку обратно в географические координаты
    final_lon, final_lat = transformer_to_latlon.transform(x, y)

    return (round(final_lat, 6), round(final_lon, 6))



'''
city = CITIES.N_NOVGOROD

data = json_helper.get_data(city)
if data == None:
    print(f"Failed to create grid: could not load {city}.json.")

city_fullname = data["city"]
  
Cell._size = 1000

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

transformer = Transformer.from_crs(
    utm_crs,
    original_crs,
    always_xy=True
)

print("Loading graph...")
G = osmnx_helper.load_graph(city)
graph = ox.truncate.largest_component(G, strongly=True)
print("Done!")

cell = Cell(0)
lon, lat = 44.006518, 56.326796
cell.middle = [round(lat, 6), round(lon, 6)]
print("Done")


print("STARTING MICRO!!!")
find_coords(cell)
print("Done")'''