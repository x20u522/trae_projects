import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import (
    improve_generated_points,
    is_module_title,
    normalize_llm_response,
    parse_llm_points,
    extract_structured_points_from_lines,
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


def test_extract_structured_points_from_lines_can_parse_business_rules():
    lines = [
        "## 报价中心",
        "### 报价列表",
        "支持选中导出或全部导出",
        "未勾选任何数据时导出当前列表全部数据",
        "总成本（不含税）=（铜箔+胶液+玻璃布+制造费）÷0.985",
    ]
    points = extract_structured_points_from_lines(lines)
    descriptions = [p["description"] for p in points]
    assert any("业务流程" in d for d in descriptions)
    assert any("公式计算" in d for d in descriptions)


def test_improve_generated_points_falls_back_when_ai_output_is_low_quality():
    bad_points = [{
        "description": "验证规则动作[1]: 所有配置管理模块",
        "title": "规则规则动作1",
        "priority": "高"
    }]
    chunks = [{"content": "## 报价中心\n### 单笔核算\n支持核算\n必须校验必填项"}]
    improved = improve_generated_points(bad_points, chunks)
    assert len(improved) >= 3
    assert all("规则动作[1]" not in p.get("description", "") for p in improved)
