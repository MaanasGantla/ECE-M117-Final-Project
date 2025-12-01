import argparse
import json
import sys
from .analyzer import run_analysis

def main():
    parser = argparse.ArgumentParser(description="CSP Analyzer")
    parser.add_argument("--url", required=True, help="Target URL to analyze")
    parser.add_argument("--out", required=True, help="Output JSON file for findings")
    
    args = parser.parse_args()
    
    print(f"Analyzing {args.url}...")
    results = run_analysis(args.url)
    
    with open(args.out, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"Analysis complete. Found {len(results.get('findings', []))} issues.")
    print(f"Results saved to {args.out}")

if __name__ == "__main__":
    main()
