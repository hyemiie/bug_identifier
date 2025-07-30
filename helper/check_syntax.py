from typing import Optional


def check_syntax_errors(code: str, language: str) -> tuple[bool, Optional[str]]:
    if language.lower() == "python":
        try:
            compile(code, '<string>', 'exec')
            return False, None
        except SyntaxError as e:
            error_msg = f"Syntax error on line {e.lineno}: {e.msg}"
            if e.text:
                error_msg += f" -> '{e.text.strip()}'"
            return True, error_msg
    return False, None

