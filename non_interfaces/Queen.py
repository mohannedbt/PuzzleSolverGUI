from gurobipy import Model, GRB

# --- Inputs ---
print("choose piece: 1 for Queen, 2 for Rook, 3 for Bishop")
piece= int(input("Enter the number of the piece: "))
n = int(input("Enter board size N: "))
k = int(input("Enter number of Piece K (< N): "))
if k > n and piece ==1:
    raise ValueError("K must be <= N")

# --- Create model ---
model = Model("K_Pieces_on_NxN_Board")
x = {}
if piece == 2:
    print("Rook selected")
elif piece == 3:
    print("Bishop selected")
else:
    print("Queen selected")
# --- Binary variables: 1 if Piece at (r,c), 0 otherwise ---
for r in range(1,n+1):
    for c in range(1,n+1):
        x[(r,c)] = model.addVar(vtype=GRB.BINARY, name=f"x_{r}_{c}")
if piece ==2  or piece ==1:
    # --- Row constraints: at most one Piece per row ---
    for r in range(1,n+1):
        model.addConstr(sum(x[(r,c)] for c in range(1,n+1)) <= 1)
    # --- Column constraints: at most one Piece per column ---
    for c in range(1,n+1):
        model.addConstr(sum(x[(r,c)] for r in range(1,n+1)) <= 1)
if piece ==3  or piece ==1:
# --- Diagonal constraints: at most one Piece per diagonal ---
    for d in range(-(n-1), n):
        model.addConstr(
            sum(
                x[(r,c)] for r in range(1,n+1) for c in range(1,n+1) if r-c == d
            ) <= 1
        )
    for d in range(2, 2*n):
        model.addConstr(
            sum(
                x[(r,c)] for r in range(1,n+1) for c in range(1,n+1) if r+c == d
            ) <= 1
        )
# --- Total Pieces = K ---
model.addConstr(sum(x[(r,c)] for r in range(1,n+1) for c in range(1,n+1)) == k)

# --- Objective (feasibility problem) ---
model.setObjective(0, GRB.MINIMIZE)

# --- Solve ---
model.optimize()

# --- Display solution ---
if model.status == GRB.OPTIMAL:
    grid = [[0]*n for _ in range(n)]
    for (r,c), var in x.items():
        if var.X > 0.5:
            grid[r-1][c-1] = 1
    for row in grid:
        print(row)
else:
    print("No solution found")
