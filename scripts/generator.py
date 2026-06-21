import os
import random
from datetime import datetime, timedelta

def main():
    total_lines = 50000
    malformed_count = 500
    valid_count = total_lines - malformed_count # 49,500

    # Severity distribution (exactly 40% INFO, 30% WARNING, 20% ERROR, 10% CRITICAL)
    severities = (
        ["INFO"] * int(valid_count * 0.40) +
        ["WARNING"] * int(valid_count * 0.30) +
        ["ERROR"] * int(valid_count * 0.20) +
        ["CRITICAL"] * int(valid_count * 0.10)
    )
    random.shuffle(severities)

    event_types = ["BATTERY", "NETWORK", "MEMORY", "CRASH", "THERMAL", "CPU", "STORAGE"]
    
    # Randomly select 500 indices for malformed lines
    malformed_indices = set(random.sample(range(total_lines), malformed_count))

    base_time = datetime(2024, 1, 15, 0, 0, 0)
    all_lines = []
    
    severity_idx = 0
    malformed_types = ["wrong_delimiter", "missing_fields", "empty_line"]
    
    for i in range(total_lines):
        current_time = base_time + timedelta(seconds=i)
        timestamp_str = current_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        if i in malformed_indices:
            # Inject malformed line
            m_type = random.choice(malformed_types)
            if m_type == "wrong_delimiter":
                device_id = f"device_{random.randint(1, 100):04d}"
                event_type = random.choice(event_types)
                severity = random.choice(["INFO", "WARNING", "ERROR", "CRITICAL"])
                message = "Malformed line with wrong delimiter."
                all_lines.append(f"{timestamp_str},{device_id},{event_type},{severity},{message}\n")
            elif m_type == "missing_fields":
                device_id = f"device_{random.randint(1, 100):04d}"
                all_lines.append(f"{timestamp_str}|{device_id}|||Malformed line with missing fields.\n")
            else: # empty_line
                all_lines.append("\n")
        else:
            # Inject valid line
            device_id = f"device_{random.randint(1, 100):04d}"
            event_type = random.choice(event_types)
            severity = severities[severity_idx]
            severity_idx += 1
            message = f"Device diagnostic event: {event_type.lower()} state checked."
            all_lines.append(f"{timestamp_str}|{device_id}|{event_type}|{severity}|{message}\n")

    # Write to file
    filename = "generated_logs.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(all_lines)

    # Get file size in MB
    file_size_mb = os.path.getsize(filename) / (1024 * 1024)

    # Print output exactly as specified
    print("=== LOG FILE GENERATED ===")
    print(f"Total lines written:       {len(all_lines)}")
    print(f"Valid lines:               {valid_count}")
    print(f"Malformed lines injected:  {malformed_count}")
    print(f"File size:                 {file_size_mb:.2f} MB")
    print("==========================")

if __name__ == "__main__":
    main()
