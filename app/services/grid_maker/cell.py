from app.utils import osmnx_helper  

class Cell:
    SIZE = 1000  # length = 1000m
    def __init__(self, ID):
        self.ID = ID
        self.middle = None # [lat, lon]
        self.population = None
        self.center_distance = None
        self.airport_distance = None
        self.metro_station_distances = {}
        self.train_station_distances = {}
    
    def estimate_population(self, buildings):
        pass
    
    def find_center_distance(self, data, graph):
        if (self.middle == None):
            print("Error: Cell does not have a middle point.")
            return
        center_coords = data["coords"]["center"]
        self.center_distance = osmnx_helper.road_distance(graph, self.middle, center_coords)
    
    def find_airport_distance(self, data, graph):
        if (self.middle == None):
            print("Error: Cell does not have a middle point.")
            return
        airport_coords = data["coords"]["airport"]
        self.center_distance = osmnx_helper.road_distance(graph, self.middle, airport_coords)
    
    def find_metro_station_distances(self, data, graph):
        pass
    
    def find_train_station_distances(self, data, graph):
        pass