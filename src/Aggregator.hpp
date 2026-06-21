#pragma once

#include "Parser.hpp"
#include <unordered_map>
#include <string>
#include <map>
#include <vector>

struct AggregationResult {
    std::map<EventType, size_t> event_type_counts;
    std::map<Severity, size_t> severity_counts;
    std::unordered_map<std::string, size_t> device_id_counts;
    size_t total_valid = 0;
    size_t total_malformed = 0;
    double processing_time_ms = 0.0;
};

class Aggregator {
public:
    static AggregationResult aggregate(const std::vector<LogEntry>& entries, size_t malformed_count);
};
