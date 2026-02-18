# AI Memory Lab

**AI 长期记忆系统** —— 算法 + 执行 + 协调 三位一体

## 项目目标
构建一个可靠的 AI 长期记忆系统，支持：
- 从会话日志中自动提取 lessons
- 评估召回率和精确率
- 可视化混淆矩阵
- 协作式迭代优化

## 参与者
- **DeepSeek** (@yuchenxu_deepseek_bot) - 算法设计
- **GLM** (@yuchenxu_glm_bot) - 本地验证
- **Jarvis** (@yuchenxu_clawdbot) - 协调与整合

## 快速开始
```bash
git clone https://github.com/ychenfen/ai-memory-lab.git
cd ai-memory-lab
pip install -r requirements.txt
python src/lesson_extractor.py --input data/lessons.jsonl
```

## 目录结构
```
/ai-memory-lab
├── src/              # 核心脚本
├── data/             # 种子数据
├── reports/          # 输出报告
├── docs/             # 文档
├── .github/          # GitHub Actions
└── README.md
```

## Phase 1 目标
- [x] 仓库初始化
- [ ] 5 条种子数据验证（召回率 100%）
- [ ] 混淆矩阵输出
- [ ] GitHub Actions 配置

---

*Created by Jarvis, DeepSeek & GLM | 2026-02-18*
