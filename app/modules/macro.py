import heapq

def calculate_value(cell, criteria=None):
    # тут должны быть формулы
    poulation_val = 0
    if "population" in criteria:
        poulation_val = 2 * cell.population
    
    center_dist_val = 0
    if 'center' in criteria:
        center_dist_val = 2 * cell.center_distance
    
    airport_dist_val = 0 
    if 'airport' in criteria:
        airport_dist_val = 2 * cell.airport_distance
        
    metro_dist_val = 0
    if 'metro' in criteria:
        metro_dist_val = 2 * cell.metro_distance
    
    train_dist_val = 0
    if 'train' in criteria:
        train_dist_val = 2 * cell.train_distance

    return poulation_val + center_dist_val + airport_dist_val + metro_dist_val + train_dist_val

def select_cells(grid, n=1, criteria=None):
    evaluated_cells = [[x, calculate_value(x, criteria)] for x in grid]
    return heapq.nlargest(n, evaluated_cells, key = lambda x: x[1])