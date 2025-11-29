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
for r in range(1,n+1):
    for c in range(1,n+1):
        model.addConstr(sum(x[(r,c,d)] for d in range(1,n+1)) == 1)
for r in range(1,n+1):
    for d in range(1,n+1):
        model.addConstr(sum(x[(r,c,d)] for c in range(1,n+1)) == 1)
for c in range(1,n+1):
    for d in range(1,n+1):
        model.addConstr(sum(x[(r,c,d)] for r in range(1,n+1)) == 1)
model.setObjective(0, GRB.MINIMIZE)
model.optimize()
if model.status == GRB.OPTIMAL:
    # Construire la grille
    grid = [[0]*(n) for _ in range(n)]
    for (r,c,d), var in x.items():
        if var.X > 0.5:
            grid[r-1][c-1] = d
    # Afficher la grille
    eliminate=0
    while True and n>1:
       eliminate=int(input("saisir le nombre de cases à éliminer"))
       if eliminate<n*n:
           break
       else:
           print("Le nombre de cases à éliminer doit être inférieur à",n*n)
    list_eliminate=[]
    while len(list_eliminate)<eliminate:
        i=rand(0,n-1)
        j=rand(0,n-1)
        if (i,j) not in list_eliminate:
            list_eliminate.append((i,j))
            grid[i][j]=" " 
    index=1
    for row in grid:
        if row:
           print(row)
        index+=1
else:
    print("Pas de solution trouvée")
