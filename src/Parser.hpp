#pragma once

#include <string>
#include <string_view>
#include <optional>
#include <vector>

enum class EventType {
    BATTERY,
    NETWORK,
    MEMORY,
    CRASH,
    THERMAL,
    CPU,
    STORAGE
};

enum class Severity {
    INFO,
    WARNING,
    ERROR,
    CRITICAL
};

struct LogEntry {
    std::string timestamp;
    std::string device_id;
    EventType event_type;
    Severity severity;
    std::string message;
};

struct ParsingResult {
    std::vector<LogEntry> valid_entries;
    size_t malformed_count = 0;
    size_t total_lines = 0;
};

std::string_view to_string(EventType type);
std::string_view to_string(Severity severity);
std::optional<EventType> parse_event_type(std::string_view str);
std::optional<Severity> parse_severity(std::string_view str);

class Parser {
public:
    // Parse a single line. Never throws, returns std::nullopt if malformed.
    static std::optional<LogEntry> parse_line(std::string_view line);

    // Stream a file line by line. Throws std::runtime_error if file cannot be opened.
    static ParsingResult parse_file(std::string_view filepath);
};
