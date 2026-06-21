#include "Parser.hpp"
#include "Aggregator.hpp"
#include "Database.hpp"
#include <iostream>
#include <exception>
#include <iomanip>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <path_to_log_file>\n";
        return 1;
    }

    std::string log_file_path = argv[1];
    std::string db_path = "diagnostics.db";

    std::cout << "=== DEVICE DIAGNOSTIC LOG PARSER ===\n";
    std::cout << "Input file:  " << log_file_path << "\n";
    std::cout << "─────────────────────────────────────\n";

    ParsingResult parsing_result;
    bool parsing_success = false;
    try {
        parsing_result = Parser::parse_file(log_file_path);
        parsing_success = true;
    } catch (const std::exception& e) {
        std::cerr << "Error reading input file: " << e.what() << "\n";
    }

    if (!parsing_success) {
        std::cout << "Parsing Results:\n";
        std::cout << "  Total lines read:     0\n";
        std::cout << "  Valid entries:        0\n";
        std::cout << "  Malformed/skipped:    0\n\n";
        std::cout << "Aggregation Results:\n";
        std::cout << "  Processing time:      0.00 ms\n\n";
        std::cout << "Persistence:\n";
        std::cout << "  Status:       FAILED\n";
        std::cout << "=====================================\n";
        return 1;
    }

    // Step 2: Aggregate
    AggregationResult agg_result = Aggregator::aggregate(parsing_result.valid_entries, parsing_result.malformed_count);

    // Step 3: Persist
    std::string persistence_status = "FAILED";
    try {
        Database db(db_path);
        db.insert_summary(agg_result);
        persistence_status = "SUCCESS";
    } catch (const std::exception& e) {
        std::cerr << "\nDatabase Persistence Error: " << e.what() << "\n";
    }

    // Step 4: Present results
    std::cout << "Parsing Results:\n";
    std::cout << "  Total lines read:     " << parsing_result.total_lines << "\n";
    std::cout << "  Valid entries:        " << agg_result.total_valid << "\n";
    std::cout << "  Malformed/skipped:    " << agg_result.total_malformed << "\n\n";

    std::cout << "Aggregation Results:\n";
    std::cout << "  Processing time:      " << std::fixed << std::setprecision(2) << agg_result.processing_time_ms << " ms\n\n";

    std::cout << "  By Event Type:\n";
    std::cout << "    BATTERY:    " << agg_result.event_type_counts.at(EventType::BATTERY) << "\n";
    std::cout << "    NETWORK:    " << agg_result.event_type_counts.at(EventType::NETWORK) << "\n";
    std::cout << "    MEMORY:     " << agg_result.event_type_counts.at(EventType::MEMORY) << "\n";
    std::cout << "    CRASH:      " << agg_result.event_type_counts.at(EventType::CRASH) << "\n";
    std::cout << "    THERMAL:    " << agg_result.event_type_counts.at(EventType::THERMAL) << "\n";
    std::cout << "    CPU:        " << agg_result.event_type_counts.at(EventType::CPU) << "\n";
    std::cout << "    STORAGE:    " << agg_result.event_type_counts.at(EventType::STORAGE) << "\n\n";

    std::cout << "  By Severity:\n";
    std::cout << "    INFO:       " << agg_result.severity_counts.at(Severity::INFO) << "\n";
    std::cout << "    WARNING:    " << agg_result.severity_counts.at(Severity::WARNING) << "\n";
    std::cout << "    ERROR:      " << agg_result.severity_counts.at(Severity::ERROR) << "\n";
    std::cout << "    CRITICAL:   " << agg_result.severity_counts.at(Severity::CRITICAL) << "\n\n";

    std::cout << "Persistence:\n";
    std::cout << "  Status:       " << persistence_status << "\n";
    std::cout << "=====================================\n";

    return (persistence_status == "SUCCESS") ? 0 : 1;
}
