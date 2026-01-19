"""
Demo: Word 文档智能填写系统
支持上传、预览、AI自动填写、下载的完整流程
"""
import json
import os
import shutil
import threading
import time
import uuid
from flask import Flask, render_template, send_file, request, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from deepseek_agent import DeepSeekAgent
from config import API_CONFIG
from word_engine import WordEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'deepseek-word-demo'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 全局状态
word_app = None
current_doc_path = None  # 当前操作的文档路径
temp_doc_path = None     # 临时预览文件路径
agent_running = False
operation_logs = []

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== 工具包装函数 ====================

def broadcast_update(action, detail=""):
    """广播文档更新事件到前端"""
    global temp_doc_path
    if word_app and temp_doc_path:
        word_app.doc.save(temp_doc_path)
    
    log_entry = {
        "time": time.strftime("%H:%M:%S"),
        "action": action,
        "detail": detail[:200] if detail else ""
    }
    operation_logs.append(log_entry)
    
    socketio.emit('doc_updated', {
        'action': action,
        'detail': detail[:200] if detail else "",
        'timestamp': log_entry["time"]
    })
    
    time.sleep(0.3)


# ========== 通用表格工具 ==========

def list_tables():
    """列出文档中所有表格的概要信息"""
    result = word_app.list_all_tables()
    if isinstance(result, str):
        return result
    
    summary = [f"文档共有 {len(result)} 个表格:"]
    for t in result:
        summary.append(f"  表格{t['index']}: {t['rows']}行x{t['cols']}列, 预览: {t['preview']}")
    
    broadcast_update("📋 列出表格", f"共 {len(result)} 个表格")
    return "\n".join(summary)


def view_table(table_index):
    """查看指定表格的完整内容（文本格式）"""
    result = word_app.get_table_as_text(int(table_index))
    broadcast_update("👁️ 查看表格", f"表格 {table_index}")
    return result


def analyze_table(table_index):
    """深度分析表格结构，识别可填写的单元格和标签-值对"""
    result = word_app.analyze_table(int(table_index))
    if "error" in result:
        return f"分析失败: {result['error']}"
    
    summary = [f"表格 {table_index} 分析结果:"]
    summary.append(f"  大小: {result['total_rows']}行 x {result['total_cols']}列")
    summary.append(f"  识别到 {len(result['label_value_pairs'])} 个标签-值对:")
    
    for pair in result['label_value_pairs'][:20]:
        status = "(待填)" if pair['needs_fill'] else f"(已填: {pair['current_value'][:20]})"
        pos = pair['value_position']
        summary.append(f"    - {pair['label']} → 位置[{pos['row']},{pos['col']}] {status}")
    
    if len(result['label_value_pairs']) > 20:
        summary.append(f"    ... 还有 {len(result['label_value_pairs']) - 20} 个")
    
    broadcast_update("🔍 分析表格", f"表格 {table_index}: {len(result['label_value_pairs'])} 个字段")
    return "\n".join(summary)


def fill_cell(table_index, row, col, value):
    """填写指定位置的单元格"""
    result = word_app.fill_cell(int(table_index), int(row), int(col), value)
    broadcast_update("✏️ 填写单元格", f"表格{table_index}[{row},{col}] = {value}")
    return result


def fill_by_label(table_index, label, value):
    """根据标签文本查找并填写"""
    result = word_app.fill_by_label(int(table_index), label, value)
    broadcast_update("✏️ 按标签填写", f"{label} = {value}")
    return result


def fill_multiple_by_labels(table_index, label_value_map):
    """批量根据标签填写多个值"""
    result = word_app.fill_multiple_by_labels(int(table_index), label_value_map)
    broadcast_update("✏️ 批量填写", f"{len(label_value_map)} 个字段")
    return result


def fill_row(table_index, row_index, values, start_col=0):
    """在指定行中从左到右填写空单元格"""
    result = word_app.find_and_fill_empty_cells_in_row(
        int(table_index), int(row_index), values, int(start_col)
    )
    broadcast_update("📝 填写行", f"表格{table_index} 第{row_index}行")
    return result


def find_empty_row(table_index, check_col=0, start_row=1):
    """查找表格中第一个空行"""
    result = word_app.find_empty_row(int(table_index), int(check_col), int(start_row))
    if result == -1:
        return "未找到空行"
    return f"找到空行: 第 {result} 行"


# ==================== 工具定义 ====================

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_tables",
            "description": "List all tables in the document with their basic info (rows, cols, preview). Call this FIRST to see what tables exist.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_table",
            "description": "View the complete content of a specific table in text format. Useful for understanding the table structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_index": {"type": "integer", "description": "Index of the table (0-based)"}
                },
                "required": ["table_index"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_table",
            "description": "Deep analyze a table to identify fillable cells and label-value pairs. Returns positions and current values.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_index": {"type": "integer", "description": "Index of the table (0-based)"}
                },
                "required": ["table_index"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fill_cell",
            "description": "Fill a specific cell by row and column index. Use when you know the exact position.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_index": {"type": "integer", "description": "Index of the table (0-based)"},
                    "row": {"type": "integer", "description": "Row index (0-based)"},
                    "col": {"type": "integer", "description": "Column index (0-based)"},
                    "value": {"type": "string", "description": "Value to fill"}
                },
                "required": ["table_index", "row", "col", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fill_by_label",
            "description": "Find a cell by its label text and fill the adjacent value cell. Supports partial matching. This is the RECOMMENDED way to fill form fields.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_index": {"type": "integer", "description": "Index of the table (0-based)"},
                    "label": {"type": "string", "description": "The label text to search for (e.g., '姓名', '电话')"},
                    "value": {"type": "string", "description": "Value to fill"}
                },
                "required": ["table_index", "label", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fill_multiple_by_labels",
            "description": "Fill multiple cells by their labels at once. More efficient for filling many fields.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_index": {"type": "integer", "description": "Index of the table (0-based)"},
                    "label_value_map": {
                        "type": "object",
                        "description": "A dictionary mapping labels to values, e.g., {'姓名': '张三', '电话': '13800138000'}",
                        "additionalProperties": {"type": "string"}
                    }
                },
                "required": ["table_index", "label_value_map"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fill_row",
            "description": "Fill empty cells in a specific row from left to right with provided values. Useful for filling list/table rows.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_index": {"type": "integer", "description": "Index of the table (0-based)"},
                    "row_index": {"type": "integer", "description": "Row index (0-based)"},
                    "values": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of values to fill in order"
                    },
                    "start_col": {"type": "integer", "description": "Starting column (default 0)", "default": 0}
                },
                "required": ["table_index", "row_index", "values"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_empty_row",
            "description": "Find the first empty row in a table (where specified column is empty). Useful for finding where to add new data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_index": {"type": "integer", "description": "Index of the table (0-based)"},
                    "check_col": {"type": "integer", "description": "Column to check for emptiness (default 0)", "default": 0},
                    "start_row": {"type": "integer", "description": "Row to start searching from (default 1, skips header)", "default": 1}
                },
                "required": ["table_index"]
            }
        }
    },
]

TOOL_MAP = {
    "list_tables": list_tables,
    "view_table": view_table,
    "analyze_table": analyze_table,
    "fill_cell": fill_cell,
    "fill_by_label": fill_by_label,
    "fill_multiple_by_labels": fill_multiple_by_labels,
    "fill_row": fill_row,
    "find_empty_row": find_empty_row
}


# ==================== Flask 路由 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文档"""
    global current_doc_path, temp_doc_path, word_app
    
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "没有文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "没有选择文件"}), 400
    
    if file and allowed_file(file.filename):
        original_name = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}_{original_name}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(filepath)
        current_doc_path = filepath
        
        temp_doc_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
        shutil.copy(filepath, temp_doc_path)
        
        word_app = WordEngine(temp_doc_path)
        
        return jsonify({
            "status": "success",
            "message": "文件上传成功",
            "filename": original_name,
            "file_id": unique_id
        })
    
    return jsonify({"status": "error", "message": "不支持的文件格式，请上传 .docx 文件"}), 400


@app.route('/api/preview')
def get_preview():
    """获取当前文档预览文件"""
    global temp_doc_path
    if temp_doc_path and os.path.exists(temp_doc_path):
        return send_file(temp_doc_path, as_attachment=False, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    return jsonify({"status": "error", "message": "没有可预览的文档"}), 404


@app.route('/api/download')
def download_file():
    """下载填写完成的文档"""
    global temp_doc_path, current_doc_path
    if temp_doc_path and os.path.exists(temp_doc_path):
        original_name = os.path.basename(current_doc_path) if current_doc_path else "document.docx"
        if '_' in original_name:
            original_name = '_'.join(original_name.split('_')[1:])
        name_parts = original_name.rsplit('.', 1)
        download_name = f"{name_parts[0]}_已填写.docx" if len(name_parts) > 1 else f"{original_name}_已填写.docx"
        
        return send_file(
            temp_doc_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    return jsonify({"status": "error", "message": "没有可下载的文档"}), 404


@app.route('/api/logs')
def get_logs():
    """获取操作日志"""
    return jsonify(operation_logs)


@app.route('/api/start', methods=['POST'])
def start_agent():
    """启动 Agent 处理任务"""
    global agent_running, word_app, operation_logs, temp_doc_path, current_doc_path
    
    if agent_running:
        return jsonify({"status": "error", "message": "Agent 正在运行中"})
    
    data = request.json
    user_request = data.get('prompt', '')
    
    if not user_request.strip():
        return jsonify({"status": "error", "message": "请输入任务描述"})
    
    if not temp_doc_path or not os.path.exists(temp_doc_path):
        return jsonify({"status": "error", "message": "请先上传文档"})
    
    operation_logs = []
    
    if current_doc_path and os.path.exists(current_doc_path):
        shutil.copy(current_doc_path, temp_doc_path)
        word_app = WordEngine(temp_doc_path)
    
    def run_agent():
        global agent_running
        agent_running = True
        
        try:
            socketio.emit('agent_status', {'status': 'running', 'message': '🚀 Agent 启动中...'})
            
            agent = DeepSeekAgent(**API_CONFIG)
            messages = [
                {"role": "user", "content": user_request + " (Tips: You can execute multiple tool calls in a single turn to save time. Use fill_by_label for form fields.)"}
            ]
            
            run_agent_with_broadcast(agent, messages, tools, TOOL_MAP, max_turns=50)
            
            # 只有在未被停止的情况下才发送完成状态
            if agent_running:
                socketio.emit('agent_status', {'status': 'completed', 'message': '✅ 任务完成!'})
            
        except Exception as e:
            socketio.emit('agent_status', {'status': 'error', 'message': f'❌ 错误: {str(e)}'})
        finally:
            agent_running = False
    
    thread = threading.Thread(target=run_agent)
    thread.start()
    
    return jsonify({"status": "started", "message": "Agent 已启动"})


def run_agent_with_broadcast(agent, messages, tools, tool_map, max_turns=10):
    """运行 Agent 并广播状态"""
    global agent_running
    for i in range(max_turns):
        if not agent_running:
            socketio.emit('agent_status', {'status': 'stopped', 'message': '⏹️ 已停止'})
            break
        socketio.emit('agent_thinking', {'turn': i + 1, 'message': f'🤔 第 {i+1} 轮思考中...'})
        
        try:
            response = agent.client.chat.completions.create(
                model=agent.model_name,
                messages=messages,
                tools=tools,
                extra_body=agent.extra_body
            )
        except Exception as e:
            socketio.emit('agent_error', {'message': f'API 错误: {str(e)}'})
            break

        message = response.choices[0].message
        
        reasoning_content = getattr(message, 'reasoning_content', None)
        if reasoning_content:
            socketio.emit('agent_reasoning', {'content': reasoning_content[:500] + '...' if len(reasoning_content) > 500 else reasoning_content})
            msg_dict = message.model_dump(exclude_none=True)
            msg_dict['reasoning_content'] = reasoning_content
            messages.append(msg_dict)
        else:
            messages.append(message)

        if message.content:
            socketio.emit('agent_response', {'content': message.content})

        if message.tool_calls:
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args_str = tool_call.function.arguments
                
                socketio.emit('tool_call', {
                    'name': func_name,
                    'args': args_str[:200] if len(args_str) > 200 else args_str
                })
                
                if tool_map and func_name in tool_map:
                    try:
                        args = json.loads(args_str)
                        result = tool_map[func_name](**args)
                        result_str = str(result)
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_str
                        })
                    except Exception as e:
                        error_msg = f"Error executing tool {func_name}: {str(e)}"
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": error_msg
                        })
        else:
            break


@app.route('/api/stop', methods=['POST'])
def stop_agent():
    """停止 Agent"""
    global agent_running
    agent_running = False
    return jsonify({"status": "stopped"})


@app.route('/api/reset', methods=['POST'])
def reset_document():
    """重置文档到原始状态"""
    global word_app, temp_doc_path, current_doc_path, operation_logs
    
    if current_doc_path and os.path.exists(current_doc_path) and temp_doc_path:
        shutil.copy(current_doc_path, temp_doc_path)
        word_app = WordEngine(temp_doc_path)
        operation_logs = []
        return jsonify({"status": "success", "message": "文档已重置"})
    
    return jsonify({"status": "error", "message": "没有可重置的文档"}), 400


# ==================== WebSocket 事件 ====================

@socketio.on('connect')
def handle_connect():
    print('客户端已连接')
    emit('connected', {'message': '已连接到服务器'})


@socketio.on('disconnect')
def handle_disconnect():
    print('客户端已断开')


# ==================== 主程序 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Word 文档智能填写系统")
    print("=" * 60)
    print("📁 上传目录: uploads/")
    print("🌐 访问地址: http://localhost:5000")
    print("=" * 60)
    
    os.makedirs('templates', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    for f in os.listdir('uploads'):
        if f.startswith('temp_'):
            try:
                os.remove(os.path.join('uploads', f))
            except:
                pass
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
