import json
import os

print("=== Data Loading Verification ===")
print(f"Current directory: {os.getcwd()}")
print(f"Files in data directory: {os.listdir('data') if os.path.exists('data') else 'No data directory'}")

# Load test data
test_data = []
training_data = []

try:
    # Load TestData.jsonl
    with open('data/TestData.jsonl', 'r', encoding='utf-8') as f:
        test_data = [json.loads(line.strip()) for line in f if line.strip()]
    print(f"✓ Loaded {len(test_data)} test records")
    
    # Load TrainingData.jsonl
    with open('data/TrainingData.jsonl', 'r', encoding='utf-8') as f:
        training_data = [json.loads(line.strip()) for line in f if line.strip()]
    print(f"✓ Loaded {len(training_data)} training records")
    
    # Combine data
    combined_data = test_data + training_data
    print(f"✓ Combined: {len(combined_data)} total records")
    
    # Extract unique values for dropdowns
    environments = sorted(set(r.get('environment', '') for r in combined_data if r.get('environment')))
    modules = sorted(set(r.get('module', '') for r in combined_data if r.get('module')))
    failure_types = sorted(set(r.get('failure_type', '') for r in combined_data if r.get('failure_type')))
    test_ids = sorted(set(r.get('test_id', '') for r in combined_data if r.get('test_id')))
    
    print("\n=== Dropdown Values ===")
    print(f"Environments ({len(environments)}): {environments}")
    print(f"Modules ({len(modules)}): {modules[:10]}{'...' if len(modules) > 10 else ''}")
    print(f"Failure Types ({len(failure_types)}): {failure_types}")
    print(f"Test IDs ({len(test_ids)}): {test_ids[:10]}{'...' if len(test_ids) > 10 else ''}")
    
    # Show sample record
    if combined_data:
        print(f"\n=== Sample Record ===")
        sample = combined_data[0]
        for key, value in sample.items():
            if key != 'logs':  # Skip logs as they're long
                print(f"{key}: {value}")
    
    print("\n✓ Data loading verification successful!")
    
except Exception as e:
    print(f"✗ Error loading data: {e}")
    import traceback
    traceback.print_exc() 