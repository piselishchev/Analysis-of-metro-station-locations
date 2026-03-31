import osmnx as ox
import networkx as nx
from pathlib import Path
from app.config import Config
from app.utils import json_helper
import geopandas as gpd


def load_graph(city, network_type="drive"):
    filename = f"graph_{network_type}.graphml"
    filepath = Config.DATA_DIR / "cities" / city / filename
    
    if filepath.exists():
        return ox.load_graphml(filepath)
    
    data = json_helper.get_data(city)
    if data == None:
        print(f"Failed to load graph: could not load {city}.json.")
        return
    
    city_fullname = data["city"]
    
    G = ox.graph_from_place(city_fullname, network_type=network_type)
    ox.save_graphml(G, filepath)
    return G


def road_distance(graph, coord1, coord2):
    """
    graph = ox.truncate.largest_component(G, strongly=True)
    G: ox.graph_from_place(city_name, network_type='drive')
    coord1, coord2: (lat, lon)
    returns: shortest road distance in meters
    """

    orig_node = ox.distance.nearest_nodes(graph, X=coord1[1], Y=coord1[0])
    dest_node = ox.distance.nearest_nodes(graph, X=coord2[1], Y=coord2[0])
    
    
    distance = nx.shortest_path_length(
        graph,
        orig_node,
        dest_node,
        weight='length' 
    )

    return distance

def build_distance_map_to_target(graph, target_coord):
    target_node = ox.distance.nearest_nodes(graph, X=target_coord[1], Y=target_coord[0])

    distances = nx.single_source_dijkstra_path_length(
        graph,
        target_node,
        weight="length"
    )
    return distances