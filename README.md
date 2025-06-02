# AutoPrompt

AutoPrompt 是一个智能提示词优化系统，基于大语言模型自动生成、评估和优化提示词（Prompt）。该系统能够根据示例文本和期望输出，自动生成最优的提示词模板。

## 核心特性

- 🤖 基于 Qwen3-32B 大语言模型
- 🎯 自动生成多样化的提示词模板
- 📊 智能评估提示词效果
- 🔄 迭代优化提示词质量
- 🌐 Web 界面交互
- 🛠 支持 Ollama 本地部署

## 系统架构

### 后端组件
- `app.py`: Web 服务主入口，基于 Flask 框架
- `prompt_optimizer.py`: 提示词优化核心逻辑
- `prompt_template.py`: 提示词模板管理

### 工作流程
1. 提示词生成：根据示例生成多个候选模板
2. 响应生成：使用候选模板生成响应
3. 效果评估：评估响应相似度和模板通用性
4. 优化选择：选择最佳提示词模板

## 快速开始

### 环境要求
- Python 3.8+
- Ollama（本地运行的 LLM 服务）
- 推荐配置：
  - CPU: 8核心以上
  - 内存: 32GB以上
  - GPU: 支持 CUDA 的显卡，显存 16GB 以上

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/AutoPrompt.git
cd AutoPrompt
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 启动 Ollama 服务并加载模型：
```bash
ollama run qwen3:30b
```

4. 运行 Web 服务：
```bash
python app.py
```

5. 访问 Web 界面：
```
http://localhost:5000
```

## API 使用说明

### 优化提示词接口

```python
POST /optimize
Content-Type: application/json

{
    "example_text": "示例文本",
    "expected_output": "期望输出",
    "target_text": "目标文本",
    "last_prompt": "上一次的提示词"
}
```

响应格式：
```json
{
    "status": "success",
    "data": {
        "best_template": "最佳提示词模板",
        "best_response": "最佳响应",
        "best_similarity_score": 0.95,
        "best_generality_score": 0.85,
        "result_response": "最终生成结果"
    }
}
```

## 高级配置

### 模型配置
在 `prompt_optimizer.py` 中可以配置：
- 模型名称：`model_name`
- Ollama API 地址：`base_url`
- 温度参数：`temperature`

### 评估权重调整
在评估阶段可以调整：
- 相似度权重：默认 0.7
- 通用性权重：默认 0.3

## 最佳实践

1. 提供高质量的示例：
   - 示例文本应该具有代表性
   - 期望输出要清晰明确

2. 迭代优化：
   - 使用系统生成的最佳提示词作为下一轮优化的输入
   - 通过多轮优化获得更好的效果

3. 性能优化：
   - 适当调整生成模板的数量
   - 根据实际需求调整评估权重

## 常见问题

1. 模型连接失败：
   - 检查 Ollama 服务是否正常运行
   - 验证 API 地址配置是否正确

2. 生成结果不理想：
   - 优化示例文本的质量
   - 调整评估权重
   - 尝试多轮优化

## 贡献指南

欢迎提交 Pull Request 或 Issue！在提交之前，请确保：
- 代码符合 PEP 8 规范
- 添加必要的测试用例
- 更新相关文档

## 许可证

本项目采用 MIT 许可证 