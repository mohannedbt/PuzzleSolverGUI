from gurobipy import Model, GRB
from random import randint as rand
# Crée le modèle
model = Model("Sudoku3x3")
n=int(input("saisir la taille de sudoku"))
if n<1:
    print("La taille doit être au moins 1")
print("Taille du Sudoku:", n, "x", n)
print("-----------------------------")
print("you can't add Empty sudoku if N=1")
# lignes et colonnes = 1,2,3 ; valeurs = 1,2,3
x = {}  # dictionnaire pour stocker les variables
print("Création des variables et contraintes...")
for r in range(1,n+1):
    for c in range(1,n+1):
        for d in range(1,n+1):
            x[(r,c,d)] = model.addVar(vtype=GRB.BINARY, name=f"x_{r}_{c}_{d}")
#unique number per cell
for r in range(1,n+1):
    for c in range(1,n+1):
        model.addConstr(sum(x[(r,c,d)] for d in range(1,n+1))<= 1)
#O shaped constraints
# O-shaped piece (2x2)
for r in range(1, n):      # 1-indexed, fits in grid
    for c in range(1, n):
        model.addConstr(
            sum(x[(rr, cc, 1)] for rr in range(r, r+2) for cc in range(c, c+2)) == 1
        )
model.setObjective(0, GRB.MINIMIZE)
model.optimize()
if model.status == GRB.OPTIMAL:
    # Construire la grille
    grid = [[0]*(n) for _ in range(n)]
    for (r,c,d), var in x.items():
        if var.X > 0.5:
            grid[r-1][c-1] = d


    for row in grid:
        if row:
           print(row)
       
else:
    print("Pas de solution trouvée")
