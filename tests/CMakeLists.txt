include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

add_executable(run_tests
    parser_tests.cpp
    aggregator_tests.cpp
)
target_link_libraries(run_tests PRIVATE
    diagnostic_lib
    gtest_main
)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(run_tests PRIVATE -Wall -Wextra -Werror -pedantic)
elseif(MSVC)
    target_compile_options(run_tests PRIVATE /W4 /WX)
endif()

add_test(NAME device_tests COMMAND run_tests)
