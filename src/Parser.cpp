#include "Parser.hpp"
#include <fstream>
#include <sstream>
#include <stdexcept>

std::string_view to_string(EventType type) {
    switch (type) {
        case EventType::BATTERY: return "BATTERY";
        case EventType::NETWORK: return "NETWORK";
        case EventType::MEMORY:  return "MEMORY";
        case EventType::CRASH:   return "CRASH";
        case EventType::THERMAL: return "THERMAL";
        case EventType::CPU:     return "CPU";
        case EventType::STORAGE: return "STORAGE";
    }
    return "UNKNOWN";
}

std::string_view to_string(Severity severity) {
    switch (severity) {
        case Severity::INFO:     return "INFO";
        case Severity::WARNING:  return "WARNING";
        case Severity::ERROR:    return "ERROR";
        case Severity::CRITICAL: return "CRITICAL";
    }
    return "UNKNOWN";
}

std::optional<EventType> parse_event_type(std::string_view str) {
    if (str == "BATTERY") return EventType::BATTERY;
    if (str == "NETWORK") return EventType::NETWORK;
    if (str == "MEMORY")  return EventType::MEMORY;
    if (str == "CRASH")   return EventType::CRASH;
    if (str == "THERMAL") return EventType::THERMAL;
    if (str == "CPU")     return EventType::CPU;
    if (str == "STORAGE") return EventType::STORAGE;
    return std::nullopt;
}

std::optional<Severity> parse_severity(std::string_view str) {
    if (str == "INFO")     return Severity::INFO;
    if (str == "WARNING")  return Severity::WARNING;
    if (str == "ERROR")    return Severity::ERROR;
    if (str == "CRITICAL") return Severity::CRITICAL;
    return std::nullopt;
}

namespace {
std::vector<std::string_view> split(std::string_view str, char delimiter) {
    std::vector<std::string_view> tokens;
    size_t start = 0;
    size_t end = str.find(delimiter);
    while (end != std::string_view::npos) {
        tokens.push_back(str.substr(start, end - start));
        start = end + 1;
        end = str.find(delimiter, start);
    }
    tokens.push_back(str.substr(start));
    return tokens;
}
} // namespace

std::optional<LogEntry> Parser::parse_line(std::string_view line) {
    // Strip trailing \r if it exists (for Windows line endings)
    if (!line.empty() && line.back() == '\r') {
        line.remove_suffix(1);
    }

    auto tokens = split(line, '|');
    if (tokens.size() != 5) {
        return std::nullopt;
    }

    // Basic non-empty checks for essential fields
    if (tokens[0].empty() || tokens[1].empty() || tokens[2].empty() || tokens[3].empty()) {
        return std::nullopt;
    }

    auto event_type = parse_event_type(tokens[2]);
    if (!event_type) {
        return std::nullopt;
    }

    auto severity = parse_severity(tokens[3]);
    if (!severity) {
        return std::nullopt;
    }

    return LogEntry{
        std::string(tokens[0]),
        std::string(tokens[1]),
        *event_type,
        *severity,
        std::string(tokens[4])
    };
}

ParsingResult Parser::parse_file(std::string_view filepath) {
    std::ifstream file((std::string(filepath)));
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file: " + std::string(filepath));
    }

    ParsingResult result;
    std::string line;
    while (std::getline(file, line)) {
        result.total_lines++;
        auto entry = parse_line(line);
        if (entry) {
            result.valid_entries.push_back(std::move(*entry));
        } else {
            result.malformed_count++;
        }
    }

    return result;
}
