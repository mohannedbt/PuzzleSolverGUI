#!/usr/bin/env python3
"""
Comprehensive Test Suite for Assembly Line Balancing Solver
Tests core solver, GUI integration, and unifiedinterface compatibility
"""

import sys
sys.path.insert(0, '/home/mambaa/Documents/GL3S1/RechercheOp/TP/PuzzleSolverGUI')

def test_core_solver():
    """Test the core solver functionality"""
    print("\n" + "=" * 70)
    print("TEST 1: CORE SOLVER")
    print("=" * 70)
    
    from non_interfaces.AssemblyLineBalance import (
        balance_line, parse_task_input, display_solution
    )
    
    # Test 1a: Parsing
    print("\n1a. Testing input parsing...")
    input_text = """task paint max 10 avg 7
task hammer max 30 avg 27
task assemble max 50 avg 40
task inspect max 15 avg 12

max_cycle 60"""
    
    try:
        tasks, t_max, t_avg, C_max = parse_task_input(input_text)
        assert len(tasks) == 4
        assert sum(t_max) == 105
        print("   ✓ Parsing works correctly")
    except Exception as e:
        print(f"   ✗ Parsing failed: {e}")
        return False
    
    # Test 1b: Solving
    print("1b. Testing solver...")
    try:
        result = balance_line(t_max, precedence=None, C_max=C_max, t_avg=t_avg, tasks=tasks)
        assert result['stations_used'] == 2
        assert result['is_optimal'] == True
        assert abs(result['efficiency_max'] - 87.5) < 0.1
        print("   ✓ Solver works correctly")
        print(f"      - Stations: {result['stations_used']}")
        print(f"      - Optimal: {result['is_optimal']}")
        print(f"      - Efficiency: {result['efficiency_max']:.1f}%")
    except Exception as e:
        print(f"   ✗ Solving failed: {e}")
        return False
    
    # Test 1c: Display
    print("1c. Testing result formatting...")
    try:
        output = display_solution(result, t_max, t_avg)
        assert "ASSEMBLY LINE BALANCING" in output
        assert "Station" in output
        assert "Efficiency" in output
        print("   ✓ Result formatting works")
    except Exception as e:
        print(f"   ✗ Display failed: {e}")
        return False
    
    return True


def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 70)
    print("TEST 2: ERROR HANDLING")
    print("=" * 70)
    
    from non_interfaces.AssemblyLineBalance import parse_task_input
    
    test_cases = [
        ("", "Empty input"),
        ("task A max 5 avg 4", "Missing max_cycle"),
        ("max_cycle 10", "No tasks"),
        ("task A max 100 avg 80\nmax_cycle 60", "Task exceeds C_max"),
        ("task A max 0 avg 4\nmax_cycle 10", "Non-positive max"),
    ]
    
    passed = 0
    for input_text, description in test_cases:
        try:
            parse_task_input(input_text)
            print(f"   ✗ {description}: should have failed")
        except ValueError:
            print(f"   ✓ {description}: correctly rejected")
            passed += 1
    
    return passed == len(test_cases)


def test_gui_integration():
    """Test GUI module imports"""
    print("\n" + "=" * 70)
    print("TEST 3: GUI INTEGRATION")
    print("=" * 70)
    
    try:
        from graphical_interfaces.AssemblyLineBalance import AssemblyLineBalanceSolverGUI
        print("   ✓ GUI module imports successfully")
        
        # Check required methods
        required = ['create_menu_page', 'create_input_page', 'create_result_page', 
                   'create_manual_page', 'solve', 'display_result']
        for method in required:
            if hasattr(AssemblyLineBalanceSolverGUI, method):
                print(f"   ✓ Method {method} exists")
            else:
                print(f"   ✗ Method {method} missing")
                return False
        return True
    except ImportError as e:
        print(f"   ✗ GUI import failed: {e}")
        return False


def test_unified_interface():
    """Test integration with unifiedinterface"""
    print("\n" + "=" * 70)
    print("TEST 4: UNIFIED INTERFACE INTEGRATION")
    print("=" * 70)
    
    try:
        # Check if we can import from unifiedinterface
        import unifiedinterface
        print("   ✓ unifiedinterface module loads")
        
        # Verify AssemblyLineBalance is imported
        from graphical_interfaces.AssemblyLineBalance import AssemblyLineBalanceSolverGUI
        print("   ✓ AssemblyLineBalanceSolverGUI can be imported directly")
        
        return True
    except ImportError as e:
        print(f"   ✗ Integration test failed: {e}")
        return False


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "=" * 70)
    print("TEST 5: EDGE CASES")
    print("=" * 70)
    
    from non_interfaces.AssemblyLineBalance import balance_line, parse_task_input
    
    # Test 5a: Single task
    print("\n5a. Single task...")
    try:
        input_text = "task A max 10 avg 8\nmax_cycle 20"
        tasks, t_max, t_avg, C_max = parse_task_input(input_text)
        result = balance_line(t_max, C_max=C_max, t_avg=t_avg, tasks=tasks)
        assert result['stations_used'] == 1
        print("    ✓ Single task handled correctly")
    except Exception as e:
        print(f"    ✗ Single task failed: {e}")
        return False
    
    # Test 5b: All tasks fit in one station
    print("5b. Multiple tasks, one station...")
    try:
        input_text = "task A max 5 avg 4\ntask B max 5 avg 4\nmax_cycle 15"
        tasks, t_max, t_avg, C_max = parse_task_input(input_text)
        result = balance_line(t_max, C_max=C_max, t_avg=t_avg, tasks=tasks)
        assert result['stations_used'] == 1
        assert len(result['assignment'][0]) == 2
        print("    ✓ Multiple tasks in one station handled correctly")
    except Exception as e:
        print(f"    ✗ Multiple tasks in one station failed: {e}")
        return False
    
    # Test 5c: Each task in separate station
    print("5c. Each task in separate station...")
    try:
        input_text = "task A max 25 avg 20\ntask B max 25 avg 20\nmax_cycle 30"
        tasks, t_max, t_avg, C_max = parse_task_input(input_text)
        result = balance_line(t_max, C_max=C_max, t_avg=t_avg, tasks=tasks)
        assert result['stations_used'] == 2
        print("    ✓ Separate stations handled correctly")
    except Exception as e:
        print(f"    ✗ Separate stations failed: {e}")
        return False
    
    return True


def test_metrics_calculation():
    """Test that metrics are calculated correctly"""
    print("\n" + "=" * 70)
    print("TEST 6: METRICS CALCULATION")
    print("=" * 70)
    
    from non_interfaces.AssemblyLineBalance import balance_line, parse_task_input
    
    input_text = """task A max 3 avg 2.5
task B max 2 avg 1.8
task C max 4 avg 3.2
task D max 2 avg 1.5

max_cycle 5"""
    
    tasks, t_max, t_avg, C_max = parse_task_input(input_text)
    result = balance_line(t_max, C_max=C_max, t_avg=t_avg, tasks=tasks)
    
    # Manual calculations
    total_max = sum(t_max)  # 11
    total_avg = sum(t_avg)  # 9
    stations = result['stations_used']  # Should be 3
    theoretical_min = -(-total_max // C_max)  # ceil(11/5) = 3
    
    print(f"\nMetrics validation:")
    print(f"  Total (max): {total_max}, Total (avg): {total_avg}")
    print(f"  Stations: {stations}, Theoretical min: {theoretical_min}")
    
    # Check calculations
    checks = [
        (result['stations_used'] == theoretical_min, "Optimal solution"),
        (result['theoretical_min_stations'] == theoretical_min, "Theoretical min correct"),
        (len(result['assignment']) == stations, "Assignment count matches"),
        (len(result['cycle_times_max']) == stations, "Max cycle times count"),
        (len(result['cycle_times_avg']) == stations, "Avg cycle times count"),
        (abs(result['efficiency_max'] - (total_max / (stations * C_max) * 100)) < 0.1, "Efficiency max correct"),
        (abs(result['efficiency_avg'] - (total_avg / (stations * C_max) * 100)) < 0.1, "Efficiency avg correct"),
        (abs(result['balance_delay'] - (100 - result['efficiency_max'])) < 0.1, "Balance delay correct"),
    ]
    
    passed = 0
    for check, description in checks:
        if check:
            print(f"  ✓ {description}")
            passed += 1
        else:
            print(f"  ✗ {description}")
    
    return passed == len(checks)


def main():
    """Run all tests"""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "ASSEMBLY LINE BALANCING SOLVER TEST SUITE" + " " * 11 + "║")
    print("╚" + "=" * 68 + "╝")
    
    tests = [
        ("Core Solver", test_core_solver),
        ("Error Handling", test_error_handling),
        ("GUI Integration", test_gui_integration),
        ("Unified Interface", test_unified_interface),
        ("Edge Cases", test_edge_cases),
        ("Metrics Calculation", test_metrics_calculation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ EXCEPTION in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")
    
    print("=" * 70)
    print(f"Result: {passed}/{total} tests passed")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
