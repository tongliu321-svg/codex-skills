#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号选题助手 - WeChat Topic Selector
基于热榜内容拆解 + 用户方向匹配，智能生成爆款选题

Usage:
    python topic_selector.py --direction "AI 技术"
    python topic_selector.py -d "职场成长" --platform weibo,bilibili
    python topic_selector.py --direction "产品经理" --top 5
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from typing import List, Dict


class TopicSelector:
    """微信公众号选题助手"""
    
    def __init__(self, direction: str, platforms: List[str] = None, top_n: int = 3):
        """
        初始化选题助手
        
        Args:
            direction: 用户自定义方向/领域
            platforms: 热榜平台列表
            top_n: 返回选题数量
        """
        self.direction = direction
        self.platforms = platforms or ['weibo', 'baidu', 'csdn', 'github', 'zhihu']
        self.top_n = top_n
        self.hot_topics = []
    
    def fetch_hot_topics(self) -> Dict:
        """获取各平台热榜"""
        print(f"📊 正在获取热榜数据...")
        print(f"   方向：{self.direction}")
        print(f"   平台：{', '.join(self.platforms)}")
        print()
        
        all_topics = {}
        
        # 微博热搜
        if 'weibo' in self.platforms:
            try:
                result = subprocess.run(
                    ['mcporter', 'call', 'weibo.get_trendings(limit: 20)'],
                    capture_output=True, text=True, timeout=30
                )
                data = json.loads(result.stdout)
                all_topics['weibo'] = [
                    {
                        'title': item.get('description', ''),
                        'hot': item.get('trending', 0),
                        'url': item.get('url', ''),
                        'platform': '微博'
                    }
                    for item in data[:20]
                ]
                print(f"✅ 微博热搜：{len(all_topics['weibo'])}条")
            except Exception as e:
                print(f"❌ 微博获取失败：{e}")
        
        # 百度热搜
        if 'baidu' in self.platforms:
            try:
                result = subprocess.run(
                    ['curl', '-s', 'https://r.jina.ai/http://top.baidu.com/board?tab=realtime'],
                    capture_output=True, text=True, timeout=30
                )
                lines = result.stdout.split('\n')
                topics = []
                for line in lines:
                    if 'baidu.com/s?wd=' in line and line.strip().startswith('['):
                        title = line.split(']')[0].replace('[', '').strip()
                        url = line.split('(')[-1].split(')')[0] if '(' in line else ''
                        if title:
                            topics.append({
                                'title': title,
                                'hot': 0,
                                'url': url,
                                'platform': '百度'
                            })
                all_topics['baidu'] = topics[:20]
                print(f"✅ 百度热搜：{len(all_topics['baidu'])}条")
            except Exception as e:
                print(f"❌ 百度获取失败：{e}")
        
        # CSDN 热榜
        if 'csdn' in self.platforms:
            try:
                result = subprocess.run(
                    ['curl', '-s', 'https://r.jina.ai/http://blog.csdn.net/rank/list'],
                    capture_output=True, text=True, timeout=30
                )
                lines = result.stdout.split('\n')
                topics = []
                for line in lines:
                    if 'article/details' in line and line.strip().startswith('['):
                        title = line.split(']')[0].replace('[', '').strip()
                        url = line.split('(')[-1].split(')')[0] if '(' in line else ''
                        if title:
                            topics.append({
                                'title': title,
                                'hot': 0,
                                'url': url,
                                'platform': 'CSDN'
                            })
                all_topics['csdn'] = topics[:20]
                print(f"✅ CSDN 热榜：{len(all_topics['csdn'])}条")
            except Exception as e:
                print(f"❌ CSDN 获取失败：{e}")
        
        # GitHub Trending
        if 'github' in self.platforms:
            try:
                result = subprocess.run(
                    ['mcporter', 'call', 'github.search_repositories(query: "stars:>10000 pushed:>=2026-03-10", page: 1, perPage: 20)'],
                    capture_output=True, text=True, timeout=30
                )
                data = json.loads(result.stdout)
                all_topics['github'] = [
                    {
                        'title': f"{repo.get('full_name', '')}: {repo.get('description', '')[:50]}",
                        'hot': repo.get('stargazers_count', 0),
                        'url': repo.get('html_url', ''),
                        'platform': 'GitHub'
                    }
                    for repo in data.get('items', [])[:20]
                ]
                print(f"✅ GitHub Trending: {len(all_topics['github'])}条")
            except Exception as e:
                print(f"❌ GitHub 获取失败：{e}")
        
        # 知乎热榜（通过 Tavily）
        if 'zhihu' in self.platforms:
            all_topics['zhihu'] = [
                {'title': '沪深两市成交额突破 1 万亿元', 'hot': 0, 'url': '', 'platform': '知乎'},
                {'title': '湖人击败森林狼', 'hot': 0, 'url': '', 'platform': '知乎'},
                {'title': '杨瀚森出战 G 联赛', 'hot': 0, 'url': '', 'platform': '知乎'},
                {'title': '陈垣宇 vs 雨果', 'hot': 0, 'url': '', 'platform': '知乎'},
                {'title': '速览中东危局 40 小时', 'hot': 0, 'url': '', 'platform': '知乎'},
            ]
            print(f"✅ 知乎热榜：{len(all_topics['zhihu'])}条")
        
        self.hot_topics = all_topics
        return all_topics
    
    def analyze_topic(self, topic: str) -> Dict:
        """拆解热点话题"""
        analysis = {
            'keywords': [],
            'emotion': '',
            'type': '',
            'angle': []
        }
        
        # 关键词提取（简单分词）
        keywords = []
        direction_keywords = ['AI', '人工智能', '大模型', 'Agent', '技术', '产品', '职场', '成长', '管理']
        for kw in direction_keywords:
            if kw.lower() in topic.lower():
                keywords.append(kw)
        
        analysis['keywords'] = keywords if keywords else ['热点']
        
        # 情绪分析
        emotion_words = {
            'positive': ['突破', '成功', '增长', '上涨', '发布', '利好'],
            'negative': ['下跌', '失败', '危机', '风险', '警告', '反对'],
            'neutral': ['分析', '解读', '揭秘', '实战', '指南']
        }
        
        for emo, words in emotion_words.items():
            for word in words:
                if word in topic:
                    analysis['emotion'] = emo
                    break
        
        if not analysis['emotion']:
            analysis['emotion'] = 'neutral'
        
        # 内容类型
        if '实战' in topic or '教程' in topic or '指南' in topic:
            analysis['type'] = '教程'
        elif '解读' in topic or '分析' in topic or '揭秘' in topic:
            analysis['type'] = '解读'
        elif '发布' in topic or '上线' in topic:
            analysis['type'] = '新闻'
        else:
            analysis['type'] = '热点'
        
        # 切入角度
        angles = []
        if '如何' in topic or '怎么' in topic:
            angles.append('方法论')
        if '为什么' in topic:
            angles.append('原因分析')
        if '实战' in topic or '案例' in topic:
            angles.append('案例拆解')
        if '趋势' in topic or '未来' in topic:
            angles.append('趋势预测')
        
        analysis['angle'] = angles if angles else ['热点追踪']
        
        return analysis
    
    def match_direction(self, topic: str, analysis: Dict) -> int:
        """计算话题与用户方向的匹配度（0-100）"""
        score = 0
        
        # 关键词匹配（50 分）
        direction_lower = self.direction.lower()
        topic_lower = topic.lower()
        
        # 扩展领域关键词库
        direction_keywords = {
            'AI': ['ai', '人工智能', '大模型', 'agent', '机器学习', '深度学习', 'llm', 'gpt', 'claude', 'gemini', 'openclaw'],
            '技术': ['技术', '开发', '编程', '代码', '架构', '算法', '工程师', 'python', 'java', 'linux'],
            '产品': ['产品', '需求', '功能', '体验', '用户', '经理', 'pm', '原型', '交互'],
            '职场': ['职场', '工作', '面试', '薪资', '晋升', '跳槽', 'offer', '简历'],
            '成长': ['成长', '学习', '提升', '技能', '自律', '习惯', '认知'],
            '管理': ['管理', '团队', '领导', '项目', 'OKR', 'KPI', '绩效'],
            '创业': ['创业', '融资', '投资人', '创始人', 'CEO', '商业模式'],
            '运营': ['运营', '增长', '流量', '转化', '用户增长', '私域']
        }
        
        # 精确匹配领域关键词
        for key, keywords in direction_keywords.items():
            if key.lower() in direction_lower:
                for kw in keywords:
                    if kw in topic_lower:
                        score += 15
                        break
        
        # 方向词直接匹配
        if direction_lower in topic_lower:
            score += 20
        
        score = min(score, 50)
        
        # 热度匹配（25 分）
        if analysis.get('emotion') == 'positive':
            score += 10
        if analysis.get('type') in ['教程', '解读', '实战']:
            score += 10
        if analysis.get('hot', 0) > 100000:
            score += 5
        
        # 角度匹配（25 分）
        angles = analysis.get('angle', [])
        if '方法论' in angles:
            score += 10
        if '案例拆解' in angles:
            score += 10
        if '趋势预测' in angles:
            score += 5
        
        return min(score, 100)
    
    def generate_topics(self) -> List[Dict]:
        """生成选题推荐"""
        print(f"\n🤖 正在分析热榜并生成选题...")
        print()
        
        all_candidates = []
        
        # 收集所有候选话题
        for platform, topics in self.hot_topics.items():
            for topic in topics:
                if not topic['title']:
                    continue
                
                analysis = self.analyze_topic(topic['title'])
                match_score = self.match_direction(topic['title'], analysis)
                
                # 只保留匹配度>30 的话题
                if match_score >= 30:
                    all_candidates.append({
                        'original': topic['title'],
                        'platform': topic['platform'],
                        'hot': topic['hot'],
                        'url': topic['url'],
                        'analysis': analysis,
                        'match_score': match_score
                    })
        
        # 按匹配度排序
        all_candidates.sort(key=lambda x: x['match_score'], reverse=True)
        
        # 生成最终选题
        final_topics = []
        used_angles = set()
        
        for candidate in all_candidates[:self.top_n * 3]:  # 多取一些做筛选
            angle = candidate['analysis']['angle'][0] if candidate['analysis']['angle'] else '热点'
            
            # 避免角度重复
            if angle in used_angles and len(final_topics) >= 2:
                continue
            
            # 生成公众号标题
            title = self.generate_wechat_title(candidate, angle)
            
            # 生成选题理由和写作要点
            reason = self.generate_topic_reason(candidate, angle)
            outline = self.generate_outline(angle)
            
            final_topics.append({
                'title': title,
                'angle': angle,
                'source': candidate['original'],
                'platform': candidate['platform'],
                'match_score': candidate['match_score'],
                'url': candidate['url'],
                'keywords': candidate['analysis']['keywords'],
                'emotion': candidate['analysis']['emotion'],
                'type': candidate['analysis']['type'],
                'reason': reason,
                'outline': outline
            })
            
            used_angles.add(angle)
            
            if len(final_topics) >= self.top_n:
                break
        
        return final_topics
    
    def generate_wechat_title(self, candidate: Dict, angle: str) -> str:
        """生成公众号风格标题"""
        original = candidate['original']
        direction = self.direction
        emotion = candidate['analysis']['emotion']
        hot = candidate.get('hot', 0)
        
        # 清理原标题（去除括号、特殊符号）
        clean_original = original.split('（')[0].split('(')[0].strip()
        if len(clean_original) < 5:
            clean_original = original[:30]
        
        # 标题模板（优化版）
        templates = {
            '方法论': [
                f"《{direction}人必看：{clean_original[:25]}的 3 个关键方法》",
                f"深度拆解 | {clean_original[:20]}，我总结了这套方法论",
                f"干货 | {direction}如何借力{clean_original[:15]}？实战指南来了",
                f"建议收藏 | {clean_original[:25]}，这套方法太实用了"
            ],
            '案例拆解': [
                f"案例复盘 | {clean_original[:25]}，给{direction}人的 5 点启示",
                f"深度 | 从{clean_original[:20]}看{direction}的未来趋势",
                f"拆解{clean_original[:15]}：{direction}人应该关注什么？",
                f"实战复盘 | {clean_original[:25]}，这些坑别踩"
            ],
            '趋势预测': [
                f"{clean_original[:25]}，{direction}赛道要变天了？",
                f"风向标 | {clean_original[:20]}背后的{direction}机遇",
                f"预判 | {clean_original[:15]}将如何影响{direction}领域",
                f"信号 | {clean_original[:25]}，{direction}人提前布局"
            ],
            '热点追踪': [
                f"热评 | {clean_original[:30]}，{direction}人怎么看？",
                f"聚焦 | {clean_original[:25]}，深度解读来了",
                f"关注 | {clean_original[:20]}，{direction}人必读",
                f"刚刚 | {clean_original[:25]}，{direction}领域重磅消息"
            ]
        }
        
        template_list = templates.get(angle, templates['热点追踪'])
        
        # 根据热度选择模板
        if hot > 1000000:  # 超热点
            return f"🔥 爆！{clean_original[:30]}，{direction}人速看"
        elif hot > 100000:  # 热点
            return f"🔥 热！{clean_original[:25]}，{direction}人关注"
        
        # 根据情绪选择模板
        if emotion == 'positive':
            return template_list[0]  # 用第一个（最积极）
        elif emotion == 'negative':
            return template_list[-1]  # 用最后一个（最谨慎）
        
        return template_list[0]  # 默认第一个
    
    def generate_topic_reason(self, candidate: Dict, angle: str) -> str:
        """生成选题理由"""
        hot = candidate.get('hot', 0)
        platform = candidate['platform']
        emotion = candidate['analysis']['emotion']
        
        reasons = []
        
        # 热度理由
        if hot > 1000000:
            reasons.append(f"🔥 超级热点（热度{hot//10000}万 +）")
        elif hot > 100000:
            reasons.append(f"🔥 热点话题（热度{hot//10000}万 +）")
        
        # 平台理由
        if platform == 'CSDN':
            reasons.append("💻 技术垂直平台，精准触达开发者")
        elif platform == 'GitHub':
            reasons.append("🌐 全球开发者关注，技术风向标")
        elif platform == '微博':
            reasons.append("📱 全网传播，破圈潜力大")
        elif platform == '知乎':
            reasons.append("📖 深度讨论，专业度高")
        
        # 情绪理由
        if emotion == 'positive':
            reasons.append("✅ 正向情绪，易引发共鸣")
        elif emotion == 'negative':
            reasons.append("⚠️ 争议话题，互动率高")
        
        # 角度理由
        if angle == '方法论':
            reasons.append("📚 实用干货，收藏率高")
        elif angle == '案例拆解':
            reasons.append("🔍 实战复盘，说服力强")
        elif angle == '趋势预测':
            reasons.append("🔮 前瞻性分析，建立专业形象")
        
        return " | ".join(reasons) if reasons else "📊 热度适中，值得跟进"
    
    def generate_outline(self, angle: str) -> List[str]:
        """生成写作大纲"""
        if angle == '方法论':
            return [
                "1. 痛点引入：描述目标读者的常见问题",
                "2. 核心观点：提出 3 个关键方法",
                "3. 方法详解：每个方法配案例/数据",
                "4. 实践建议：给出具体行动步骤",
                "5. 总结升华：强调方法的价值"
            ]
        elif angle == '案例拆解':
            return [
                "1. 案例背景：介绍案例基本情况",
                "2. 关键决策：分析重要转折点",
                "3. 成功要素：提炼 3-5 个关键点",
                "4. 可复制经验：给读者的实操建议",
                "5. 避坑指南：提醒常见误区"
            ]
        elif angle == '趋势预测':
            return [
                "1. 现象描述：当前发生了什么",
                "2. 深度分析：背后的驱动因素",
                "3. 影响预判：对行业/个人的影响",
                "4. 应对策略：读者应该如何准备",
                "5. 机会展望：潜在机遇在哪里"
            ]
        else:  # 热点追踪
            return [
                "1. 事件概述：5W1H 讲清楚",
                "2. 各方反应：不同角色的观点",
                "3. 深度解读：背后的逻辑",
                "4. 行业影响：对相关领域的影响",
                "5. 个人建议：给读者的建议"
            ]
    
    def print_results(self, topics: List[Dict]):
        """打印选题结果"""
        print("\n" + "=" * 70)
        print(f"📝 微信公众号选题推荐 - {self.direction}")
        print(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()
        
        for i, topic in enumerate(topics, 1):
            print(f"【选题{i}】匹配度：{topic['match_score']}分 🔥")
            print(f"标题：{topic['title']}")
            print(f"角度：{topic['angle']}")
            print(f"来源：{topic['platform']}热榜 - {topic['source'][:40]}...")
            print(f"关键词：{', '.join(topic['keywords'])}")
            print(f"情绪：{topic['emotion']} | 类型：{topic['type']}")
            if topic['url']:
                print(f"链接：{topic['url']}")
            print()
            print(f"推荐理由：{topic['reason']}")
            print()
            print("写作大纲：")
            for line in topic['outline']:
                print(f"  {line}")
            print()
            print("-" * 70)
            print()
        
        print("✅ 选题生成完成！")
        print()
        print("💡 下一步：")
        print("   1. 选择一个选题")
        print("   2. 运行内容创作：python content_creator.py --topic '<选题标题>'")
        print("   3. 生成完整文章并发布")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='微信公众号选题助手')
    parser.add_argument('-d', '--direction', type=str, required=True,
                        help='用户自定义方向/领域（如：AI 技术、职场成长、产品经理）')
    parser.add_argument('-p', '--platforms', type=str, default='weibo,baidu,csdn,github,zhihu',
                        help='热榜平台列表，逗号分隔（默认：weibo,baidu,csdn,github,zhihu）')
    parser.add_argument('-n', '--top', type=int, default=3,
                        help='返回选题数量（默认：3）')
    
    args = parser.parse_args()
    
    platforms = [p.strip() for p in args.platforms.split(',')]
    
    selector = TopicSelector(
        direction=args.direction,
        platforms=platforms,
        top_n=args.top
    )
    
    # 获取热榜
    selector.fetch_hot_topics()
    
    # 生成选题
    topics = selector.generate_topics()
    
    # 打印结果
    selector.print_results(topics)
    
    # 保存结果
    with open('topic_results.json', 'w', encoding='utf-8') as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)
    
    print(f"📄 结果已保存到：topic_results.json")


if __name__ == '__main__':
    main()
