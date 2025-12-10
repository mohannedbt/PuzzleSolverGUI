"""
Assembly Line Balancing Problem - Type I (with Dual Time Analysis)
MILP Formulation: Assign tasks to workstations minimizing station count
while respecting precedence constraints and cycle time limits.
"""

from gurobipy import Model, GRB
import math


def parse_task_input(text_input):
    """
    Parse input text in format:
    task <name> max <max_time> avg <avg_time>
    ...
    max_cycle <value>
    
    Returns: (tasks, t_max, t_avg, C_max) or raises ValueError
    """
    lines = [l.strip() for l in text_input.strip().split('\n') if l.strip()]
    
    tasks = []
    t_max = []
    t_avg = []
    C_max = None
    
    for line in lines:
        tokens = line.split()
        
        if tokens[0].lower() == 'task':
            # Format: task <name> max <value> avg <value>
            if len(tokens) < 4:
                raise ValueError(f"Invalid task format: {line}")
            
            name = tokens[1]
            
            max_val = None
            avg_val = None
            
            i = 2
            while i < len(tokens):
                if tokens[i].lower() == 'max' and i + 1 < len(tokens):
                    max_val = float(tokens[i + 1])
                    i += 2
                elif tokens[i].lower() == 'avg' and i + 1 < len(tokens):
                    avg_val = float(tokens[i + 1])
                    i += 2
                else:
                    i += 1
            
            if max_val is None:
                raise ValueError(f"Task {name} missing max duration")
            
            tasks.append(name)
            t_max.append(max_val)
            t_avg.append(avg_val if avg_val is not None else max_val)
        
        elif tokens[0].lower() == 'max_cycle':
            if len(tokens) < 2:
                raise ValueError("max_cycle requires a value")
            C_max = float(tokens[1])
    
    if not tasks:
        raise ValueError("No tasks found in input")
    if C_max is None:
        raise ValueError("max_cycle not specified")
    if C_max <= 0:
        raise ValueError("max_cycle must be positive")
    
    # Validate task times
    for i, (name, t, a) in enumerate(zip(tasks, t_max, t_avg)):
        if t <= 0:
            raise ValueError(f"Task {name} max duration must be positive")
        if a <= 0:
            raise ValueError(f"Task {name} avg duration must be positive")
        if t > C_max:
            raise ValueError(f"Task {name} max duration ({t}) exceeds C_max ({C_max}) - infeasible")
    
    return tasks, t_max, t_avg, C_max


def balance_line(t_max, precedence=None, C_max=60, t_avg=None, tasks=None):
    """
    Assembly line balancing with dual time analysis.
    
    Parameters:
    -----------
    t_max : list[float]
        Maximum/worst-case durations for n tasks
    precedence : list[tuple], adjacency matrix, or None
        Precedence constraints as pairs (i,j) where i must precede j
        OR adjacency matrix where precedence[i][j]=1 if i precedes j
    C_max : float
        Maximum allowed cycle time per station
    t_avg : list[float] or None
        Average/expected durations (same length as t_max)
    tasks : list[str] or None
        Task names for reporting
    
    Returns:
    --------
    dict with keys:
        'assignment': list[list[int]] - task indices per station
        'stations_used': int
        'cycle_times_max': list[float] - actual cycle time per station (max times)
        'cycle_times_avg': list[float] - cycle time per station (avg times)
        'efficiency_max': float - overall line efficiency (%)
        'efficiency_avg': float or None
        'station_efficiencies_max': list[float] - per station (%)
        'station_efficiencies_avg': list[float] or None
        'balance_delay': float - percentage of idle time (%)
        'theoretical_min_stations': int
        'is_optimal': bool
        'actual_max_cycle': float - max cycle across all stations (max times)
        'actual_avg_cycle': float or None - max cycle across all stations (avg times)
    """
    
    n = len(t_max)
    
    # Default values
    if t_avg is None:
        t_avg = t_max.copy()
    
    if tasks is None:
        tasks = [f"Task{i}" for i in range(n)]
    
    # Validate inputs
    if len(t_max) != len(t_avg):
        raise ValueError("t_max and t_avg must have same length")
    
    if C_max <= 0:
        raise ValueError("C_max must be positive")
    
    for i, (tm, ta) in enumerate(zip(t_max, t_avg)):
        if tm > C_max:
            raise ValueError(f"Task {i} max duration ({tm}) exceeds C_max ({C_max})")
    
    # Parse precedence constraints
    edges = []
    if precedence is not None:
        if isinstance(precedence, list):
            if precedence and isinstance(precedence[0], tuple):
                edges = list(precedence)
            elif precedence and isinstance(precedence[0], (list, tuple)) and len(precedence[0]) > 0:
                # Adjacency matrix
                for i in range(len(precedence)):
                    for j in range(len(precedence[i])):
                        if precedence[i][j] == 1:
                            edges.append((i, j))
    
    # Build MILP model
    model = Model("AssemblyLineBalance")
    model.setParam("OutputFlag", 0)
    
    # Decision variables
    # x[i][k] = 1 if task i is assigned to station k
    x = {}
    for i in range(n):
        for k in range(n):
            x[(i, k)] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{k}")
    
    # y[k] = 1 if station k is used
    y = {}
    for k in range(n):
        y[k] = model.addVar(vtype=GRB.BINARY, name=f"y_{k}")
    
    # Constraint 1: Each task assigned to exactly one station
    for i in range(n):
        model.addConstr(
            sum(x[(i, k)] for k in range(n)) == 1,
            name=f"assign_{i}"
        )
    
    # Constraint 2: Station load <= C_max (using max durations)
    for k in range(n):
        model.addConstr(
            sum(t_max[i] * x[(i, k)] for i in range(n)) <= C_max * y[k],
            name=f"capacity_{k}"
        )
    
    # Constraint 3: Precedence constraints
    # If (i, j) in edges, then station(i) <= station(j)
    for (i, j) in edges:
        model.addConstr(
            sum(k * x[(i, k)] for k in range(n)) <= sum(k * x[(j, k)] for k in range(n)),
            name=f"prec_{i}_{j}"
        )
    
    # Constraint 4: Station ordering (symmetry breaking)
    # y[k] >= y[k+1] ensures consecutive station numbering
    for k in range(n - 1):
        model.addConstr(y[k] >= y[k + 1], name=f"order_{k}")
    
    # Objective: minimize number of stations
    model.setObjective(sum(y[k] for k in range(n)), GRB.MINIMIZE)
    model.optimize()
    
    if model.status != GRB.OPTIMAL:
        return {
            'assignment': [],
            'stations_used': 0,
            'cycle_times_max': [],
            'cycle_times_avg': [],
            'efficiency_max': None,
            'efficiency_avg': None,
            'station_efficiencies_max': [],
            'station_efficiencies_avg': [],
            'balance_delay': None,
            'theoretical_min_stations': math.ceil(sum(t_max) / C_max),
            'is_optimal': False,
            'actual_max_cycle': None,
            'actual_avg_cycle': None,
            'error': "No feasible solution found"
        }
    
    # Extract solution
    assignment = [[] for _ in range(n)]
    stations_used = 0
    
    for k in range(n):
        if y[k].X > 0.5:
            stations_used += 1
            for i in range(n):
                if x[(i, k)].X > 0.5:
                    assignment[k].append(i)
    
    # Keep only used stations
    assignment = [s for s in assignment if s]
    
    # Calculate metrics
    cycle_times_max = []
    cycle_times_avg = []
    station_efficiencies_max = []
    station_efficiencies_avg = []
    
    total_time_max = sum(t_max)
    total_time_avg = sum(t_avg)
    
    for station_tasks in assignment:
        load_max = sum(t_max[i] for i in station_tasks)
        load_avg = sum(t_avg[i] for i in station_tasks)
        
        cycle_times_max.append(load_max)
        cycle_times_avg.append(load_avg)
        
        eff_max = (load_max / C_max) * 100
        eff_avg = (load_avg / C_max) * 100
        
        station_efficiencies_max.append(eff_max)
        station_efficiencies_avg.append(eff_avg)
    
    # Overall metrics
    efficiency_max = (total_time_max / (stations_used * C_max)) * 100
    efficiency_avg = (total_time_avg / (stations_used * C_max)) * 100
    balance_delay = 100 - efficiency_max
    
    actual_max_cycle = max(cycle_times_max) if cycle_times_max else 0
    actual_avg_cycle = max(cycle_times_avg) if cycle_times_avg else 0
    
    theoretical_min = math.ceil(total_time_max / C_max)
    is_optimal = (stations_used == theoretical_min)
    
    return {
        'assignment': assignment,
        'stations_used': stations_used,
        'cycle_times_max': cycle_times_max,
        'cycle_times_avg': cycle_times_avg,
        'efficiency_max': efficiency_max,
        'efficiency_avg': efficiency_avg,
        'station_efficiencies_max': station_efficiencies_max,
        'station_efficiencies_avg': station_efficiencies_avg,
        'balance_delay': balance_delay,
        'theoretical_min_stations': theoretical_min,
        'is_optimal': is_optimal,
        'actual_max_cycle': actual_max_cycle,
        'actual_avg_cycle': actual_avg_cycle,
        'tasks': tasks
    }


def display_solution(result, t_max, t_avg):
    """Pretty print the solution"""
    
    if result.get('error'):
        return f"❌ {result['error']}\n"
    
    output = []
    output.append("=" * 70)
    output.append("ASSEMBLY LINE BALANCING SOLUTION")
    output.append("=" * 70)
    output.append("")
    
    # Metrics
    output.append(f"Stations Used: {result['stations_used']}")
    output.append(f"Theoretical Minimum: {result['theoretical_min_stations']}")
    output.append(f"Is Optimal: {'Yes' if result['is_optimal'] else 'No'}")
    output.append("")
    
    output.append("Using Maximum Durations (Worst-Case):")
    output.append(f"  Overall Efficiency: {result['efficiency_max']:.2f}%")
    output.append(f"  Balance Delay: {result['balance_delay']:.2f}%")
    output.append(f"  Max Cycle Time: {result['actual_max_cycle']:.2f}")
    output.append("")
    
    output.append("Using Average Durations (Expected):")
    output.append(f"  Overall Efficiency: {result['efficiency_avg']:.2f}%")
    output.append(f"  Max Cycle Time: {result['actual_avg_cycle']:.2f}")
    output.append("")
    
    # Station details
    output.append("Station Assignments:")
    for k, station_tasks in enumerate(result['assignment']):
        task_names = [result['tasks'][i] for i in station_tasks]
        output.append(
            f"  Station {k + 1}: {', '.join(task_names)}"
        )
        output.append(
            f"    Max Load: {result['cycle_times_max'][k]:.2f} "
            f"(Eff: {result['station_efficiencies_max'][k]:.1f}%)"
        )
        output.append(
            f"    Avg Load: {result['cycle_times_avg'][k]:.2f} "
            f"(Eff: {result['station_efficiencies_avg'][k]:.1f}%)"
        )
    
    return "\n".join(output)
