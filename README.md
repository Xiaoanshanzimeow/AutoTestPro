# 接口自动化测试框架（AutoTestPro）

基于 **Pytest + YAML 数据驱动** 的接口自动化测试框架，配套独立的 Flask Mock 服务，实现测试与业务代码分离。

## 架构

- **单接口正反向测试**：等价类划分 + 边界值分析，覆盖正常用例与缺参/错值等失败用例
- **接口串联测试**：通过 `extract.yaml` 全局参数池在用例间传递数据（token、order_id 等）
- **业务流程测试**：按真实业务链路串联多个接口，模拟端到端流程

```
testcase/
├── Single interface/    # 单接口正反向
├── ProductManager/      # 接口串联
└── Business interface/  # 业务流程
mock_server/api_server/  # Flask Mock 服务（127.0.0.1:8787）
```

## 快速开始

```bash
# 1. 装依赖（推荐 uv）
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# 2. 起 mock 服务（注意在 base/ 目录下启动）
cd mock_server/api_server/base
python flask_service.py

# 3. 跑测试（另一个终端，在项目根目录）
cd <项目根目录> && source .venv/bin/activate
pytest testcase/ -v
```

## 技术栈

Pytest · PyYAML · Requests · Allure · Flask · 数据驱动 · 参数化
