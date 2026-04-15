import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import (
    improve_generated_points,
    is_module_title,
    normalize_llm_response,
    parse_llm_points,
    extract_structured_points_from_lines,
    build_default_generic_points,
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


def test_extract_structured_points_from_lines_supports_core_doc_scenarios():
    """
    文档解析测试点生成的核心作用：
    1) 识别层级结构（模块/子模块）
    2) 提取流程动作类语句
    3) 提取规则约束类语句
    4) 提取公式计算类语句
    """
    lines = [
        "## Module A",
        "### Sub Module B",
        "支持执行批量操作并返回处理结果",
        "当输入不合法时必须阻断提交",
        "总费用 = 基础值 + 调整值",
    ]
    points = extract_structured_points_from_lines(lines)
    descriptions = [p["description"] for p in points]
    assert any("业务流程" in d for d in descriptions)
    assert any("公式计算" in d for d in descriptions)
    assert any("规则约束生效" in d for d in descriptions)


def test_improve_generated_points_falls_back_when_ai_output_is_low_quality():
    bad_points = [{
        "description": "验证规则动作[1]: 所有配置管理模块",
        "title": "规则规则动作1",
        "priority": "高"
    }]
    chunks = [{"content": "## Module X\n### Sub Module Y\n支持执行流程\n必须校验前置条件"}]
    improved = improve_generated_points(bad_points, chunks)
    assert len(improved) >= 3
    assert all("规则动作[1]" not in p.get("description", "") for p in improved)


def test_generic_fallback_points_are_domain_agnostic():
    points = build_default_generic_points("Module A", "Sub Module B")
    assert len(points) >= 6
    # 不依赖任何固定业务术语：仅验证结构与可执行性
    for p in points:
        assert p["module"] == "Module A"
        assert p["sub_module"] == "Sub Module B"
        assert p["description"]
        assert p["priority"] in ("高", "中", "低")
        assert p["test_type"] in ("功能测试", "异常测试", "边界测试", "交互测试", "权限测试", "性能测试")


def test_extract_structured_points_from_markdown_table_is_generic():
    lines = [
        "## Entity Management",
        "### Field Definition",
        "| 字段名称 | 字段类型 | 是否必填 |",
        "| --- | --- | --- |",
        "| FieldAlpha | Text | Yes |",
        "| FieldBeta | Number | No |",
    ]
    points = extract_structured_points_from_lines(lines)
    desc = [p["description"] for p in points]
    assert any("字段[FieldAlpha]" in d for d in desc)
    assert any("字段[FieldBeta]" in d for d in desc)


def test_extract_structured_points_can_handle_mixed_document_sections():
    """
    覆盖“任意文档”常见混合段落：
    - 标题层级
    - 列表规则
    - 表格字段
    - 普通文本噪声
    """
    lines = [
        "## Platform",
        "### Access Control",
        "- 支持角色授权",
        "- 不允许未授权访问",
        "",
        "| 参数 | 类型 | 说明 |",
        "| --- | --- | --- |",
        "| token | string | 访问凭证 |",
        "这里是一段普通说明文本，不包含关键动作词",
    ]
    points = extract_structured_points_from_lines(lines)
    descriptions = [p["description"] for p in points]
    assert any("业务流程" in d for d in descriptions)
    assert any("规则约束生效" in d for d in descriptions)
    assert any("字段[token]" in d for d in descriptions)
