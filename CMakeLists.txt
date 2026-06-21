cmake_minimum_required(VERSION 3.14)
project(DeviceDiagnosticLogParser C CXX)

# Enforce C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Define target Windows version for API features on Windows/MinGW
if(WIN32)
    add_compile_definitions(_WIN32_WINNT=0x0600)
endif()

# Check SQLite3
find_package(SQLite3 QUIET)
if(SQLite3_FOUND)
    message(STATUS "Found system SQLite3: ${SQLite3_LIBRARIES}")
    add_library(sqlite3_lib INTERFACE)
    target_link_libraries(sqlite3_lib INTERFACE SQLite::SQLite3)
else()
    message(STATUS "SQLite3 not found on system. Downloading SQLite3 amalgamation...")
    include(FetchContent)
    FetchContent_Declare(
        sqlite3_amalgamation
        URL https://www.sqlite.org/2026/sqlite-amalgamation-3530200.zip
    )
    FetchContent_MakeAvailable(sqlite3_amalgamation)
    
    add_library(sqlite3_lib STATIC
        ${sqlite3_amalgamation_SOURCE_DIR}/sqlite3.c
    )
    target_include_directories(sqlite3_lib SYSTEM PUBLIC ${sqlite3_amalgamation_SOURCE_DIR})
    
    # SQLite3 needs threads
    find_package(Threads REQUIRED)
    target_link_libraries(sqlite3_lib PRIVATE Threads::Threads)
    
    # Disable warnings for the SQLite3 amalgamation source code
    if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
        target_compile_options(sqlite3_lib PRIVATE -w)
    elseif(MSVC)
        target_compile_options(sqlite3_lib PRIVATE /w)
    endif()
endif()

# We will organize components into a library 'diagnostic_lib'
add_library(diagnostic_lib STATIC
    src/Parser.hpp
    src/Parser.cpp
    src/Aggregator.hpp
    src/Aggregator.cpp
    src/Database.hpp
    src/Database.cpp
)

target_include_directories(diagnostic_lib PUBLIC src)
target_link_libraries(diagnostic_lib PRIVATE sqlite3_lib)

# Set compile options for our library
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(diagnostic_lib PRIVATE -Wall -Wextra -Werror -pedantic)
elseif(MSVC)
    target_compile_options(diagnostic_lib PRIVATE /W4 /WX)
endif()

# Main Executable
add_executable(device_parser src/main.cpp)
target_link_libraries(device_parser PRIVATE diagnostic_lib)
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(device_parser PRIVATE -Wall -Wextra -Werror -pedantic)
elseif(MSVC)
    target_compile_options(device_parser PRIVATE /W4 /WX)
endif()

# Testing
option(BUILD_TESTING "Build tests" ON)
if(BUILD_TESTING)
    enable_testing()
    add_subdirectory(tests)
endif()
