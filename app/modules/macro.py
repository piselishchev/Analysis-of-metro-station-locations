import heapq
import numpy as np
import math

def calculate_value(cell, criteria=None):
    # Если население меньше 1000, сразу возвращаем 0
    if cell.population < 1000:
        return 0

    # Запрещаем ячейки, расположенные ближе 500 м к любой существующей станции метро
    if cell.metro_distance is not None and cell.metro_distance < 500:
        return 0

    population_val = 0
    if "population" in criteria:
        population_val = cell.population / 5000

    center_dist_val = 0
    if 'center' in criteria:
        x = cell.center_distance / 1000
        center_dist_val = 1 / (0.6 + math.exp(x - 4))
    
    airport_dist_val = 0 
    if 'airport' in criteria:
        x = cell.airport_distance / 1000 
        airport_dist_val = 1 / (0.5 + math.exp(5.3 * (x - 1)))
        
    metro_dist_val = 0
    if 'metro' in criteria:
        x = cell.metro_distance / 2000
        exp1 = math.exp(-0.1 * x)
        exp2 = math.exp(-4 * x)
        metro_dist_val = -math.exp(1.6) * exp2 + 6 / ((1 + math.exp(0.1) * exp1) * (1 + math.e * exp1))
    
    train_dist_val = 0
    if 'train' in criteria:
        x = cell.train_distance / 1000
        train_dist_val = 1 / (0.8 + math.exp(3 * x - 5.1))

    return population_val + center_dist_val + airport_dist_val + metro_dist_val + train_dist_val

def select_cells(grid_matrix, n=1, criteria=None):
    """
    Выбирает n лучших ячеек с запретом соседних (включая диагонали).
    Принимает матрицу (2D список) и возвращает список [cell, score].
    Ячейки с населением < 1000, с баллом < 0.1 или расположенные ближе 500 м к метро игнорируются.
    """
    rows = len(grid_matrix)
    cols = len(grid_matrix[0]) if rows > 0 else 0
    
    # Сбор всех существующих ячеек, прошедших предварительные фильтры
    cells_with_scores = []
    for i in range(rows):
        for j in range(cols):
            cell = grid_matrix[i][j]
            if cell is None:
                continue
            if cell.population < 1000:
                continue
            if cell.metro_distance is not None and cell.metro_distance < 500:
                continue
            score = calculate_value(cell, criteria)
            if score >= 0.1:
                cells_with_scores.append((score, i, j, cell))
    
    # Сортировка по убыванию оценки
    cells_with_scores.sort(key=lambda x: x[0], reverse=True)
    
    # Матрица запретов
    forbidden = [[False] * cols for _ in range(rows)]
    
    selected = []  # список пар [cell, score]
    
    for score, i, j, cell in cells_with_scores:
        if len(selected) >= n:
            break
        if forbidden[i][j]:
            continue
        
        selected.append([cell, score])
        
        # Запрещаем все соседние клетки (включая текущую)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                ni, nj = i + di, j + dj
                if 0 <= ni < rows and 0 <= nj < cols:
                    forbidden[ni][nj] = True
    
    return selected