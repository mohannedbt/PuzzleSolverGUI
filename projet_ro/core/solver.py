import gurobipy as gp
from gurobipy import GRB

def solve_shortest_path_with_risk(nodes, arcs, dist, risk, start, end, R_max):
    """
    Solve shortest path with risk constraint using Gurobi.
    Returns (status, best_distance, total_risk, path_arcs)
    """

    m = gp.Model("grid_shortest_path")

    # Variables x[a] ∈ {0,1}
    x = m.addVars(arcs, vtype=GRB.BINARY, name="x")

    # Objective: minimize total distance
    m.setObjective(
        gp.quicksum(dist[a] * x[a] for a in arcs),
        GRB.MINIMIZE
    )

    # Risk constraint
    m.addConstr(
        gp.quicksum(risk[a] * x[a] for a in arcs) <= R_max,
        "risk_limit"
    )

    # Flow constraints
    for i in nodes:
        out_i = gp.quicksum(x[a] for a in arcs if a[0] == i)
        in_i  = gp.quicksum(x[a] for a in arcs if a[1] == i)

        if i == start:
            m.addConstr(out_i - in_i == 1, name=f"flow_start_{i}")
        elif i == end:
            m.addConstr(in_i - out_i == 1, name=f"flow_end_{i}")
        else:
            m.addConstr(out_i - in_i == 0, name=f"flow_mid_{i}")

    m.optimize()

    if m.status != GRB.OPTIMAL:
        return "infeasible", None, None, []

    # Extract solution
    solution_arcs = [a for a in arcs if x[a].X > 0.5]

    total_dist = sum(dist[a] * x[a].X for a in arcs)
    total_risk = sum(risk[a] * x[a].X for a in arcs)

    return "optimal", total_dist, total_risk, solution_arcs
