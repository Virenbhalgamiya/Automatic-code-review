#pragma once

#include "Aggregator.hpp"
#include <string_view>

struct sqlite3; // Forward declaration to hide SQLite internals

class Database {
private:
    sqlite3* db_ = nullptr;

public:
    explicit Database(std::string_view db_path);
    ~Database();

    // Disable copy semantics to prevent double-free of connection handle
    Database(const Database&) = delete;
    Database& operator=(const Database&) = delete;

    // Enable move semantics
    Database(Database&& other) noexcept;
    Database& operator=(Database&& other) noexcept;

    // Insert aggregation results into the database
    void insert_summary(const AggregationResult& result);
};
