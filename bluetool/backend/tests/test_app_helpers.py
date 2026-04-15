import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import (
    is_module_title,
    normalize_llm_response,
    parse_llm_points,
)


def test_is_module_title_supports_nested_numeric_patterns():
    assert is_module_title("1. 用户登录")
    assert is_module_title("1.1 登录页面")
    assert is_module_title("2.3.4 子模块")
    assert is_module_title("# 一级标题")
    assert not is_module_title("普通内容描述")


def test_normalize_llm_response_supports_dict_payload():
    assert normalize_llm_response({"text": '[{"description":"A"}]'}) == '[{"description":"A"}]'
    assert normalize_llm_response({"output_text": '[{"description":"B"}]'}) == '[{"description":"B"}]'


def test_parse_llm_points_supports_markdown_json_block():
    payload = """```json
    [{"description":"验证导入功能","priority":"高"}]
    ```"""
    points = parse_llm_points(payload)
    assert isinstance(points, list)
    assert points[0]["description"] == "验证导入功能"
