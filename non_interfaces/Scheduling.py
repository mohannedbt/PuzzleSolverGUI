"""
Graph Coloring - Exam Scheduling Problem (Console Version)
MIP Formulation: Assign minimum time slots to exams so students don't have conflicts
Conflicts: Same filière OR same teacher
"""

from gurobipy import Model, GRB


def parse_exam_data(exam_list):
    """
    Parse exam data with attributes.
    exam_list: list of tuples (name, filière, teacher)
    Returns: list of exam dicts, auto-generated edges
    """
    exams = []
    for name, filiere, teacher in exam_list:
        exams.append({
            'name': name,
            'filiere': filiere,
            'teacher': teacher
        })
    
    # Auto-generate conflicts
    edges = []
    for i in range(len(exams)):
        for j in range(i+1, len(exams)):
            # Conflict if same filière OR same teacher
            if exams[i]['filiere'] == exams[j]['filiere'] or \
               exams[i]['teacher'] == exams[j]['teacher']:
                edges.append((i, j))
    
    return exams, edges


def build_adjacency(num_vertices, edges):
    """Build adjacency list from edges"""
    graph = {i: set() for i in range(num_vertices)}
    for u, v in edges:
        if u != v:
            graph[u].add(v)
            graph[v].add(u)
    return graph


def solve_graph_coloring(num_vertices, edges):
    """
    Solve graph coloring problem using Gurobi MIP
    
    Variables:
    - x[v][c] = 1 if vertex v gets color c
    - y[c] = 1 if color c is used
    
    Constraints:
    - Each vertex gets exactly one color
    - Adjacent vertices have different colors
    
    Objective: Minimize number of colors used
    """
    
    graph = build_adjacency(num_vertices, edges)
    
    # Upper bound on colors
    max_colors = max([len(graph[v]) for v in graph]) + 1
    max_colors = max(max_colors, 2)
    
    # Create model
    model = Model("ExamScheduling")
    model.setParam("OutputFlag", 0)
    
    # Decision variables
    x = {}
    for v in range(num_vertices):
        for c in range(max_colors):
            x[(v, c)] = model.addVar(vtype=GRB.BINARY, name=f"x_{v}_{c}")
    
    y = {}
    for c in range(max_colors):
        y[c] = model.addVar(vtype=GRB.BINARY, name=f"y_{c}")
    
    # Constraint 1: Each vertex gets exactly one color
    for v in range(num_vertices):
        model.addConstr(
            sum(x[(v, c)] for c in range(max_colors)) == 1,
            name=f"vertex_color_{v}"
        )
    
    # Constraint 2: Adjacent vertices have different colors
    for u in graph:
        for v in graph[u]:
            if u < v:
                for c in range(max_colors):
                    model.addConstr(
                        x[(u, c)] + x[(v, c)] <= 1,
                        name=f"adjacent_{u}_{v}_{c}"
                    )
    
    # Constraint 3: y[c] indicates if color c is used
    for c in range(max_colors):
        for v in range(num_vertices):
            model.addConstr(
                y[c] >= x[(v, c)],
                name=f"use_color_{c}_{v}"
            )
    
    # Objective: minimize number of colors
    model.setObjective(sum(y[c] for c in range(max_colors)), GRB.MINIMIZE)
    model.optimize()
    
    if model.status != GRB.OPTIMAL:
        return None, None
    
    # Extract solution
    coloring = {}
    for v in range(num_vertices):
        for c in range(max_colors):
            if x[(v, c)].X > 0.5:
                coloring[v] = c
                break
    
    num_colors_used = int(sum(y[c].X for c in range(max_colors)))
    
    # Renumber colors to be consecutive (0, 1, 2, ..., num_colors_used-1)
    # This ensures no gaps in slot numbering
    used_colors = sorted(set(coloring.values()))
    color_mapping = {old_color: new_color for new_color, old_color in enumerate(used_colors)}
    coloring = {v: color_mapping[c] for v, c in coloring.items()}
    
    return coloring, num_colors_used


def display_solution(exams, coloring, num_colors, num_vertices):
    """Pretty print the solution with exam details"""
    
    if coloring is None:
        print("\n❌ No feasible coloring found!")
        return
    
    print("\n" + "=" * 70)
    print("OPTIMAL EXAM SCHEDULING SOLUTION")
    print("=" * 70)
    
    # Group exams by time slot
    slot_groups = {}
    for exam_idx in range(num_vertices):
        slot = coloring[exam_idx]
        if slot not in slot_groups:
            slot_groups[slot] = []
        slot_groups[slot].append(exam_idx)
    
    print(f"\n📅 SCHEDULE ({num_colors} Time Slots):\n")
    for slot in sorted(slot_groups.keys()):
        exam_indices = slot_groups[slot]
        exam_names = [exams[idx]['name'] for idx in exam_indices]
        print(f"  Time Slot {slot + 1}:")
        for name in exam_names:
            print(f"    • {name}")
        print()
    
    print("=" * 70)
    print(f"📊 STATISTICS:")
    print(f"  • Total Exams: {num_vertices}")
    print(f"  • Time Slots Required: {num_colors}")
    print(f"  • Exams per Slot: {[len(slot_groups[s]) for s in sorted(slot_groups.keys())]}")
    
    print(f"\n📋 EXAM DETAILS:\n")
    print(f"{'Exam Name':<20} {'Slot':<8} {'Filière':<15} {'Teacher':<20}")
    print("-" * 70)
    for idx, exam in enumerate(exams):
        slot = coloring[idx]
        print(f"{exam['name']:<20} {slot + 1:<8} {exam['filiere']:<15} {exam['teacher']:<20}")
    
    print("\n" + "=" * 70)


def example_1():
    """Example 1: Realistic university exam scheduling"""
    print("\n🔍 EXAMPLE 1: University Exam Scheduling (CS Department)")
    
    exams_data = [
        ("Math101", "CS1", "Prof. Smith"),
        ("Physics101", "CS1", "Prof. Jones"),
        ("Chemistry101", "CS2", "Prof. Smith"),
        ("Biology101", "CS2", "Prof. Brown"),
        ("Economics101", "CS1", "Prof. Adams"),
    ]
    
    exams, edges = parse_exam_data(exams_data)
    return exams, edges, len(exams)


def example_2():
    """Example 2: All exams same filière (all conflict)"""
    print("\n🔍 EXAMPLE 2: All Exams Same Filière")
    
    exams_data = [
        ("DataStructures", "CS1", "Prof. Smith"),
        ("Algorithms", "CS1", "Prof. Jones"),
        ("Database", "CS1", "Prof. Brown"),
        ("WebDev", "CS1", "Prof. Adams"),
        ("AI", "CS1", "Prof. Lee"),
    ]
    
    exams, edges = parse_exam_data(exams_data)
    return exams, edges, len(exams)


def example_3():
    """Example 3: Multiple teachers teaching multiple filières"""
    print("\n🔍 EXAMPLE 3: Complex Schedule with Shared Teachers")
    
    exams_data = [
        ("Math101", "CS1", "Prof. Smith"),
        ("Physics101", "ENG1", "Prof. Smith"),
        ("Chemistry101", "CS2", "Prof. Jones"),
        ("Biology101", "ENG2", "Prof. Jones"),
        ("Economics101", "CS1", "Prof. Brown"),
        ("History101", "ENG1", "Prof. Adams"),
    ]
    
    exams, edges = parse_exam_data(exams_data)
    return exams, edges, len(exams)


if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 70)
    print("EXAM SCHEDULING - GRAPH COLORING SOLVER")
    print("Automatically generates conflicts based on filière & teacher")
    print("=" * 70)
    
    # Run examples
    examples = [example_1(), example_2(), example_3()]
    
    for exams, edges, num_vertices in examples:
        print(f"\nGraph: {num_vertices} exams, {len(edges)} conflicts")
        
        coloring, num_colors = solve_graph_coloring(num_vertices, edges)
        display_solution(exams, coloring, num_colors, num_vertices)
