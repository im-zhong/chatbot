LangGraph PostgresSaver / AsyncPostgresSaver 笔记

本笔记总结了 LangGraph 中 PostgresSaver / AsyncPostgresSaver 的设计语义、生命周期、连接池行为以及正确的工程使用方式。

⸻

一、PostgresSaver 是什么？

在 LangGraph 中：
 • State：一次 graph 执行中的可变数据
 • Checkpoint：State 在某个时间点的持久化快照
 • Saver：负责把 checkpoint 写入/读取外部存储

PostgresSaver / AsyncPostgresSaver 就是：

将 LangGraph 的 state checkpoint 持久化到 PostgreSQL 的实现

⸻

二、最重要的结论（先记住）

每创建一个 PostgresSaver / AsyncPostgresSaver，都会创建一个新的数据库连接（或连接池）。

 • ❌ 不会自动共享连接池
 • ❌ 不是全局单例
 • ✅ 生命周期由你显式控制

⸻

三、同步 vs 异步 Saver 的本质区别

1️⃣ PostgresSaver（同步）
 • 内部持有 一个数据库连接（psycopg / psycopg2）
 • 不是连接池
 • 每个 saver 实例 = 一个独立连接

with PostgresSaver.from_conn_string(DB_URI) as saver:
    ...

# 退出 with → 连接关闭

⸻

2️⃣ AsyncPostgresSaver（异步）
 • 内部创建 一个 asyncpg 连接池
 • 每个 saver 实例 = 一个独立 pool
 • pool 绑定创建它的 event loop

async with AsyncPostgresSaver.from_conn_string(DB_URI) as saver:
    ...

# 退出 async with → pool 关闭

⸻

四、为什么 Saver 必须用 with / async with？

原因不是“示例代码这么写”，而是设计要求：

Saver 内部持有资源
 • 数据库连接 / 连接池
 • 事务上下文
 • checkpoint 写入器

生命周期语义

__enter__ / __aenter__  → 建立连接 / pool
__exit__  / __aexit__   → 释放连接 / pool

graph 的使用期必须 ⊆ saver 的存活期

⸻

五、graph 必须写在 with 里面吗？

❓ 常见疑问

我们在调用 graph.invoke / graph.stream 时，是否必须写在 with PostgresSaver(...) 里？

✅ 精确回答
 • ❌ 语法上不强制
 • ✅ 语义上必须保证：调用发生在 saver 未关闭之前

❌ 错误示例（use-after-close）

with PostgresSaver.from_conn_string(DB_URI) as saver:
    graph = builder.compile(checkpointer=saver)

# saver 已关闭 ❌

graph.invoke(...)

✅ 正确示例（脚本 / demo）

with PostgresSaver.from_conn_string(DB_URI) as saver:
    graph = builder.compile(checkpointer=saver)
    graph.invoke(...)

✅ 正确示例（服务端 / FastAPI）

# startup

saver = PostgresSaver.from_conn_string(DB_URI).__enter__()
graph = builder.compile(checkpointer=saver)

# request handlers

graph.invoke(...)

def shutdown():
    saver.__exit__(None, None, None)

⸻

六、每个 Saver 都会创建新连接 / 新连接池吗？

✅ 是的（这是设计行为）

Saver 类型 内部资源 是否共享
InMemorySaver 无 N/A
PostgresSaver 单连接 ❌
AsyncPostgresSaver asyncpg pool ❌

等价理解

new Saver()  ⇒  new DB connection / new pool

⸻

七、为什么 LangGraph 不提供“全局共享连接池”？

这是一个刻意的设计选择。

1️⃣ 生命周期清晰
 • 谁创建，谁关闭
 • 避免隐式全局状态

2️⃣ 并发 / event loop 安全
 • async pool 不能跨 event loop 共享
 • 隐式共享会导致难以调试的 bug

3️⃣ Graph 的可组合性

LangGraph 的核心假设：

graph 是可复制、可测试、可部署的独立单元

共享全局池会破坏这个假设。

⸻

八、常见致命错误（一定要避免）

❌ 错误 1：每个请求创建一个 Saver

async def handler():
    async with AsyncPostgresSaver.from_conn_string(DB_URI) as saver:
        graph = compile(...)
        await graph.astream(...)

后果：
 • 每个请求一个 pool
 • PostgreSQL 很快被打死

⸻

❌ 错误 2：以为 Saver 会自动提供“对话记忆”

Saver 只是存 checkpoint

真正的 key 是：

config = {
    "configurable": {
        "thread_id": "chat-123"
    }
}

 • same graph
 • same saver
 • same thread_id

👉 state 才会自动恢复

⸻

九、什么时候用哪种 Saver？

场景 推荐
本地调试 InMemorySaver
Notebook / Demo InMemorySaver
FastAPI 多用户 AsyncPostgresSaver
多 worker / k8s AsyncPostgresSaver
需要 rewind / audit Postgres / AsyncPostgres

⸻

十、一句话总结（核心记忆点）

LangGraph 的 PostgresSaver / AsyncPostgresSaver 是「每实例一连接 / 一连接池」，不会自动共享，必须显式管理生命周期。

graph 可以复用，saver 不能随便 new。

⸻

（完）
