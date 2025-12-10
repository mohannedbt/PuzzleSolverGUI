def build_grid_graph(n, dangerous_cells=None, forbidden_cells=None, diagonal=False):
    """
    Build a grid of size n x n and return:
        nodes: list of (i,j)
        arcs: list of ((i,j),(k,l))
        dist: dict {arc: distance}
        risk: dict {arc: risk_value}
    """

    if dangerous_cells is None:
        dangerous_cells = set()

    if forbidden_cells is None:
        forbidden_cells = set()

    nodes = []
    arcs = []
    dist = {}
    risk = {}

    # 1) Add all nodes
    for i in range(n):
        for j in range(n):
            nodes.append((i, j))

    # 2) Allowed directions (4-neighbors)
    directions = [
        (0, 1),   # right
        (0, -1),  # left
        (1, 0),   # down
        (-1, 0),  # up
    ]
    if diagonal:
        directions += [
            (1, 1), (1, -1),
            (-1, 1), (-1, -1)
        ]

    # 3) Build arcs with distance and risk
    for i in range(n):
        for j in range(n):

            # Skip forbidden source node
            if (i, j) in forbidden_cells:
                continue

            for dx, dy in directions:
                ni = i + dx
                nj = j + dy

                # Check inside grid
                if 0 <= ni < n and 0 <= nj < n:

                    # Skip forbidden destination
                    if (ni, nj) in forbidden_cells:
                        continue

                    arc = ((i, j), (ni, nj))
                    arcs.append(arc)

                    # Distances are uniform
                    dist[arc] = 1.0

                    # Compute the risk according to your rule:
                    src_danger = (i, j) in dangerous_cells
                    dst_danger = (ni, nj) in dangerous_cells

                    risk_value=0.0001

                    if src_danger and dst_danger:
                        risk_value = 0.8      # both dangerous → high risk
                    elif src_danger ^ dst_danger:  
                        risk_value = 0.4      # xor : only one is dangerous → medium

                    risk[arc] = risk_value

    return nodes, arcs, dist, risk
