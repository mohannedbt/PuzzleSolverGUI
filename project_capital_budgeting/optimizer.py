from gurobipy import Model, GRB

def optimize_projects(projects):
    """
    projects = [
        { "global": { "budget":B , "employees":E , "machines":M } },
        { "VAN":X , "I0":Y , "emp":A , "mach":B , "name":"Projet 1" },
        { "VAN":... }, ...
    ]
    """

    # Sécurité : liste vide
    if not projects:
        return [], 0.0

    # 1) Récupérer les données globales dans projects[0]
    if "global" not in projects[0]:
        raise ValueError("Le premier élément de la liste 'projects' doit contenir la clé 'global'.")

    global_data = projects[0]["global"]
    budget   = float(global_data.get("budget", 0))
    emp_tot  = float(global_data.get("employees", 0))
    mach_tot = float(global_data.get("machines", 0))

    # 2) Extraire la liste des vrais projets (on ignore l'index 0)
    proj_list = projects[1:]
    n = len(proj_list)

    if n == 0:
        # Aucun projet à optimiser
        return [], 0.0

    # 3) Modèle Gurobi
    model = Model("Capital_Budgeting")
    # Optionnel: couper l'affichage Gurobi si tu veux
    # model.setParam('OutputFlag', 0)

    # Variables binaires x_i pour chaque projet
    x = model.addVars(n, vtype=GRB.BINARY, name="x")

    # 4) Fonction objectif : somme des VAN des projets sélectionnés
    model.setObjective(
        sum(proj_list[i]["VAN"] * x[i] for i in range(n)),
        GRB.MAXIMIZE
    )

    # 5) Contraintes
    # Budget
    model.addConstr(
        sum(proj_list[i]["I0"] * x[i] for i in range(n)) <= budget,
        "Budget"
    )

    # Employés
    model.addConstr(
        sum(proj_list[i]["emp"] * x[i] for i in range(n)) <= emp_tot,
        "Employees"
    )

    # Machines
    model.addConstr(
        sum(proj_list[i]["mach"] * x[i] for i in range(n)) <= mach_tot,
        "Machines"
    )

    # 6) Optimisation
    model.optimize()

    # 7) Récupération de la solution
    selected = []
    if model.status == GRB.OPTIMAL or model.status == GRB.SUBOPTIMAL:
        for i in range(n):
            if x[i].X > 0.5:
                selected.append(proj_list[i]["name"])
        total_van = model.objVal
    else:
        # Pas de solution faisable
        total_van = 0.0

    return selected, total_van
