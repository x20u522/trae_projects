import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import uuid

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['HISTORY_FILE'] = 'history.json'

ALLOWED_EXTENSIONS = {'md', 'docx', 'pdf', 'txt'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_history():
    if os.path.exists(app.config['HISTORY_FILE']):
        with open(app.config['HISTORY_FILE'], 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(app.config['HISTORY_FILE'], 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # 检查是否重复上传
        history = load_history()
        existing_file = next((f for f in history if f['original_name'] == filename), None)
        
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        file_info = {
            'id': unique_filename,
            'original_name': filename,
            'stored_name': unique_filename,
            'filepath': filepath,
            'upload_time': datetime.now().isoformat(),
            'status': 'uploaded'
        }

        history = load_history()
        history.append(file_info)
        save_history(history)

        return jsonify({
            'success': True,
            'file': file_info
        })

    return jsonify({'error': '不支持的文件格式'}), 400

@app.route('/api/history', methods=['GET'])
def get_history():
    history = load_history()
    return jsonify({'success': True, 'history': history})

@app.route('/api/parse', methods=['POST'])
def parse_document():
    data = request.json
    file_id = data.get('file_id')

    history = load_history()
    file_info = next((f for f in history if f['id'] == file_id), None)

    if not file_info:
        return jsonify({'error': '文件不存在'}), 404

    filepath = file_info['filepath']
    file_extension = file_info['original_name'].rsplit('.', 1)[1].lower() if '.' in file_info['original_name'] else ''

    try:
        if file_extension == 'md' or file_extension == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        elif file_extension == 'docx':
            from docx import Document
            doc = Document(filepath)
            content = '\n'.join([para.text for para in doc.paragraphs])
        elif file_extension == 'pdf':
            from PyPDF2 import PdfReader
            reader = PdfReader(filepath)
            content = ''
            for page in reader.pages:
                content += page.extract_text() + '\n'
        else:
            return jsonify({'error': '不支持的文件格式'}), 400

        chunks = split_document(content)

        return jsonify({
            'success': True,
            'content': content,
            'chunks': chunks
        })
    except Exception as e:
        return jsonify({'error': f'解析失败: {str(e)}'}), 500

def split_document(content):
    chunks = []
    lines = content.split('\n')
    current_chunk = {'title': '文档整体', 'content': [], 'type': 'overview'}

    current_section = None
    section_content = []

    for line in lines:
        if line.strip().startswith('#'):
            if section_content:
                if current_section:
                    chunks.append({
                        'title': current_section,
                        'content': '\n'.join(section_content),
                        'type': 'section'
                    })
                else:
                    current_chunk['content'] = '\n'.join(section_content)

            current_section = line.strip()
            section_content = []
        elif line.strip() and current_section:
            section_content.append(line)
        elif line.strip():
            section_content.append(line)

    if section_content:
        chunks.append({
            'title': current_section if current_section else '文档内容',
            'content': '\n'.join(section_content),
            'type': 'section'
        })

    if current_chunk['content']:
        chunks.insert(0, current_chunk)

    if not chunks:
        chunks.append({'title': '文档内容', 'content': content, 'type': 'content'})

    return chunks

@app.route('/api/generate-test-points', methods=['POST'])
def generate_test_points():
    from langchain_openai import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain

    data = request.json
    chunks = data.get('chunks', [])

    api_key = os.getenv('OPENAI_API_KEY')
    model_name = data.get('model', 'gpt-3.5-turbo')

    if not api_key:
        # 基于文档内容生成测试点
        test_points = generate_test_points_from_content(chunks)
        return jsonify({
            'error': '未配置API密钥，使用基于文档内容的测试点生成',
            'test_points': test_points
        }), 200

    try:
        llm = ChatOpenAI(
            api_key=api_key,
            model=model_name,
            temperature=0.7
        )

        prompt_template = PromptTemplate(
            input_variables=["content"],
            template="""你是一位资深软件测试工程师。请分析以下需求文档内容，提取测试点。

要求：
1. 输出JSON格式的测试点列表
2. 每个测试点包含：test_point_id, category, description, priority, test_type
3. test_type可选值：功能测试, 交互测试, 异常测试, 边界测试, 权限测试, 性能测试
4. priority可选值：高, 中, 低
5. category分类：功能点, 交互点, 异常点, 边界点, 校验点

需求文档内容：
{content}

请生成测试点列表（JSON格式）："""
        )

        chain = LLMChain(llm=llm, prompt=prompt_template)
        all_test_points = []

        for idx, chunk in enumerate(chunks):
            response = chain.run(content=chunk['content'][:2000])

            try:
                points = json.loads(response)
                if isinstance(points, list):
                    for point in points:
                        point['chunk_id'] = idx
                        point['test_point_id'] = f"TP-{len(all_test_points) + 1:03d}"
                    all_test_points.extend(points)
            except json.JSONDecodeError:
                points = parse_text_test_points(response)
                for point in points:
                    point['chunk_id'] = idx
                    point['test_point_id'] = f"TP-{len(all_test_points) + 1:03d}"
                all_test_points.extend(points)

        return jsonify({
            'success': True,
            'test_points': all_test_points
        })

    except Exception as e:
        return jsonify({
            'error': f'AI生成失败: {str(e)}',
            'test_points': generate_demo_test_points()
        }), 200

def parse_text_test_points(text):
    points = []
    lines = text.split('\n')
    current_point = None

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('```'):
            continue

        if line[0].isdigit() or line.startswith('-') or line.startswith('*'):
            if current_point:
                points.append(current_point)

            current_point = {
                'test_point_id': f"TP-{len(points) + 1:03d}",
                'category': '功能点',
                'description': line.lstrip('0123456789.-* ').strip(),
                'priority': '中',
                'test_type': '功能测试'
            }

    if current_point:
        points.append(current_point)

    return points

def generate_demo_test_points():
    return [
        {
            'test_point_id': 'TP-001',
            'category': '功能点',
            'description': '验证用户能够成功上传需求文档',
            'priority': '高',
            'test_type': '功能测试',
            'chunk_id': 0
        },
        {
            'test_point_id': 'TP-002',
            'category': '功能点',
            'description': '验证系统能够正确解析Markdown格式文档',
            'priority': '高',
            'test_type': '功能测试',
            'chunk_id': 0
        },
        {
            'test_point_id': 'TP-003',
            'category': '异常点',
            'description': '验证上传不支持的文件格式时的错误处理',
            'priority': '中',
            'test_type': '异常测试',
            'chunk_id': 0
        },
        {
            'test_point_id': 'TP-004',
            'category': '边界点',
            'description': '验证超大文档的分块处理能力',
            'priority': '中',
            'test_type': '边界测试',
            'chunk_id': 0
        },
        {
            'test_point_id': 'TP-005',
            'category': '校验点',
            'description': '验证文档内容提取的完整性',
            'priority': '高',
            'test_type': '功能测试',
            'chunk_id': 0
        },
        {
            'test_point_id': 'TP-006',
            'category': '交互点',
            'description': '验证用户界面操作的流畅性',
            'priority': '中',
            'test_type': '交互测试',
            'chunk_id': 1
        },
        {
            'test_point_id': 'TP-007',
            'category': '功能点',
            'description': '验证测试点的手动编辑功能',
            'priority': '高',
            'test_type': '功能测试',
            'chunk_id': 1
        },
        {
            'test_point_id': 'TP-008',
            'category': '异常点',
            'description': '验证空文档上传的处理',
            'priority': '低',
            'test_type': '异常测试',
            'chunk_id': 1
        },
        {
            'test_point_id': 'TP-009',
            'category': '权限测试',
            'description': '验证未授权用户访问控制',
            'priority': '高',
            'test_type': '权限测试',
            'chunk_id': 2
        },
        {
            'test_point_id': 'TP-010',
            'category': '性能测试',
            'description': '验证大量测试点生成时的响应时间',
            'priority': '中',
            'test_type': '性能测试',
            'chunk_id': 2
        }
    ]

def generate_test_points_from_content(chunks):
    """基于文档内容生成测试点"""
    test_points = []
    point_id = 1
    
    # 分析文档内容
    content_analysis = {
        'has_upload': False,
        'has_parse': False,
        'has_test_points': False,
        'has_test_cases': False,
        'has_export': False,
        'has_history': False,
        'file_types': set(),
        'has_boundary': False,
        'has_error': False
    }
    
    # 分析每个分块
    for chunk_idx, chunk in enumerate(chunks):
        content = chunk['content'].lower()
        title = chunk['title'].lower()
        
        # 检测功能模块
        if '上传' in title or 'upload' in content:
            content_analysis['has_upload'] = True
        if '解析' in title or 'parse' in content:
            content_analysis['has_parse'] = True
        if '测试点' in title or 'test point' in content:
            content_analysis['has_test_points'] = True
        if '测试用例' in title or 'test case' in content:
            content_analysis['has_test_cases'] = True
        if '导出' in title or 'export' in content:
            content_analysis['has_export'] = True
        if '历史' in title or 'history' in content:
            content_analysis['has_history'] = True
        
        # 检测文件类型
        if 'markdown' in content or 'md' in content:
            content_analysis['file_types'].add('markdown')
        if 'word' in content or 'docx' in content:
            content_analysis['file_types'].add('word')
        if 'pdf' in content:
            content_analysis['file_types'].add('pdf')
        if 'txt' in content:
            content_analysis['file_types'].add('txt')
        
        # 检测边界和异常
        if '大小' in content or 'limit' in content:
            content_analysis['has_boundary'] = True
        if '错误' in content or 'error' in content:
            content_analysis['has_error'] = True
    
    # 生成功能测试点
    if content_analysis['has_upload']:
        test_points.append({
            'test_point_id': f'TP-{point_id:03d}',
            'category': '功能点',
            'description': '验证用户能够成功上传需求文档',
            'priority': '高',
            'test_type': '功能测试',
            'chunk_id': 0
        })
        point_id += 1
    
    if content_analysis['file_types']:
        file_types_str = ', '.join(content_analysis['file_types'])
        test_points.append({
            'test_point_id': f'TP-{point_id:03d}',
            'category': '功能点',
            'description': f'验证系统能够正确解析{file_types_str}格式文档',
            'priority': '高',
            'test_type': '功能测试',
            'chunk_id': 0
        })
        point_id += 1
    
    if content_analysis['has_parse']:
        test_points.append({
            'test_point_id': f'TP-{point_id:03d}',
            'category': '功能点',
            'description': '验证系统能够正确解析文档内容',
            'priority': '高',
            'test_type': '功能测试',
            'chunk_id': 0
        })
        point_id += 1
    
    if content_analysis['has_test_points']:
        test_points.append({
            'test_point_id': f'TP-{point_id:03d}',
            'category': '功能点',
            'description': '验证AI能够从文档中提取测试点',
            'priority': '高',
            'test_type': '功能测试',
            'chunk_id': 0
        })
        point_id += 1
    
    if content_analysis['has_test_cases']:
        test_points.append({
            'test_point_id': f'TP-{point_id:03d}',
            'category': '功能点',
            'description': '验证基于测试点生成标准测试用例',
            'priority': '高',
            'test_type': '功能测试',
            'chunk_id': 0
        })
        point_id += 1
    
    if content_analysis['has_export']:
        test_points.append({
            'test_point_id': f'TP-{point_id:03d}',
            'category': '功能点',
            'description': '验证测试用例的导出功能',
            'priority': '高',
            'test_type': '功能测试',
            'chunk_id': 0
        })
        point_id += 1
    
    if content_analysis['has_history']:
        test_points.append({
            'test_point_id': f'TP-{point_id:03d}',
            'category': '功能点',
            'description': '验证历史记录管理功能',
            'priority': '中',
            'test_type': '功能测试',
            'chunk_id': 0
        })
        point_id += 1
    
    # 生成异常测试点
    test_points.append({
        'test_point_id': f'TP-{point_id:03d}',
        'category': '异常点',
        'description': '验证上传不支持的文件格式时的错误处理',
        'priority': '中',
        'test_type': '异常测试',
        'chunk_id': 0
    })
    point_id += 1
    
    test_points.append({
        'test_point_id': f'TP-{point_id:03d}',
        'category': '异常点',
        'description': '验证空文档上传的处理',
        'priority': '中',
        'test_type': '异常测试',
        'chunk_id': 0
    })
    point_id += 1
    
    test_points.append({
        'test_point_id': f'TP-{point_id:03d}',
        'category': '异常点',
        'description': '验证重复上传同一文件的处理',
        'priority': '中',
        'test_type': '异常测试',
        'chunk_id': 0
    })
    point_id += 1
    
    # 生成边界测试点
    if content_analysis['has_boundary']:
        test_points.append({
            'test_point_id': f'TP-{point_id:03d}',
            'category': '边界点',
            'description': '验证超大文档的分块处理能力',
            'priority': '中',
            'test_type': '边界测试',
            'chunk_id': 0
        })
        point_id += 1
    
    test_points.append({
        'test_point_id': f'TP-{point_id:03d}',
        'category': '边界点',
        'description': '验证文件名长度边界处理',
        'priority': '低',
        'test_type': '边界测试',
        'chunk_id': 0
    })
    point_id += 1
    
    # 生成交互和校验测试点
    test_points.append({
        'test_point_id': f'TP-{point_id:03d}',
        'category': '交互点',
        'description': '验证用户界面操作的流畅性',
        'priority': '中',
        'test_type': '交互测试',
        'chunk_id': 0
    })
    point_id += 1
    
    test_points.append({
        'test_point_id': f'TP-{point_id:03d}',
        'category': '校验点',
        'description': '验证文档内容提取的完整性',
        'priority': '高',
        'test_type': '功能测试',
        'chunk_id': 0
    })
    point_id += 1
    
    # 生成权限和性能测试点
    test_points.append({
        'test_point_id': f'TP-{point_id:03d}',
        'category': '权限测试',
        'description': '验证未授权用户访问控制',
        'priority': '高',
        'test_type': '权限测试',
        'chunk_id': 0
    })
    point_id += 1
    
    test_points.append({
        'test_point_id': f'TP-{point_id:03d}',
        'category': '性能测试',
        'description': '验证大量测试点生成时的响应时间',
        'priority': '中',
        'test_type': '性能测试',
        'chunk_id': 0
    })
    
    return test_points

@app.route('/api/generate-test-cases', methods=['POST'])
def generate_test_cases():
    from langchain_openai import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain

    data = request.json
    test_points = data.get('test_points', [])

    api_key = os.getenv('OPENAI_API_KEY')
    model_name = data.get('model', 'gpt-3.5-turbo')

    if not api_key:
        return jsonify({
            'error': '未配置API密钥',
            'test_cases': generate_demo_test_cases(test_points)
        }), 200

    try:
        llm = ChatOpenAI(
            api_key=api_key,
            model=model_name,
            temperature=0.7
        )

        prompt_template = PromptTemplate(
            input_variables=["test_point"],
            template="""你是一位资深软件测试工程师。请基于以下测试点生成标准测试用例。

测试点信息：
{test_point}

要求：
1. 输出JSON格式的测试用例
2. 每个测试用例包含：case_id, title, module, preconditions, steps, expected_results, priority
3. case_id格式：TC-XXX（序号从1开始）
4. priority可选值：高, 中, 低
5. steps必须是具体的操作步骤，每步一行
6. expected_results必须与steps一一对应

请生成测试用例（JSON格式）："""
        )

        chain = LLMChain(llm=llm, prompt=prompt_template)
        all_cases = []
        test_point_chunks = {}

        for point in test_points:
            chunk_id = point.get('chunk_id', 0)
            if chunk_id not in test_point_chunks:
                test_point_chunks[chunk_id] = []
            test_point_chunks[chunk_id].append(point)

        for chunk_id, points in test_point_chunks.items():
            combined_content = '\n'.join([
                f"{p.get('test_point_id', '')}: {p.get('description', '')} (类型: {p.get('test_type', '功能测试')}, 优先级: {p.get('priority', '中')})"
                for p in points
            ])

            try:
                response = chain.run(test_point=combined_content)
                cases = json.loads(response)

                if isinstance(cases, list):
                    for case in cases:
                        case['module'] = f"模块{chunk_id + 1}"
                        case['case_id'] = f"TC-{len(all_cases) + 1:03d}"
                        case['related_test_points'] = [p.get('test_point_id', '') for p in points]
                    all_cases.extend(cases)
                elif isinstance(cases, dict):
                    cases['module'] = f"模块{chunk_id + 1}"
                    cases['case_id'] = f"TC-{len(all_cases) + 1:03d}"
                    cases['related_test_points'] = [p.get('test_point_id', '') for p in points]
                    all_cases.append(cases)
            except (json.JSONDecodeError, Exception) as e:
                for point in points:
                    case = generate_single_case_from_point(point, len(all_cases) + 1)
                    all_cases.append(case)

        return jsonify({
            'success': True,
            'test_cases': all_cases
        })

    except Exception as e:
        return jsonify({
            'error': f'AI生成失败: {str(e)}',
            'test_cases': generate_demo_test_cases(test_points)
        }), 200

def generate_single_case_from_point(point, index):
    return {
        'case_id': f"TC-{index:03d}",
        'title': f"测试{point.get('test_point_id', f'TP{index}')}",
        'module': f"模块{point.get('chunk_id', 0) + 1}",
        'preconditions': [
            '测试环境已准备就绪',
            '测试数据已准备',
            '相关权限已分配'
        ],
        'steps': [
            f"步骤1: 进入{point.get('category', '功能')}测试场景",
            "步骤2: 执行测试操作",
            "步骤3: 记录测试结果",
            "步骤4: 验证预期结果"
        ],
        'expected_results': [
            f"能够正常进入{point.get('category', '功能')}测试场景",
            "操作执行成功",
            "测试结果正确记录",
            "预期结果与实际结果一致"
        ],
        'priority': point.get('priority', '中'),
        'related_test_points': [point.get('test_point_id', '')]
    }

def generate_demo_test_cases(test_points):
    cases = []
    for idx, point in enumerate(test_points[:10], 1):
        case = generate_single_case_from_point(point, idx)
        cases.append(case)
    return cases

@app.route('/api/export', methods=['POST'])
def export_cases():
    data = request.json
    test_cases = data.get('test_cases', [])
    format_type = data.get('format', 'json')

    if format_type == 'json':
        return jsonify({
            'success': True,
            'data': json.dumps(test_cases, ensure_ascii=False, indent=2)
        })

    elif format_type == 'markdown':
        md_content = "# 测试用例文档\n\n"
        md_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for case in test_cases:
            md_content += f"## {case.get('case_id', 'TC-000')}: {case.get('title', '未命名')}\n\n"
            md_content += f"**测试模块**: {case.get('module', '未分类')}\n\n"
            md_content += f"**优先级**: {case.get('priority', '中')}\n\n"
            md_content += f"**前置条件**:\n"
            for pre in case.get('preconditions', []):
                md_content += f"- {pre}\n"
            md_content += "\n"

            md_content += f"**测试步骤**:\n"
            for i, step in enumerate(case.get('steps', []), 1):
                md_content += f"{i}. {step}\n"
            md_content += "\n"

            md_content += f"**预期结果**:\n"
            for i, result in enumerate(case.get('expected_results', []), 1):
                md_content += f"{i}. {result}\n"
            md_content += "\n---\n\n"

        return jsonify({
            'success': True,
            'data': md_content
        })

    return jsonify({'error': '不支持的导出格式'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
