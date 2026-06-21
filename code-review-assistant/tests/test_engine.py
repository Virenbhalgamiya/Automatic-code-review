from src.engine.analyzer import analyze_code

def test_unused_import() -> None:
    code = """
import math
import os
print(math.pi)
"""
    issues = analyze_code(code)
    unused_imports = [i for i in issues if i.issue_type == "unused_import"]
    assert len(unused_imports) == 1
    assert unused_imports[0].line_number == 3
    assert "os" in unused_imports[0].description
    assert unused_imports[0].severity == "low"

def test_long_function() -> None:
    code = """
def my_long_func() -> None:
    \"\"\"This is a docstring.\"\"\"
    print(1)
    print(2)
    print(3)
    print(4)
    print(5)
    print(6)
    print(7)
    print(8)
    print(9)
    print(10)
    print(11)
    print(12)
    print(13)
    print(14)
    print(15)
    print(16)
    print(17)
    print(18)
    print(19)
    print(20)
    print(21)
"""
    issues = analyze_code(code)
    long_funcs = [i for i in issues if i.issue_type == "long_function"]
    assert len(long_funcs) == 1
    assert long_funcs[0].line_number == 2
    assert "exceeds 20 lines" in long_funcs[0].description
    assert long_funcs[0].severity == "medium"

def test_missing_docstring() -> None:
    code = """
def undocumented_function(x: int) -> int:
    return x * 2
"""
    issues = analyze_code(code)
    missing_docs = [i for i in issues if i.issue_type == "missing_docstring"]
    assert len(missing_docs) == 1
    assert missing_docs[0].line_number == 2
    assert "undocumented_function" in missing_docs[0].description
    assert missing_docs[0].severity == "low"

def test_hardcoded_secret() -> None:
    code = """
SECRET_PASSWORD = "my-secure-password-123"
"""
    issues = analyze_code(code)
    secrets = [i for i in issues if i.issue_type == "hardcoded_secret"]
    assert len(secrets) == 1
    assert secrets[0].line_number == 2
    assert "SECRET_PASSWORD" in secrets[0].description
    assert secrets[0].severity == "high"

def test_bare_except() -> None:
    code = """
try:
    val = int("not-a-number")
except:
    val = 0
"""
    issues = analyze_code(code)
    bare_excepts = [i for i in issues if i.issue_type == "bare_except"]
    assert len(bare_excepts) == 1
    assert bare_excepts[0].line_number == 4
    assert "Bare except" in bare_excepts[0].description
    assert bare_excepts[0].severity == "high"

def test_missing_type_hint() -> None:
    code = """
def add_numbers(a: int, b) -> int:
    \"\"\"Adds two numbers.\"\"\"
    return a + b
"""
    issues = analyze_code(code)
    missing_hints = [i for i in issues if i.issue_type == "missing_type_hint"]
    assert len(missing_hints) == 1
    assert missing_hints[0].line_number == 2
    assert "b" in missing_hints[0].description
    assert missing_hints[0].severity == "low"
