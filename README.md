# Analysis of metro station locations
 
Explore our analitical system which is a tool to find good places for new metro stations. Open data and road networks are in used.
 
## What it does
 
The program splits the city into 1 km squares, then rates each square based on:
 
- how many people live there
- distance to existing metro stations
- distance to city center
- distance to airport and train stations
 
Then it picks the best squares, and inside each square it looks for the exact best spot (near roads, intersections, etc.).
 
## How to run
 
You need Python 3.9 or newer.
 
1. Install required packages:
 
   pip install scikit-learn, osmnx, flask, geopy
 
2. Run the Main.py file
 
3. Open http://127.0.0.1:5000/ in your browser.
 
## What you see on the map
 
- Red circles with "M" – existing metro stations
- Green circles with "Ж" – railway stations
- Blue circles with "Н" – places the algorithm suggests
 
You can click on any marker to see details.
 
## Notes
 
First run will be slow because OSMnx downloads road data. After that it caches locally.
 
The project was tested on Nizhny Novgorod, Russia. For other cities you need to adjust the JSON file and possibly the UTM zone.
