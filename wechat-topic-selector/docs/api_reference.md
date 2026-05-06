# API 参考文档

## TopicSelector 类

### 初始化

```python
selector = TopicSelector(
    direction="AI 技术",      # 用户方向/领域
    platforms=['weibo', 'baidu', 'csdn'],  # 热榜平台
    top_n=3                   # 返回选题数量
)
```

### 方法

#### fetch_hot_topics()
获取各平台热榜

```python
topics = selector.fetch_hot_topics()
```

**返回**: Dict，包含各平台热榜数据

#### analyze_topic(topic: str)
拆解热点话题

```python
analysis = selector.analyze_topic("2026 全球大模型深度对决")
```

**返回**:
```python
{
    'keywords': ['大模型', 'AI'],
    'emotion': 'neutral',
    'type': '解读',
    'angle': ['方法论']
}
```

#### match_direction(topic: str, analysis: Dict)
计算匹配度（0-100 分）

```python
score = selector.match_direction("AI 技术", analysis)
```

**返回**: int (0-100)

#### generate_wechat_title(candidate: Dict, angle: str)
生成公众号标题

```python
title = selector.generate_wechat_title(candidate, '方法论')
```

**返回**: str（公众号风格标题）

#### generate_topic_reason(candidate: Dict, angle: str)
生成选题理由

```python
reason = selector.generate_topic_reason(candidate, '方法论')
```

**返回**: str（推荐理由）

#### generate_outline(angle: str)
生成写作大纲

```python
outline = selector.generate_outline('方法论')
```

**返回**: List[str]（5 步写作框架）

#### generate_topics()
生成选题推荐

```python
topics = selector.generate_topics()
```

**返回**: List[Dict]（选题列表）

#### print_results(topics: List[Dict])
打印选题结果

```python
selector.print_results(topics)
```

---

## 命令行参数

```bash
python3 topic_selector.py [OPTIONS]
```

**参数**:
- `-d, --direction TEXT` - 用户方向/领域（必填）
- `-p, --platforms TEXT` - 热榜平台列表（默认：weibo,baidu,csdn,github,zhihu）
- `-n, --top INT` - 返回选题数量（默认：3）

**示例**:
```bash
python3 topic_selector.py -d "AI 技术"
python3 topic_selector.py -d "职场成长" -p weibo,baidu
python3 topic_selector.py -d "产品经理" -n 5
```

---

## 输出格式

### 控制台输出

```
======================================================================
📝 微信公众号选题推荐 - AI 技术
生成时间：2026-03-13 17:05:46
======================================================================

【选题 1】匹配度：85 分 🔥
标题：《AI 技术人必看：2026 全球大模型深度对决的 3 个关键方法》
角度：方法论
来源：CSDN 热榜 - 2026 全球大模型深度对决...
关键词：AI, 大模型，技术
情绪：neutral | 类型：解读
链接：https://blog.csdn.net/xxx/article/details/xxx

推荐理由：💻 技术垂直平台，精准触达开发者 | 📚 实用干货，收藏率高

写作大纲：
  1. 痛点引入：描述目标读者的常见问题
  2. 核心观点：提出 3 个关键方法
  3. 方法详解：每个方法配案例/数据
  4. 实践建议：给出具体行动步骤
  5. 总结升华：强调方法的价值

----------------------------------------------------------------------
```

### JSON 输出

保存到 `topic_results.json`：

```json
[
  {
    "title": "《AI 技术人必看：...》",
    "angle": "方法论",
    "source": "2026 全球大模型深度对决...",
    "platform": "CSDN",
    "match_score": 85,
    "url": "https://...",
    "keywords": ["AI", "大模型"],
    "emotion": "neutral",
    "type": "解读",
    "reason": "💻 技术垂直平台...",
    "outline": [...]
  }
]
```

---

## 错误处理

所有方法都包含错误处理，获取失败时会输出错误信息但不会中断程序。

```python
try:
    selector.fetch_hot_topics()
except Exception as e:
    print(f"❌ 热榜获取失败：{e}")
```

---

## 性能优化建议

1. **批量获取**: 一次性获取所有平台热榜
2. **缓存结果**: 将结果保存到 JSON，避免重复请求
3. **定时任务**: 使用 Cron Job 定时获取，避免频繁调用

---

## 更新日志

### v1.1.0 (2026-03-13)
- ✨ 优化标题生成逻辑
- ✨ 增强匹配算法（50+25+25 分制）
- ✨ 新增选题理由生成
- ✨ 新增写作大纲生成
- ✨ 扩展领域关键词库（8 大领域）
- 🐛 修复重复代码 bug

### v1.0.0 (2026-03-13)
- ✨ 初始版本发布
- 📊 支持 5 大平台热榜获取
- 🤖 智能匹配打分
- 📝 公众号标题生成
