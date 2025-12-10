# Problem Modeling: Exam Scheduling → Graph Coloring → MIP

## Stage 1: Exam Data → Graph Coloring Problem

### Input: Exam Data
```
Exam         Filière  Teacher
─────────────────────────────
WEB          GL2      Mr. Aymen
Recherche Op GL3      Mrs. Imen
UNIX         GL2      Mr. Jemai
WEB(advanced) GL3     Mr. Aymen
SE           GL2      Mrs. Imen
```

### Conflict Generation Rule
Two exams conflict if they share:
- **Same filière** (department) OR
- **Same teacher**

### Graph Construction
**Vertices:** 5 exams (indexed 0-4)
**Edges:** Pairs with conflicts

```
Conflict Table:
─────────────────────────────────────────
Exam 0 (WEB, GL2, Mr.Aymen)
  • Conflicts with 1? NO  (different filière, different teacher)
  • Conflicts with 2? YES (same filière GL2)
  • Conflicts with 3? YES (same teacher Mr. Aymen)
  • Conflicts with 4? YES (same filière GL2)
  
Exam 1 (Recherche Op, GL3, Mrs. Imen)
  • Conflicts with 2? NO  (different filière, different teacher)
  • Conflicts with 3? YES (same filière GL3)
  • Conflicts with 4? YES (same teacher Mrs. Imen)
  
Exam 2 (UNIX, GL2, Mr. Jemai)
  • Conflicts with 3? NO  (different filière, different teacher)
  • Conflicts with 4? YES (same filière GL2)
  
Exam 3 (WEB(advanced), GL3, Mr. Aymen)
  • Conflicts with 4? NO  (different filière, different teacher)
  
Exam 4 (SE, GL2, Mrs. Imen)
  • Done
```

### Resulting Graph
```
       0 ─── 2 ─── 4 ─── 1
       │           │      │
       └─── 3 ─────┴──────┘

Edges: (0,2), (0,3), (0,4), (1,3), (1,4), (2,4)
Total: 6 conflict edges
```

### Graph Coloring Problem
**Goal:** Color vertices with minimum colors such that no adjacent vertices share a color.

---

## Stage 2: Graph Coloring → Integer Linear Program (MIP)

### Decision Variables

#### 1. Assignment Variables
```
x[v,c] ∈ {0,1}

Where:
  v ∈ {0,1,2,3,4}  (vertices/exams)
  c ∈ {0,1,2,...,max_colors-1}  (colors/time slots)
  
x[v,c] = 1  ⟺  vertex v is assigned color c
x[v,c] = 0  ⟺  vertex v is NOT assigned color c
```

Example interpretation:
- `x[0,0] = 1` means "WEB exam gets color 0 (time slot 1)"
- `x[0,1] = 0` means "WEB exam does NOT get color 1 (time slot 2)"

#### 2. Color Usage Variables
```
y[c] ∈ {0,1}

Where:
  c ∈ {0,1,2,...,max_colors-1}  (colors/time slots)
  
y[c] = 1  ⟺  color c is used by at least one vertex
y[c] = 0  ⟺  color c is not used
```

Example:
- `y[0] = 1` means "time slot 1 is used"
- `y[2] = 0` means "time slot 3 is not used"

---

### Constraints

#### Constraint 1: Each Exam Gets Exactly One Time Slot
```
∑(c=0 to max_colors-1) x[v,c] = 1    for each vertex v

Example for exam 0 (WEB):
x[0,0] + x[0,1] + x[0,2] + ... + x[0,k] = 1
```

**Meaning:** WEB must be assigned to exactly one time slot.

---

#### Constraint 2: Conflicting Exams Cannot Share a Time Slot
```
x[u,c] + x[v,c] ≤ 1    for each edge (u,v), for each color c

Example for edge (0,2) conflict at color 0:
x[0,0] + x[2,0] ≤ 1
```

**Meaning:** At most one of the conflicting exams can use time slot 1.

**Why it works:**
- If `x[0,0] = 1` (WEB uses slot 1), then `x[2,0]` must be ≤ 0, so `x[2,0] = 0` (UNIX cannot use slot 1)
- If `x[0,0] = 0` (WEB doesn't use slot 1), then `x[2,0]` can be 0 or 1

**All edges enforced:**
```
(0,2): x[0,c] + x[2,c] ≤ 1  for all c
(0,3): x[0,c] + x[3,c] ≤ 1  for all c
(0,4): x[0,c] + x[4,c] ≤ 1  for all c
(1,3): x[1,c] + x[3,c] ≤ 1  for all c
(1,4): x[1,c] + x[4,c] ≤ 1  for all c
(2,4): x[2,c] + x[4,c] ≤ 1  for all c
```

---

#### Constraint 3: Color Usage Tracking
```
y[c] ≥ x[v,c]    for each color c, for each vertex v

Example for color 0:
y[0] ≥ x[0,0]
y[0] ≥ x[1,0]
y[0] ≥ x[2,0]
y[0] ≥ x[3,0]
y[0] ≥ x[4,0]
```

**Meaning:** Color c is marked as "used" (`y[c] = 1`) if ANY vertex uses it.

**How it works:**
- If any `x[v,c] = 1`, then `y[c] ≥ 1`, so `y[c] = 1`
- If all `x[v,c] = 0`, then `y[c]` can be 0 (solver will set to 0 to minimize)

---

### Objective Function

```
Minimize: ∑(c) y[c]

That is: minimize the total number of colors (time slots) used
```

**Why this works:**
- Since `y[c] = 1` only when color c is used
- Minimizing the sum of `y[c]` minimizes the number of colors
- This finds the **chromatic number** (minimum colors needed)

---

## Stage 3: MIP Solution → Schedule

### Solver Output Example
Gurobi solves and returns:
```
x[0,0] = 1, x[0,1] = 0, x[0,2] = 0  →  WEB gets slot 1
x[1,0] = 1, x[1,1] = 0, x[1,2] = 0  →  Recherche Op gets slot 1
x[2,0] = 0, x[2,1] = 1, x[2,2] = 0  →  UNIX gets slot 2
x[3,0] = 0, x[3,1] = 1, x[3,2] = 0  →  WEB(advanced) gets slot 2
x[4,0] = 0, x[4,1] = 0, x[4,2] = 1  →  SE gets slot 3

y[0] = 1, y[1] = 1, y[2] = 1, y[3..] = 0
```

### Verification of Constraints

**Constraint 1 (Each exam one slot):**
- WEB: 1+0+0 = 1 ✓
- UNIX: 0+1+0 = 1 ✓
- All others satisfied ✓

**Constraint 2 (No adjacent same slot):**
- Edge (0,2) at slot 1: x[0,0]=1, x[2,0]=0 → 1+0=1 ≤ 1 ✓
- Edge (0,2) at slot 2: x[0,1]=0, x[2,1]=1 → 0+1=1 ≤ 1 ✓
- Edge (0,4) at slot 3: x[0,2]=0, x[4,2]=1 → 0+1=1 ≤ 1 ✓
- All other edges satisfied ✓

**Constraint 3 (Color tracking):**
- Color 0: max(1,1,0,0,0) = 1, y[0]=1 ✓
- Color 1: max(0,0,1,1,0) = 1, y[1]=1 ✓
- Color 2: max(0,0,0,0,1) = 1, y[2]=1 ✓

**Objective:**
- Sum = 1+1+1 = 3 colors used (minimum possible) ✓

### Final Schedule
```
Time Slot 1: WEB, Recherche Op
Time Slot 2: UNIX, WEB(advanced)
Time Slot 3: SE

Minimum time slots required: 3
```

---

## Summary of Transformations

```
Step 1: Exam Data
  Input: name, filière, teacher attributes
  
  ↓ (Conflict Generation: same filière OR same teacher)
  
Step 2: Graph Coloring Problem
  Vertices: 5 exams
  Edges: 6 conflicts
  Goal: Chromatic number (min colors)
  
  ↓ (Formulation as MIP)
  
Step 3: Integer Linear Program
  Variables: x[v,c] (assignment), y[c] (usage)
  Constraints: 
    - Each vertex one color
    - Adjacent vertices different colors
    - Color tracking
  Objective: Minimize total colors
  
  ↓ (Gurobi Solver)
  
Step 4: Optimal Schedule
  Coloring: vertex → color assignment
  Time slots: 3 (minimum)
  Schedule: Exams grouped by time slot
```

---

## Why MIP is Appropriate

1. **Exact Solution:** Finds guaranteed optimal solution (minimum colors)
2. **Handles Constraints:** Naturally encodes conflict constraints
3. **Scalability:** Works efficiently for typical exam scheduling (30-100 exams)
4. **NP-Complete Alternative:** Graph coloring is NP-complete; MIP finds exact optimum without trying all possibilities
