# Device Diagnostic Log Parser

A high-performance, modular, and production-quality C++17 command-line interface (CLI) tool designed to ingest, validate, aggregate, and persist structured diagnostic log entries. It streams massive logs line-by-line using stack-allocated stream buffers to ensure constant memory complexity \(O(1)\), enforces strict RAII resource management, serializes aggregated metrics as JSON text, and records summaries directly into a SQLite3 database.

## Architecture Overview

```
                      ┌─────────────────────────┐
                      │    Log File (.txt)      │
                      └────────────┬────────────┘
                                   │ Line-by-line Stream
                                   ▼
                      ┌─────────────────────────┐
                      │     Parser Component    │
                      │  (Parser.hpp/.cpp)      │
                      └────────────┬────────────┘
                                   │
                                   │ Vector of LogEntry
                                   ▼
                      ┌─────────────────────────┐
                      │  Aggregation Component  │
                      │ (Aggregator.hpp/.cpp)   │
                      └────────────┬────────────┘
                                   │
                                   │ AggregationResult
                                   ▼
                      ┌─────────────────────────┐
                      │  Persistence Component  │
                      │  (Database.hpp/.cpp)    │
                      └────────────┬────────────┘
                                   │
                                   │ JSON Serialized String
                                   ▼
                      ┌─────────────────────────┐
                      │    SQLite Database      │
                      │    (diagnostics.db)     │
                      └─────────────────────────┘
```

### Components and Responsibilities
- **Parser**: Streams file data line-by-line using C++17 `std::string_view` for zero-allocation token validation. It maps lines into a list of structured `LogEntry` values, tracking malformed entries without raising exceptions.
- **Aggregator**: Processes the clean memory elements, counting log occurrences per event type (7 types) and severity (4 levels) while recording processing times down to microseconds.
- **Database**: Standard SQLite3 wrapper that isolates all SQLite API calls. It creates tables and inserts summaries using RAII (clean resource lifecycle management in constructor/destructor) and stores event-type and severity maps as JSON strings.
- **CLI (Main)**: Serves as the entry point, handles runtime errors gracefully, updates database persistence status, and renders the final report.

---

## System Prerequisites

To build and run this project, you need the following system packages:
- **C++ Compiler**: Support for C++17 (e.g., GCC 7+, Clang 5+, or MSVC 2017+)
- **CMake**: version 3.14 or later
- **Python 3**: For generating mock log datasets
- **SQLite3 Development Libraries**:
  - *Ubuntu/Debian*: `sudo apt-get install libsqlite3-dev`
  - *macOS*: `brew install sqlite`
  - *Windows (MSYS2)*: `pacman -S mingw-w64-x86_64-sqlite3`
  - *(Optional)*: If SQLite3 is not found in the system path, the build system's CMake script will automatically download the SQLite3 amalgamation and compile it statically as part of the build.

---

## How to Build

Configure and compile the project using standard CMake commands:

```bash
# Create a build directory
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release

# Build all targets (executable and tests)
cmake --build build
```

---

## How to Generate Test Data

Use the provided Python script to generate a synthetic log file containing exactly 50,000 log entries (49,500 valid entries with standard distributions and exactly 500 randomly injected malformed lines):

```bash
python scripts/generator.py
```

---

## How to Run the Parser

Execute the compiled CLI parser by providing the path to the log file as an argument:

```bash
# On Linux/macOS
./build/device_parser generated_logs.txt

# On Windows
.\build\device_parser.exe generated_logs.txt
```

---

## How to Run Tests

Execute unit tests to verify the correctness of the parser and aggregator:

```bash
# Using CTest
ctest --test-dir build --output-on-failure

# Running the test binary directly
./build/tests/run_tests
```

---

## How to Run Valgrind

Run memory validation against the binary with a full leak check:

```bash
valgrind --leak-check=full --show-leak-kinds=all ./build/device_parser generated_logs.txt
```

---

## Results and Outputs

### Successful Run Output
```text
=== DEVICE DIAGNOSTIC LOG PARSER ===
Input file:  generated_logs.txt
─────────────────────────────────────
Parsing Results:
  Total lines read:     50000
  Valid entries:        49500
  Malformed/skipped:    500

Aggregation Results:
  Processing time:      29.07 ms

  By Event Type:
    BATTERY:    7094
    NETWORK:    7102
    MEMORY:     6987
    CRASH:      7139
    THERMAL:    7039
    CPU:        7091
    STORAGE:    7048

  By Severity:
    INFO:       19800
    WARNING:    14850
    ERROR:      9900
    CRITICAL:   4950

Persistence:
  Status:       SUCCESS
=====================================
```

### Valgrind Memory Safety Output
```text
==4284== Memcheck, a memory error detector
==4284== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==4284== Using Valgrind-3.18.1 and LibVEX; rerun with -h for copyright info
==4284== Command: ./build-linux/device_parser generated_logs.txt
==4284== 
...
==4284== 
==4284== HEAP SUMMARY:
==4284==     in use at exit: 0 bytes in 0 blocks
==4284==   total heap usage: 298,499 allocs, 298,499 frees, 29,115,562 bytes allocated
==4284== 
==4284== All heap blocks were freed -- no leaks are possible
==4284== 
==4284== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)
```
