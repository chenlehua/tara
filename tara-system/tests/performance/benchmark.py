#!/usr/bin/env python3
"""Performance benchmark script for TARA System."""
import asyncio
import time
import statistics
from typing import List, Callable, Any
import httpx
import argparse


async def measure_latency(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    iterations: int = 100,
    **kwargs,
) -> dict:
    """Measure API latency."""
    latencies = []
    errors = 0
    
    for _ in range(iterations):
        start = time.perf_counter()
        try:
            response = await getattr(client, method)(url, **kwargs)
            if response.status_code >= 400:
                errors += 1
        except Exception:
            errors += 1
        end = time.perf_counter()
        latencies.append((end - start) * 1000)  # Convert to ms
    
    return {
        "min": min(latencies),
        "max": max(latencies),
        "mean": statistics.mean(latencies),
        "median": statistics.median(latencies),
        "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0,
        "p95": sorted(latencies)[int(len(latencies) * 0.95)],
        "p99": sorted(latencies)[int(len(latencies) * 0.99)],
        "errors": errors,
        "iterations": iterations,
    }


async def run_benchmarks(base_url: str, iterations: int):
    """Run all benchmarks."""
    results = {}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"Running benchmarks against {base_url} ({iterations} iterations each)")
        print("-" * 60)
        
        # Project Service Benchmarks
        print("\n📦 Project Service Benchmarks:")
        
        # Health check
        result = await measure_latency(client, "get", f"{base_url}:8001/health", iterations)
        results["project_health"] = result
        print(f"  Health Check: mean={result['mean']:.2f}ms, p95={result['p95']:.2f}ms")
        
        # List projects
        result = await measure_latency(
            client, "get", f"{base_url}:8001/api/v1/projects", iterations
        )
        results["project_list"] = result
        print(f"  List Projects: mean={result['mean']:.2f}ms, p95={result['p95']:.2f}ms")
        
        # Create project
        result = await measure_latency(
            client, "post", f"{base_url}:8001/api/v1/projects",
            iterations=min(iterations, 50),  # Limit creates
            json={"name": "Benchmark Project", "vehicle_type": "BEV"},
        )
        results["project_create"] = result
        print(f"  Create Project: mean={result['mean']:.2f}ms, p95={result['p95']:.2f}ms")
        
        # Asset Service Benchmarks
        print("\n🔧 Asset Service Benchmarks:")
        
        result = await measure_latency(client, "get", f"{base_url}:8003/health", iterations)
        results["asset_health"] = result
        print(f"  Health Check: mean={result['mean']:.2f}ms, p95={result['p95']:.2f}ms")
        
        result = await measure_latency(
            client, "get", f"{base_url}:8003/api/v1/assets?project_id=1", iterations
        )
        results["asset_list"] = result
        print(f"  List Assets: mean={result['mean']:.2f}ms, p95={result['p95']:.2f}ms")
        
        # Threat Service Benchmarks
        print("\n⚠️  Threat Service Benchmarks:")
        
        result = await measure_latency(client, "get", f"{base_url}:8004/health", iterations)
        results["threat_health"] = result
        print(f"  Health Check: mean={result['mean']:.2f}ms, p95={result['p95']:.2f}ms")
        
        result = await measure_latency(
            client, "get", f"{base_url}:8004/api/v1/threats?project_id=1", iterations
        )
        results["threat_list"] = result
        print(f"  List Threats: mean={result['mean']:.2f}ms, p95={result['p95']:.2f}ms")
        
        result = await measure_latency(
            client, "get", f"{base_url}:8004/api/v1/risks/matrix?project_id=1", iterations
        )
        results["risk_matrix"] = result
        print(f"  Risk Matrix: mean={result['mean']:.2f}ms, p95={result['p95']:.2f}ms")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        
        all_means = [r["mean"] for r in results.values()]
        all_p95s = [r["p95"] for r in results.values()]
        total_errors = sum(r["errors"] for r in results.values())
        
        print(f"  Overall Mean Latency: {statistics.mean(all_means):.2f}ms")
        print(f"  Overall P95 Latency: {statistics.mean(all_p95s):.2f}ms")
        print(f"  Total Errors: {total_errors}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="TARA System Performance Benchmark")
    parser.add_argument(
        "--url",
        default="http://localhost",
        help="Base URL for services",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of iterations per benchmark",
    )
    args = parser.parse_args()
    
    asyncio.run(run_benchmarks(args.url, args.iterations))


if __name__ == "__main__":
    main()
