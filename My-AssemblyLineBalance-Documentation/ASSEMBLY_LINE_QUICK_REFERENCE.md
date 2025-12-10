# Assembly Line Balancing - Quick Reference

## Input Format

Each task definition on its own line:
```
task <name> max <max_duration> avg <avg_duration>
```

Then specify the maximum cycle time:
```
max_cycle <value>
```

### Complete Example:
```
task paint max 10 avg 7
task hammer max 30 avg 27
task assemble max 50 avg 40
task inspect max 15 avg 12

max_cycle 60
```

### Rules:
- **name**: Unique task identifier (any string, no spaces)
- **max_duration**: Worst-case execution time (must be positive, ≤ C_max)
- **avg_duration**: Expected execution time (must be positive)
- **C_max**: Maximum allowed time per workstation (must be positive)

## Understanding the Output

### Solution Metrics:
- **Stations**: Number of workstations required
- **Theoretical Minimum**: Lower bound (cannot do better with this C_max)
- **Is Optimal**: Whether we achieved the theoretical minimum
- **Max Cycle**: Maximum time on any single workstation

### Efficiency Metrics (%)
- **Efficiency (max)**: Using worst-case times: `(Total Time) / (Stations × C_max) × 100`
- **Efficiency (avg)**: Using expected times: `(Expected Total) / (Stations × C_max) × 100`
- **Balance Delay**: Wasted capacity: `100 - Efficiency(max)`

### Per-Station Metrics:
- **Max Load**: Sum of maximum durations for tasks in station
- **Avg Load**: Sum of average durations for tasks in station
- **Efficiency**: Station load / C_max × 100

### Color-Coded Efficiency:
- 🟢 **Green (≥85%)**: Excellent utilization
- 🟡 **Yellow (70-85%)**: Good utilization  
- 🟠 **Orange (50-70%)**: Moderate utilization
- 🔴 **Red (<50%)**: Poor utilization, needs balancing

## Interpretation Guide

### Why Two Time Estimates?

**Maximum times** (pessimistic):
- Used for **planning** and **resource allocation**
- Guarantees the line will NEVER exceed C_max (worst case)
- Determines minimum stations needed

**Average times** (realistic):
- Shows **expected real-world performance**
- Actual cycle time will typically be lower
- Reveals practical efficiency with same workstations

### Example Analysis:
```
Input: paint(10/7), hammer(30/27), assemble(50/40), inspect(15/12), C_max=60

Solution:
- Station 1: paint(10/7) + assemble(50/40)
  - Max load: 60 (100% efficiency - fully utilized worst case)
  - Avg load: 47 (78% efficiency - still good on average)
  
- Station 2: hammer(30/27) + inspect(15/12)  
  - Max load: 45 (75% efficiency)
  - Avg load: 39 (65% efficiency)

Interpretation:
✓ With worst-case times, we perfectly balance Station 1 at exactly C_max
✓ With expected times, Station 1 still has 13 units of slack (78% utilized)
✓ Overall line uses only 87.5% of worst-case capacity
✓ But realistically operates at 71.7% (more realistic planning scenario)
```

## Key Insights

1. **Optimal Solutions**: When actual stations = theoretical minimum
   - Rare but achievable with balanced task durations
   - Indicates excellent assignment

2. **Suboptimal Solutions**: When actual > theoretical minimum
   - Some idle time exists (balance delay > 0%)
   - Task durations don't divide evenly into available C_max
   - Still the best possible assignment

3. **Comparison Strategy**:
   - If `efficiency_avg` >> `efficiency_max`: Tasks rarely exceed expected time
   - If `efficiency_avg` ≈ `efficiency_max`: High variability in task times
   - Use `balance_delay` to identify "slack" in the line

## Example Scenarios

### Scenario 1: Perfect Balance
- Tasks: A=25, B=25, C=25 (max), avg same
- C_max=30
- Result: 3 stations (theoretical min), 100% efficiency
- Interpretation: Perfect division possible

### Scenario 2: Imbalanced Tasks
- Tasks: A=29, B=1 (max), avg same
- C_max=30  
- Result: 2 stations (theoretical min=2), 96.7% efficiency
- Interpretation: Nearly perfect, some idle time unavoidable

### Scenario 3: High Variability
- Tasks: A=10 max / 5 avg, B=10 max / 5 avg (max), avg both=5
- C_max=15
- Result: 2 stations (theoretical min), varied efficiency
- Interpretation: Planning conservative but operations have slack

## Common Issues & Solutions

**Issue**: "Task exceeds C_max"
- **Cause**: A task duration > maximum allowed per station
- **Fix**: Increase C_max or split the task into subtasks

**Issue**: Efficiency < 50%
- **Cause**: Task durations don't divide well into C_max
- **Fix**: Adjust C_max or review task duration estimates
- **Alternative**: This might be realistic - some processes can't do better

**Issue**: Many stations needed
- **Cause**: Total task time much larger than C_max
- **Fix**: Increase C_max, parallelize fewer tasks, or reduce scope

## Tips for Good Balancing

1. **Choose C_max carefully**
   - Too low → Too many stations, high costs
   - Too high → Few stations but low efficiency
   - Sweet spot: ~ceil(total_time / desired_stations)

2. **Keep task durations similar**
   - Wide variance → Poor balance, wasted capacity
   - Similar durations → Better utilization

3. **Review avg vs max gap**
   - If large gap: High risk/variability
   - If small gap: Predictable performance

## For Developers

### Using the Solver Programmatically:

```python
from non_interfaces.AssemblyLineBalance import balance_line, parse_task_input

# Parse input
input_text = """task A max 10 avg 7
max_cycle 20"""
tasks, t_max, t_avg, C_max = parse_task_input(input_text)

# Solve (optional: pass precedence constraints)
result = balance_line(
    t_max=t_max,
    C_max=C_max,
    t_avg=t_avg,
    tasks=tasks,
    precedence=None  # Can add list of (i,j) tuples
)

# Access results
print(f"Stations: {result['stations_used']}")
print(f"Assignment: {result['assignment']}")
print(f"Efficiency: {result['efficiency_max']:.1f}%")
```

### Result Dictionary Keys:
- `assignment`: List[List[int]] - task indices per station
- `stations_used`: int
- `cycle_times_max`: List[float]
- `cycle_times_avg`: List[float]
- `efficiency_max`: float (%)
- `efficiency_avg`: float (%)
- `station_efficiencies_max`: List[float]
- `station_efficiencies_avg`: List[float]
- `balance_delay`: float (%)
- `theoretical_min_stations`: int
- `is_optimal`: bool
- `actual_max_cycle`: float
- `actual_avg_cycle`: float

---
**Last Updated**: December 2025
**Status**: Production Ready
