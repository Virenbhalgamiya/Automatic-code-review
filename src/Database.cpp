#include "Database.hpp"
#include <sqlite3.h>
#include <stdexcept>
#include <sstream>
#include <iomanip>
#include <chrono>

namespace {
std::string get_current_timestamp() {
    auto now = std::chrono::system_clock::now();
    auto in_time_t = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    struct tm buf;
#if defined(_WIN32) || defined(_WIN64)
    localtime_s(&buf, &in_time_t);
#else
    localtime_r(&in_time_t, &buf);
#endif
    ss << std::put_time(&buf, "%Y-%m-%dT%H:%M:%S");
    return ss.str();
}

std::string to_json(const std::map<EventType, size_t>& counts) {
    std::string json = "{";
    bool first = true;
    for (const auto& [type, count] : counts) {
        if (!first) json += ",";
        json += "\"" + std::string(to_string(type)) + "\":" + std::to_string(count);
        first = false;
    }
    json += "}";
    return json;
}

std::string to_json(const std::map<Severity, size_t>& counts) {
    std::string json = "{";
    bool first = true;
    for (const auto& [sev, count] : counts) {
        if (!first) json += ",";
        json += "\"" + std::string(to_string(sev)) + "\":" + std::to_string(count);
        first = false;
    }
    json += "}";
    return json;
}
} // namespace

Database::Database(std::string_view db_path) {
    int rc = sqlite3_open((std::string(db_path)).c_str(), &db_);
    if (rc != SQLITE_OK) {
        std::string err_msg = db_ ? sqlite3_errmsg(db_) : "Unknown error";
        if (db_) {
            sqlite3_close(db_);
            db_ = nullptr;
        }
        throw std::runtime_error("Failed to open SQLite database: " + err_msg);
    }

    // Create table if it doesn't exist
    char* err_msg = nullptr;
    const char* create_table_sql = 
        "CREATE TABLE IF NOT EXISTS diagnostic_summaries ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "timestamp TEXT NOT NULL,"
        "total_valid INTEGER NOT NULL,"
        "total_malformed INTEGER NOT NULL,"
        "event_type_counts TEXT NOT NULL,"
        "severity_counts TEXT NOT NULL"
        ");";

    rc = sqlite3_exec(db_, create_table_sql, nullptr, nullptr, &err_msg);
    if (rc != SQLITE_OK) {
        std::string exception_msg = "Failed to create table: ";
        if (err_msg) {
            exception_msg += err_msg;
            sqlite3_free(err_msg);
        } else {
            exception_msg += "Unknown error";
        }
        sqlite3_close(db_);
        db_ = nullptr;
        throw std::runtime_error(exception_msg);
    }
}

Database::~Database() {
    if (db_) {
        sqlite3_close(db_);
    }
}

Database::Database(Database&& other) noexcept : db_(other.db_) {
    other.db_ = nullptr;
}

Database& Database::operator=(Database&& other) noexcept {
    if (this != &other) {
        if (db_) {
            sqlite3_close(db_);
        }
        db_ = other.db_;
        other.db_ = nullptr;
    }
    return *this;
}

void Database::insert_summary(const AggregationResult& result) {
    if (!db_) {
        throw std::runtime_error("Database connection is closed");
    }

    const char* insert_sql = 
        "INSERT INTO diagnostic_summaries (timestamp, total_valid, total_malformed, event_type_counts, severity_counts) "
        "VALUES (?, ?, ?, ?, ?);";

    sqlite3_stmt* stmt = nullptr;
    int rc = sqlite3_prepare_v2(db_, insert_sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        throw std::runtime_error("Failed to prepare INSERT statement: " + std::string(sqlite3_errmsg(db_)));
    }

    std::string timestamp = get_current_timestamp();
    std::string event_counts_json = to_json(result.event_type_counts);
    std::string severity_counts_json = to_json(result.severity_counts);

    sqlite3_bind_text(stmt, 1, timestamp.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_int64(stmt, 2, static_cast<sqlite3_int64>(result.total_valid));
    sqlite3_bind_int64(stmt, 3, static_cast<sqlite3_int64>(result.total_malformed));
    sqlite3_bind_text(stmt, 4, event_counts_json.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 5, severity_counts_json.c_str(), -1, SQLITE_TRANSIENT);

    rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        std::string err = sqlite3_errmsg(db_);
        sqlite3_finalize(stmt);
        throw std::runtime_error("Failed to execute INSERT statement: " + err);
    }

    sqlite3_finalize(stmt);
}
