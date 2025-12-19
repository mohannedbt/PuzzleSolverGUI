"""
Assembly Line Balancing Problem - Type I (with Dual Time Analysis)
MILP Formulation: Assign tasks to workstations minimizing station count
while respecting precedence constraints and cycle time limits.
"""

import math
import gurobipy as gp
from gurobipy import GRB


def parse_task_input(text_input):
    """
    Parse input text in format:
    task <name> max <max_time> avg <avg_time>
    dep <task_name> <dependent_task_name>
    ...
    max_cycle <value>
    
    Returns: (tasks, t_max, t_avg, C_max, dependencies) or raises ValueError
    """
    lines = [l.strip() for l in text_input.strip().split('\n') if l.strip()]
    
    tasks = []
    task_to_index = {}
    t_max = []
    t_avg = []
    C_max = None
    dependencies_str = []  # Temporary storage for string dependencies
    
    for line_num, line in enumerate(lines, 1):
        tokens = line.split()
        if not tokens:
            continue
            
        cmd = tokens[0].lower()
        
        if cmd == 'task':
            # Format: task <name> max <value> avg <value>
            if len(tokens) < 4:
                raise ValueError(f"Line {line_num}: Invalid task format: {line}")
            
            name = tokens[1]
            
            if name in task_to_index:
                raise ValueError(f"Line {line_num}: Duplicate task name: {name}")
            
            max_val = None
            avg_val = None
            
            i = 2
            while i < len(tokens):
                if tokens[i].lower() == 'max' and i + 1 < len(tokens):
                    try:
                        max_val = float(tokens[i + 1])
                    except ValueError:
                        raise ValueError(f"Line {line_num}: Invalid max value: {tokens[i+1]}")
                    i += 2
                elif tokens[i].lower() == 'avg' and i + 1 < len(tokens):
                    try:
                        avg_val = float(tokens[i + 1])
                    except ValueError:
                        raise ValueError(f"Line {line_num}: Invalid avg value: {tokens[i+1]}")
                    i += 2
                else:
                    i += 1
            
            if max_val is None:
                raise ValueError(f"Line {line_num}: Task {name} missing max duration")
            
            # Default avg to max if not provided
            if avg_val is None:
                avg_val = max_val
            
            # Add task
            task_index = len(tasks)
            tasks.append(name)
            task_to_index[name] = task_index
            t_max.append(max_val)
            t_avg.append(avg_val)
        
        elif cmd == 'dep':
            # Format: dep <task_name> <dependent_task_name>
            if len(tokens) != 3:
                raise ValueError(f"Line {line_num}: Invalid dep format: {line}")
            
            task1, task2 = tokens[1], tokens[2]
            dependencies_str.append((task1, task2))  # Store as string pair
        
        elif cmd == 'max_cycle':
            if len(tokens) != 2:
                raise ValueError(f"Line {line_num}: max_cycle requires exactly one value")
            try:
                C_max = float(tokens[1])
            except ValueError:
                raise ValueError(f"Line {line_num}: Invalid max_cycle value: {tokens[1]}")
        
        else:
            raise ValueError(f"Line {line_num}: Unknown command: {cmd}")
    
    # Validate
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
    
    # Convert string dependencies to index tuples
    dependencies_idx = []  # Final dependencies list with indices
    for task1, task2 in dependencies_str:
        if task1 not in task_to_index:
            raise ValueError(f"Task '{task1}' referenced in dependency but not defined")
        if task2 not in task_to_index:
            raise ValueError(f"Task '{task2}' referenced in dependency but not defined")
        
        i = task_to_index[task1]
        j = task_to_index[task2]
        
        # Check for self-dependency
        if i == j:
            raise ValueError(f"Task '{task1}' cannot depend on itself")
        
        dependencies_idx.append((i, j))
    
    return tasks, t_max, t_avg, C_max, dependencies_idx


def balance_line(t_max, dependencies=None, C_max=60, t_avg=None, tasks=None):
    """
    Assembly line balancing with dual time analysis.
    
    Parameters:
    -----------
    t_max : list[float]
        Maximum/worst-case durations for n tasks
    dependencies : list[tuple] or None
        Precedence constraints as pairs (i,j) where i must precede j
        i and j are task indices (0-based)
    C_max : float
        Maximum allowed cycle time per station
    t_avg : list[float] or None
        Average/expected durations (same length as t_max)
    tasks : list[str] or None
        Task names for reporting
    
    Returns:
    --------
    dict with solution metrics
    """
    n = len(t_max)  # number of tasks
    
    # Default values
    if t_avg is None:
        t_avg = t_max.copy()
    
    if tasks is None:
        tasks = [f"Task_{i}" for i in range(n)]
    
    # Validate inputs
    if len(t_max) != len(t_avg):
        raise ValueError("t_max and t_avg must have same length")
    
    if C_max <= 0:
        raise ValueError("C_max must be positive")
    
    for i, tm in enumerate(t_max):
        if tm > C_max:
            raise ValueError(f"Task {i} max duration ({tm}) exceeds C_max ({C_max})")
    
    # Validate dependencies parameter
    edges = []
    if dependencies is not None:
        if isinstance(dependencies, list):
            if all(isinstance(edge, tuple) and len(edge) == 2 for edge in dependencies):
                edges = list(dependencies)
            else:
                raise ValueError("Dependencies must be a list of tuples (i, j)")
        else:
            raise ValueError("Dependencies must be a list of tuples or None")
    else:
        edges = []
    
    # Build MILP model
    model = gp.Model("AssemblyLineBalance")
    model.setParam("OutputFlag", 0)
    
    # Maximum possible stations = number of tasks (worst case)
    max_stations = n
    
    # Decision variables
    # x[i][k] = 1 if task i is assigned to station k
    x = {}
    for i in range(n):
        for k in range(max_stations):
            x[(i, k)] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{k}")
    
    # y[k] = 1 if station k is used
    y = {}
    for k in range(max_stations):
        y[k] = model.addVar(vtype=GRB.BINARY, name=f"y_{k}")
    
    # Constraint 1: Each task assigned to exactly one station
    for i in range(n):
        model.addConstr(
            gp.quicksum(x[(i, k)] for k in range(max_stations)) == 1,
            name=f"assign_{i}"
        )
    
    # Constraint 2: Station load <= C_max (using max durations)
    for k in range(max_stations):
        load_expr = gp.quicksum(t_max[i] * x[(i, k)] for i in range(n))
        model.addConstr(load_expr <= C_max * y[k], name=f"capacity_{k}")
    
    # Constraint 3: Precedence constraints
    # If (i, j) in edges, then station(i) <= station(j)
    for (i, j) in edges:
        if i < n and j < n:  # Validate indices
            left = gp.quicksum(k * x[(i, k)] for k in range(max_stations))
            right = gp.quicksum(k * x[(j, k)] for k in range(max_stations))
            model.addConstr(left <= right, name=f"prec_{i}_{j}")
    
    # Constraint 4: Station ordering (symmetry breaking)
    # y[k] >= y[k+1] ensures stations used consecutively from 0
    for k in range(max_stations - 1):
        model.addConstr(y[k] >= y[k + 1], name=f"order_{k}")
    
    # Constraint 5: Task can only be assigned to used station
    for i in range(n):
        for k in range(max_stations):
            model.addConstr(x[(i, k)] <= y[k], name=f"active_{i}_{k}")
    
    # Objective: minimize number of stations
    model.setObjective(gp.quicksum(y[k] for k in range(max_stations)), GRB.MINIMIZE)
    
    # Solve
    model.optimize()
    
    if model.status != GRB.OPTIMAL:
        # Calculate theoretical minimum for reporting
        total_time_max = sum(t_max)
        total_time_avg = sum(t_avg)
        theoretical_min = math.ceil(total_time_max / C_max)
        
        return {
            'optimal': False,
            'error': f"Solver status: {model.status}",
            'stations_used': 0,
            'theoretical_min_stations': theoretical_min,
            'total_time_max': total_time_max,
            'total_time_avg': total_time_avg,
            'C_max': C_max
        }
    
    # Extract solution
    assignment_by_station = []  # list of lists: station -> [task_indices]
    station_used_flags = []
    
    for k in range(max_stations):
        if y[k].X > 0.5:  # Station is used
            tasks_in_station = []
            for i in range(n):
                if x[(i, k)].X > 0.5:
                    tasks_in_station.append(i)
            if tasks_in_station:
                assignment_by_station.append(tasks_in_station)
                station_used_flags.append(True)
        else:
            station_used_flags.append(False)
    
    stations_used = len(assignment_by_station)
    
    # Calculate metrics
    cycle_times_max = []  # Actual cycle time at each station (using max durations)
    cycle_times_avg = []  # Actual cycle time at each station (using avg durations)
    station_efficiencies_max = []  # workload_max / C_max
    station_efficiencies_avg = []  # workload_avg / C_max
    
    total_time_max = sum(t_max)
    total_time_avg = sum(t_avg)
    
    for station_tasks in assignment_by_station:
        load_max = sum(t_max[i] for i in station_tasks)
        load_avg = sum(t_avg[i] for i in station_tasks)
        
        cycle_times_max.append(load_max)
        cycle_times_avg.append(load_avg)
        
        station_efficiencies_max.append(load_max / C_max * 100)  # Convert to percentage
        station_efficiencies_avg.append(load_avg / C_max * 100)  # Convert to percentage
    
    # Overall metrics
    actual_max_cycle = max(cycle_times_max) if cycle_times_max else 0
    actual_avg_cycle = max(cycle_times_avg) if cycle_times_avg else 0
    
    efficiency_max = (total_time_max / (stations_used * C_max)) * 100  # Convert to percentage
    efficiency_avg = (total_time_avg / (stations_used * C_max)) * 100  # Convert to percentage
    balance_delay = 100 - efficiency_max
    
    # Theoretical minimum stations
    theoretical_min = math.ceil(total_time_max / C_max)
    is_optimal = (stations_used == theoretical_min)
    
    return {
        'assignment': assignment_by_station,  # Changed from assignment_details
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
