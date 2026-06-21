"""
This is a realistic sample backend service module designed to test
the Automated Code Review Assistant's static analysis capabilities.
"""
# Issue 1: Unused imports (2 unused imports: sys, os)
import sys
import os
import json  # Used import

# Issue 3: Function without docstring (1st)
# Issue 6: Function without type hints (1st parameter 'config' has no annotation)
def configure_service(config):
    # Issue 4: Hardcoded secret-like variable (contains 'api' and 'key')
    API_KEY = "sk-proj-1234567890abcdef"
    print(f"Service configured with config: {config}")
    return {"status": "configured", "key": API_KEY}


# Issue 3: Function without docstring (2nd)
# Issue 6: Function without type hints (2nd parameter 'payload' has no annotation)
def handle_request(req_id: str, payload) -> bool:
    try:
        data = json.loads(payload)
        print(f"Request {req_id} loaded successfully: {data}")
        return True
    # Issue 5: Bare except clause
    except:
        print("Failed to load payload")
        return False


# Issue 2: Function over 20 lines (long function)
def perform_data_pipeline(source: str, destination: str) -> None:
    """Runs a long simulation of a database ingestion pipeline."""
    # Body starts here:
    print(f"Initializing transfer from {source} to {destination}")
    records = []
    for i in range(10):
        records.append({"id": i, "val": i * 10})
        
    print(f"Generated {len(records)} test records.")
    
    # Adding lines to exceed 20 lines of body:
    processed = 0
    for r in records:
        r["val"] += 5
        processed += 1
        print(f"Processed record {r['id']}")
        
    print(f"Completed processing of {processed} records.")
    result_data = {"status": "success", "count": processed}
    output_str = json.dumps(result_data)
    print(f"Serialized output: {output_str}")
    print("Writing to destination...")
    print("Flushing buffers...")
    print("Closing connection...")
    print("Pipeline run completed successfully.")
