# 接口自动化测试框架（AutoTestPro）

基于 **Pytest + YAML 数据驱动** 的接口自动化测试框架，配套独立的 Flask Mock 服务，实现「测试代码」与「被测系统」解耦，并接入 GitHub Actions 完成无人值守的 CI/CD。

## 特性

- **YAML 数据驱动**：用例用 YAML 描述（接口地址、参数、断言、提取），测试代码只做通用执行引擎，新增用例零代码改动。
- **三层测试结构**：单接口正反向 / 接口串联 / 业务场景，覆盖从单点到端到端。
- **强断言引擎**：支持 `contains` / `eq` / `ne` / `nv` / `db`（数据库落库校验）/ `schema`（JSON Schema 结构校验）六种断言模式。
- **接口关联**：通过 `extract.yaml` 变量池在用例间传递数据（token、orderNumber 等），`${get_extract_data(xxx)}` 占位符动态替换。
- **并发 + 失败重试**：pytest-xdist 多进程并发、pytest-rerunfailures 失败自动重试、pytest-order 依赖链排序，并按 worker 隔离变量池。
- **Mock 故障注入**：Mock 通过 `X-Mock-Fault` 请求头模拟第三方 500 / 延迟，测支付回调的容错与幂等。
- **CI/CD**：GitHub Actions push 触发 → 起 MySQL → 起 Mock → 跑全量 → Allure 报告发布到 GitHub Pages。
- **密码脱敏**：数据库密码走 `.env`（gitignored），代码 `os.getenv` 优先读环境变量，`config.ini` 只留占位符兜底。

## 架构

```
AutoTestPro/
├── testcase/                    # 测试用例（YAML 数据 + 极薄的 pytest 收集层）
│   ├── Single interface/        # 单接口正反向
│   ├── ProductManager/          # 接口串联（商品列表→详情→下单→支付）
│   └── Business interface/      # 业务场景（支付成功/失败/幂等/故障注入）
├── base/                        # 执行引擎（发请求、占位符替换、提取、断言编排）
├── common/                      # 公共库（断言、DB 连接、YAML 读写、日志）
├── conf/                        # 配置（config.ini、.env 加载）
├── data/                        # 数据文件（登录用例等）
├── mock_server/api_server/      # 独立 Flask Mock 服务（127.0.0.1:8787）
├── conftest.py                  # 根级 fixture（清理环境、结果通知）
└── .github/workflows/ci.yml     # CI/CD 流水线
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置数据库密码（复制模板，填入真实密码；.env 已 gitignore，不入库）
cp .env.example .env

# 3. 起 Mock 服务（另开一个终端，注意在 base/ 目录下启动）
cd mock_server/api_server/base
python flask_service.py

# 4. 跑测试（回到项目根目录）
pytest testcase -v
```

> Mock 服务与被测系统是解耦的：pytest 只通过 HTTP 请求 Mock（`[api_envi]` 里的 `127.0.0.1:8787`），从不 import Mock 代码。

## 断言模式

在用例的 `validation` 里声明，`assert_result` 统一分发：

| 关键字 | 语义 | 示例 |
|---|---|---|
| `contains` | 响应包含（支持 `status_code`、空值、子串） | `contains: {'error_code': '0000'}` |
| `eq` | 多字段精确相等 | `eq: {'message': '登录成功', 'msg_code': 200}` |
| `ne` | 不相等 | `ne: {'error_code': '0000'}` |
| `nv` | 任意值（单字段） | `nv: {'status': '0'}` |
| `db` | 数据库落库断言 | `db: "SELECT * FROM orders WHERE order_number='xxx' AND status='1'"` |
| `schema` | JSON Schema 结构校验 | `schema: {type: object, required: [msg], properties: {...}}` |

## 数据驱动示例

```yaml
- baseInfo:
    api_name: 用户登录
    url: /dar/user/login
    method: POST
    header:
      Content-Type: application/x-www-form-urlencoded;charset=UTF-8
  testCase:
    - case_name: 用户名密码正确登录
      data:
        user_name: test01
        passwd: admin123
      validation:
        - eq: {'msg': '登录成功'}
      extract:
        token: $.token          # 提取 token 进变量池，供后续用例 ${get_extract_data(token)} 引用
```

## Mock 故障注入

Mock 的回调接口通过 `X-Mock-Fault` 请求头模拟第三方异常（放在 header 是为了不污染真实业务字段）：

| 值 | 行为 |
|---|---|
| `500` | 返回 500，不写订单状态（订单保持待支付） |
| `delay` | 延迟 2 秒后正常处理 |

```yaml
header:
  X-Mock-Fault: '500'   # 模拟第三方支付服务不可用
```

## CI/CD

push / PR 触发 `.github/workflows/ci.yml`：起 MySQL 8 容器 → 现场生成 `.env`（密码来自 GitHub Secret）→ 建 `orders` 表 → 起 Mock → `pytest` 跑全量 → 生成 Allure → 发布到 GitHub Pages。

## 技术栈

Pytest · PyYAML · Requests · Allure · Flask · pytest-xdist · pytest-rerunfailures · pytest-order · jsonschema · python-dotenv · PyMySQL · GitHub Actions
