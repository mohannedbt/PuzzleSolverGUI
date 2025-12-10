import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.grid_builder import build_grid_graph
from core.solver import solve_shortest_path_with_risk

danger = {(1,1), (2,3)}
forbid = {(0,2), (3,1)}


nodes, arcs, dist, risk = build_grid_graph(5, danger,forbid)

status, d, r, path = solve_shortest_path_with_risk(
    nodes, arcs, dist, risk,
    start=(0,0),
    end=(4,4),
    R_max=3.0
)

print("Status:", status)
print("Distance:", d)
print("Risk:", r)
print("Path arcs:", path)
