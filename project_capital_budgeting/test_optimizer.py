from optimizer import optimize_projects   # on importe ton fichier corrigé

# ===================== DONNÉES = EXEMPLE DE TEST ===================== #
projects = [
    { "global": { "budget":120000 , "employees":15 , "machines":10 }},

    { "name":"Projet 1", "VAN":44319 , "I0":50000 , "emp":5 , "mach":3 },
    { "name":"Projet 2", "VAN":28732 , "I0":40000 , "emp":4 , "mach":2 },
    #{ "name":"Projet 3", "VAN":46455 , "I0":70000 , "emp":7 , "mach":5 },
   # { "name":"Projet 4", "VAN":11983 , "I0":30000 , "emp":3 , "mach":1 }
]

# ===================== LANCEMENT OPTIMISATION ===================== #
selected, total_van = optimize_projects(projects)

print("\n===== 📌 RESULTAT OPTIMISATION GUROBI =====")
print("Projets sélectionnés :")
for p in selected:
    print("  ➤", p)

print(f"\n💰 VAN Totale Maximisée = {total_van:.2f} TND")
print("=================================================\n")
