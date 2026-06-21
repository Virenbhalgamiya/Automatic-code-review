#include <gtest/gtest.h>
#include "Parser.hpp"
#include <fstream>
#include <cstdio>

TEST(ParserTest, ValidLineParsesCorrectly) {
    auto entry = Parser::parse_line("2024-01-15T00:00:00|device_0001|BATTERY|INFO|Battery level check");
    ASSERT_TRUE(entry.has_value());
    EXPECT_EQ(entry->timestamp, "2024-01-15T00:00:00");
    EXPECT_EQ(entry->device_id, "device_0001");
    EXPECT_EQ(entry->event_type, EventType::BATTERY);
    EXPECT_EQ(entry->severity, Severity::INFO);
    EXPECT_EQ(entry->message, "Battery level check");
}

TEST(ParserTest, MissingFieldReturnsNullopt) {
    // Missing severity
    auto entry1 = Parser::parse_line("2024-01-15T00:00:00|device_0001|BATTERY||Battery level check");
    EXPECT_FALSE(entry1.has_value());

    // Missing event type
    auto entry2 = Parser::parse_line("2024-01-15T00:00:00|device_0001||INFO|Battery level check");
    EXPECT_FALSE(entry2.has_value());

    // Missing pipe completely (wrong delimiter)
    auto entry3 = Parser::parse_line("2024-01-15T00:00:00,device_0001,BATTERY,INFO,Battery level check");
    EXPECT_FALSE(entry3.has_value());
}

TEST(ParserTest, InvalidEventTypeReturnsNullopt) {
    auto entry = Parser::parse_line("2024-01-15T00:00:00|device_0001|INVALID_TYPE|INFO|Message");
    EXPECT_FALSE(entry.has_value());
}

TEST(ParserTest, InvalidSeverityReturnsNullopt) {
    auto entry = Parser::parse_line("2024-01-15T00:00:00|device_0001|BATTERY|INVALID_SEV|Message");
    EXPECT_FALSE(entry.has_value());
}

TEST(ParserTest, EmptyLineReturnsNullopt) {
    auto entry1 = Parser::parse_line("");
    EXPECT_FALSE(entry1.has_value());

    auto entry2 = Parser::parse_line("\n");
    EXPECT_FALSE(entry2.has_value());
}

TEST(ParserTest, SmallMixedFileReturnsCorrectCounts) {
    const std::string temp_filename = "temp_test_logs.txt";
    std::ofstream outfile(temp_filename);
    ASSERT_TRUE(outfile.is_open());

    outfile << "2024-01-15T00:00:00|device_0001|BATTERY|INFO|Valid 1\n";
    outfile << "2024-01-15T00:00:01|device_0002|NETWORK|WARNING|Valid 2\n";
    outfile << "malformed line with wrong delimiter,etc\n";
    outfile << "2024-01-15T00:00:02|device_0001|CPU|ERROR|Valid 3\n";
    outfile << "\n"; // empty line
    outfile << "2024-01-15T00:00:03|device_0003|CRASH|CRITICAL|Valid 4\n";
    outfile.close();

    try {
        auto result = Parser::parse_file(temp_filename);
        EXPECT_EQ(result.total_lines, 6);
        EXPECT_EQ(result.valid_entries.size(), 4);
        EXPECT_EQ(result.malformed_count, 2);

        // Clean up
        std::remove(temp_filename.c_str());
    } catch (...) {
        std::remove(temp_filename.c_str());
        throw;
    }
}
