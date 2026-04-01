# В файле app/modules/citymap.py
from flask import Blueprint, render_template, request, jsonify
from app.services.grid_maker import create_grid
from app.utils.cities import CITIES
from flask import current_app
from app.utils import osmnx_helper

citymap = Blueprint('citymap', __name__)

@citymap.route('/submit', methods=['POST'])
def submit_analysis():
    data = request.get_json() or {}

    n_stations = int(data.get("n_stations", 3))
    criteria = data.get("criteria", [])
    
    from .. import macro
    from .. import micro
    
    if not hasattr(current_app, 'grid'):
        current_app.grid = create_grid(CITIES.N_NOVGOROD)
    _grid = current_app.grid
    print("Grid acquired!")
    
    G = osmnx_helper.load_graph(CITIES.N_NOVGOROD)
    
    results = {"results": []}
    print("Going to macro...")
    best_macro_cells = macro.select_cells(_grid, n_stations, criteria)
    print("Done!")
    idx = 1
    for macro_cell, score in best_macro_cells:
        print(f"Going to micro ({idx})...")
        coords = micro.find_coords(macro_cell, G)
        print("Done!")
        info = {
            "name": f"Локация №{idx}",
            "lat": coords[0],
            "lon": coords[1],
            "score": score,
            "population": macro_cell.population,
            "center": macro_cell.center_distance,
            "airport": macro_cell.airport_distance,
            "metro": macro_cell.metro_distance,
            "train": macro_cell.train_distance
        }
        idx += 1
        results["results"].append(info)
    
    return jsonify(results)


@citymap.route('/map/Nizhny-Novgorod')
def map_page():
    return render_template("map.html", background_image="citymap.jpg")
