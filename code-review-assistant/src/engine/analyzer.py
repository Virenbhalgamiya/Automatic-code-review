import ast
from typing import List, Dict, Set, Tuple
from pydantic import BaseModel, Field

class Issue(BaseModel):
    issue_type: str = Field(..., description="The type of the static analysis issue detected.")
    line_number: int = Field(..., description="The line number where the issue was detected.")
    description: str = Field(..., description="A human-readable description of the issue.")
    severity: str = Field(..., description="The severity level of the issue: low, medium, or high.")

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.issues: List[Issue] = []
        
        # Track imports: name -> (line_number, node)
        self.imported_names: Dict[str, Tuple[int, ast.AST]] = {}
        
        # Track all referenced names
        self.referenced_names: Set[str] = set()

    def analyze(self) -> List[Issue]:
        """Parses and analyzes the Python source code, returning a list of issues."""
        try:
            tree = ast.parse(self.source_code)
        except SyntaxError as e:
            return [
                Issue(
                    issue_type="syntax_error",
                    line_number=e.lineno or 1,
                    description=f"Syntax Error: {e.msg}",
                    severity="high"
                )
            ]
        except Exception as e:
            return [
                Issue(
                    issue_type="parsing_error",
                    line_number=1,
                    description=f"Failed to parse file: {str(e)}",
                    severity="high"
                )
            ]

        # Traverse the AST to extract imports, references, and patterns
        self.visit(tree)
        
        # Post-process unused imports
        for name, (lineno, _) in self.imported_names.items():
            if name not in self.referenced_names:
                self.issues.append(
                    Issue(
                        issue_type="unused_import",
                        line_number=lineno,
                        description=f"Imported name '{name}' is never referenced.",
                        severity="low"
                    )
                )

        # Sort issues primarily by line number, then by issue type
        self.issues.sort(key=lambda x: (x.line_number, x.issue_type))
        return self.issues

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            # Bind the name that is introduced into the local namespace.
            # E.g. 'import os' introduces 'os'; 'import os.path' introduces 'os';
            # 'import os as my_os' introduces 'my_os'.
            name = alias.asname if alias.asname else alias.name.split('.')[0]
            if name != '*':
                self.imported_names[name] = (node.lineno, node)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            # E.g. 'from os import path' introduces 'path';
            # 'from os import path as my_path' introduces 'my_path'.
            name = alias.asname if alias.asname else alias.name
            if name != '*':
                self.imported_names[name] = (node.lineno, node)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.referenced_names.add(node.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function_or_method(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function_or_method(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if ast.get_docstring(node) is None:
            self.issues.append(
                Issue(
                    issue_type="missing_docstring",
                    line_number=node.lineno,
                    description=f"Class '{node.name}' is missing a docstring.",
                    severity="low"
                )
            )
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is None:
            self.issues.append(
                Issue(
                    issue_type="bare_except",
                    line_number=node.lineno,
                    description="Bare except clause used. Catch specific exceptions instead.",
                    severity="high"
                )
            )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self._check_hardcoded_secrets(node.targets, node.value, node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value:
            self._check_hardcoded_secrets([node.target], node.value, node.lineno)
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self._check_hardcoded_secrets([node.target], node.value, node.lineno)
        self.generic_visit(node)

    def _check_function_or_method(self, node: ast.AST) -> None:
        name = getattr(node, "name", "unknown")
        lineno = node.lineno
        
        # 1. Check docstring
        if ast.get_docstring(node) is None:
            self.issues.append(
                Issue(
                    issue_type="missing_docstring",
                    line_number=lineno,
                    description=f"Function '{name}' is missing a docstring.",
                    severity="low"
                )
            )
            
        # 2. Check length
        body = getattr(node, "body", [])
        if body:
            start_line = body[0].lineno
            end_line = body[-1].end_lineno
            if end_line is None:
                end_line = start_line
            body_length = end_line - start_line + 1
            if body_length > 20:
                self.issues.append(
                    Issue(
                        issue_type="long_function",
                        line_number=lineno,
                        description=f"Function '{name}' body exceeds 20 lines ({body_length} lines).",
                        severity="medium"
                    )
                )

        # 3. Check type hints for parameters (excluding self/cls)
        args_obj = getattr(node, "args", None)
        if args_obj:
            params = []
            if hasattr(args_obj, "posonlyargs"):
                params.extend(args_obj.posonlyargs)
            if hasattr(args_obj, "args"):
                params.extend(args_obj.args)
            if hasattr(args_obj, "kwonlyargs"):
                params.extend(args_obj.kwonlyargs)
            if args_obj.vararg:
                params.append(args_obj.vararg)
            if args_obj.kwarg:
                params.append(args_obj.kwarg)

            for param in params:
                param_name = param.arg
                # Exclude self and cls parameters from missing type hint warnings
                if param_name in ("self", "cls"):
                    continue
                if param.annotation is None:
                    self.issues.append(
                        Issue(
                            issue_type="missing_type_hint",
                            line_number=param.lineno,
                            description=f"Parameter '{param_name}' in function '{name}' has no type hint annotation.",
                            severity="low"
                        )
                    )

    def _check_hardcoded_secrets(self, targets: List[ast.AST], value: ast.AST, lineno: int) -> None:
        if not (isinstance(value, ast.Constant) and isinstance(value.value, str)):
            return

        secret_patterns = ["password", "secret", "key", "token", "api"]
        
        for target in targets:
            target_name = ""
            if isinstance(target, ast.Name):
                target_name = target.id
            elif isinstance(target, ast.Attribute):
                target_name = target.attr
            elif isinstance(target, ast.arg):
                target_name = target.arg
            
            if target_name:
                normalized_name = target_name.lower()
                if any(pattern in normalized_name for pattern in secret_patterns):
                    self.issues.append(
                        Issue(
                            issue_type="hardcoded_secret",
                            line_number=lineno,
                            description=f"Potential hardcoded secret assigned to variable '{target_name}'.",
                            severity="high"
                        )
                    )

def analyze_code(source_code: str) -> List[Issue]:
    """Pure, stateless function that runs static analysis on source code."""
    analyzer = CodeAnalyzer(source_code)
    return analyzer.analyze()
