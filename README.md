# Qwen3-32B 模型服务

这是一个使用 Qwen3-32B 模型的服务实现，支持对话和工具调用功能。

## 环境要求

- Python 3.8+
- CUDA 支持（推荐）或 CPU
- 至少 64GB 系统内存
- 如果使用 GPU，建议显存 32GB 以上

## 安装

1. 克隆仓库：
```bash
git clone <repository_url>
cd <repository_name>
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

```python
from model_service import QwenService

# 初始化服务
service = QwenService()

# 对话示例
messages = [
    {"role": "user", "content": "你好，请介绍一下你自己"}
]
response = service.chat(messages)
print(response)
```

### 工具调用

```python
# 定义工具
tools = [
    {
        "name": "get_weather",
        "description": "获取指定城市的天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称"
                }
            },
            "required": ["city"]
        }
    }
]

# 调用工具
query = "请帮我查询北京的天气"
response = service.call_tool(query, tools)
print(response)
```

## 注意事项

1. 首次运行时会自动下载模型，需要较长时间和足够的磁盘空间
2. 建议使用 GPU 运行，CPU 运行会较慢
3. 模型输出可能需要进行适当的后处理
4. 请确保网络连接正常，以便下载模型

## 参数说明

### QwenService 类

- `model_path`: 模型路径，默认为 "Qwen/Qwen3-32B"
- `device`: 自动选择 CUDA 或 CPU

### chat 方法

- `messages`: 对话历史列表
- `max_length`: 生成文本的最大长度，默认 2048

### call_tool 方法

- `query`: 用户输入的查询文本
- `tools`: 工具列表，包含工具的名称、描述和参数信息 