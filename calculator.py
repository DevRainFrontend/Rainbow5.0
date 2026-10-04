import ast
import operator

MAX_LENGTH = 120
MAX_DEPTH = 12

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_node(node, depth: int = 0):
    if depth > MAX_DEPTH:
        raise ValueError("İfade çok karmaşık.")

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Yalnızca sayılar kullanılabilir.")

    if isinstance(node, ast.BinOp):
        op = _OPERATORS.get(type(node.op))
        if not op:
            raise ValueError("Desteklenmeyen işlem.")
        left = _eval_node(node.left, depth + 1)
        right = _eval_node(node.right, depth + 1)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Üs değeri çok büyük.")
        return op(left, right)

    if isinstance(node, ast.UnaryOp):
        op = _OPERATORS.get(type(node.op))
        if not op:
            raise ValueError("Desteklenmeyen işlem.")
        return op(_eval_node(node.operand, depth + 1))

    raise ValueError("Geçersiz ifade.")


def calculate(expression: str) -> float:
    expression = expression.strip()
    if not expression:
        raise ValueError("Boş ifade.")
    if len(expression) > MAX_LENGTH:
        raise ValueError("İfade çok uzun.")

    tree = ast.parse(expression, mode="eval")
    return _eval_node(tree.body)
