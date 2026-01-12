"""
Performance benchmarking script.
"""
import time
import statistics
from typing import Callable, List
from database_manager import DatabaseManager
from config import get_connection_string


class PerformanceTester:
    """Performance testing for database operations."""
    
    def __init__(self, conn_string: str):
        self.conn_string = conn_string
        self.results = {}
    
    def benchmark(self, operation: Callable, name: str, iterations: int = 100):
        """
        Run a benchmark test.
        
        Args:
            operation: Function to benchmark
            name: Name of the benchmark
            iterations: Number of iterations
            
        Returns:
            Dictionary with benchmark results
        """
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            operation()
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to milliseconds
        
        result = {
            'name': name,
            'iterations': iterations,
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'min': min(times),
            'max': max(times),
            'p95': sorted(times)[int(len(times) * 0.95)]
        }
        
        self.results[name] = result
        return result
    
    def run_all_benchmarks(self):
        """Run comprehensive benchmark suite."""
        print("=" * 80)
        print("PERFORMANCE BENCHMARKS")
        print("=" * 80)
        
        with DatabaseManager(self.conn_string) as db:
            # Test 1: Single customer lookup
            print("\n1. Single Customer Lookup...")
            self.benchmark(
                lambda: db.get_customer_complete(1),
                "Single Customer Lookup",
                iterations=1000
            )
            
            # Test 2: All customers
            print("2. Retrieve All Customers...")
            self.benchmark(
                lambda: db.get_all_customers(),
                "Retrieve All Customers",
                iterations=100
            )
            
            # Test 3: Department statistics
            print("3. Department Statistics...")
            self.benchmark(
                lambda: db.get_department_statistics(),
                "Department Statistics",
                iterations=500
            )
            
            # Test 4: Union operation
            print("4. Union Operation...")
            self.benchmark(
                lambda: db.demonstrate_union(),
                "Union Operation",
                iterations=500
            )
            
            # Test 5: Intersection
            print("5. Intersection Operation...")
            self.benchmark(
                lambda: db.demonstrate_intersection(),
                "Intersection Operation",
                iterations=500
            )
        
        self.print_results()
    
    def print_results(self):
        """Print formatted benchmark results."""
        print("\n" + "=" * 80)
        print("BENCHMARK RESULTS")
        print("=" * 80)
        
        for name, result in self.results.items():
            print(f"\n{name}:")
            print(f"  Iterations:  {result['iterations']}")
            print(f"  Mean:        {result['mean']:.3f} ms")
            print(f"  Median:      {result['median']:.3f} ms")
            print(f"  Std Dev:     {result['stdev']:.3f} ms")
            print(f"  Min:         {result['min']:.3f} ms")
            print(f"  Max:         {result['max']:.3f} ms")
            print(f"  95th %ile:   {result['p95']:.3f} ms")


def main():
    """Run performance benchmarks."""
    conn_string = get_connection_string()
    tester = PerformanceTester(conn_string)
    tester.run_all_benchmarks()


if __name__ == "__main__":
    main()
