#include <gtest/gtest.h>
#include "Aggregator.hpp"

TEST(AggregatorTest, AggregatesCorrectly) {
    std::vector<LogEntry> entries;
    // Build 10 known entries with specific types and severities
    // 3 BATTERY, 2 NETWORK, 1 MEMORY, 4 CRASH
    // 4 INFO, 3 WARNING, 2 ERROR, 1 CRITICAL
    entries.push_back({"2024-01-15T00:00:00", "device_0001", EventType::BATTERY, Severity::INFO, "Msg"});
    entries.push_back({"2024-01-15T00:00:01", "device_0001", EventType::BATTERY, Severity::INFO, "Msg"});
    entries.push_back({"2024-01-15T00:00:02", "device_0002", EventType::BATTERY, Severity::WARNING, "Msg"});

    entries.push_back({"2024-01-15T00:00:03", "device_0002", EventType::NETWORK, Severity::INFO, "Msg"});
    entries.push_back({"2024-01-15T00:00:04", "device_0003", EventType::NETWORK, Severity::WARNING, "Msg"});

    entries.push_back({"2024-01-15T00:00:05", "device_0001", EventType::MEMORY, Severity::ERROR, "Msg"});

    entries.push_back({"2024-01-15T00:00:06", "device_0004", EventType::CRASH, Severity::INFO, "Msg"});
    entries.push_back({"2024-01-15T00:00:07", "device_0004", EventType::CRASH, Severity::WARNING, "Msg"});
    entries.push_back({"2024-01-15T00:00:08", "device_0004", EventType::CRASH, Severity::ERROR, "Msg"});
    entries.push_back({"2024-01-15T00:00:09", "device_0004", EventType::CRASH, Severity::CRITICAL, "Msg"});

    size_t malformed_count = 5;

    auto result = Aggregator::aggregate(entries, malformed_count);

    // Assert total valid == 10
    EXPECT_EQ(result.total_valid, 10);
    EXPECT_EQ(result.total_malformed, 5);

    // Assert every count matches exactly
    // Event types
    EXPECT_EQ(result.event_type_counts.at(EventType::BATTERY), 3);
    EXPECT_EQ(result.event_type_counts.at(EventType::NETWORK), 2);
    EXPECT_EQ(result.event_type_counts.at(EventType::MEMORY), 1);
    EXPECT_EQ(result.event_type_counts.at(EventType::CRASH), 4);
    EXPECT_EQ(result.event_type_counts.at(EventType::THERMAL), 0);
    EXPECT_EQ(result.event_type_counts.at(EventType::CPU), 0);
    EXPECT_EQ(result.event_type_counts.at(EventType::STORAGE), 0);

    // Severities
    EXPECT_EQ(result.severity_counts.at(Severity::INFO), 4);
    EXPECT_EQ(result.severity_counts.at(Severity::WARNING), 3);
    EXPECT_EQ(result.severity_counts.at(Severity::ERROR), 2);
    EXPECT_EQ(result.severity_counts.at(Severity::CRITICAL), 1);

    // Devices
    EXPECT_EQ(result.device_id_counts.at("device_0001"), 3);
    EXPECT_EQ(result.device_id_counts.at("device_0002"), 2);
    EXPECT_EQ(result.device_id_counts.at("device_0003"), 1);
    EXPECT_EQ(result.device_id_counts.at("device_0004"), 4);

    // Assert processing time > 0
    EXPECT_GT(result.processing_time_ms, 0.0);
}
