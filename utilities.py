import osmnx as ox
import networkx as nx

def road_distance(graph, coord1, coord2):
    """
    graph: ox.graph_from_place(city_name, network_type='drive')
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
