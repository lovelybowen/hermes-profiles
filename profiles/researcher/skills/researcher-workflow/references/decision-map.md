# 研究员工作流 - 决策图

```mermaid
graph TD
    START([Orchestrator 分配任务]) --> Phase1[阶段 1：接收任务]
    Phase1 --> Phase1_Work[将简报重述为 SCOPE.md]
    Phase1_Work --> Phase2[阶段 2：收集研究资料]
    
    Phase2 --> Phase2_Work["执行 groktocrawl 研究<br/>(agent → search → scrape → browser)"]
    Phase2_Work --> Phase3[阶段 3：评估缺口]
    
    Phase3 --> GapCheck{应用三问模型}
    GapCheck -->|范围内、改变结论、增加深度| Recursed[递归：完整或定向研究]
    GapCheck -->|范围内、不改变结论、增加深度| RecurseLight[递归：轻量研究]
    GapCheck -->|范围内、仅增加材料数量| StopGap[记录为范围外]
    GapCheck -->|范围外| StopGap
    
    Recursed --> Phase2
    RecurseLight --> Phase2
    
    StopGap --> Phase4[阶段 4：构建金字塔]
    
    Phase4 --> Layer3[组装第 3 层：详细档案]
    Layer3 --> Layer2[组装第 2 层：分析集合]
    Layer2 --> Layer1[组装第 1 层：管理摘要]
    Layer1 --> Verify[验证交叉引用链接]
    
    Verify --> Phase5[阶段 5：交付发现]
    Phase5 --> Done([向 orchestrator 返回路径])
    
    style START fill:#4a90d9,color:#fff
    style Done fill:#4a90d9,color:#fff
    style GapCheck fill:#e6a817,color:#000
    style Phase1 fill:#2d6a4f,color:#fff
    style Phase2 fill:#2d6a4f,color:#fff
    style Phase3 fill:#2d6a4f,color:#fff
    style Phase4 fill:#2d6a4f,color:#fff
    style Phase5 fill:#2d6a4f,color:#fff
```

## 流程说明

- 阶段 1、2、4、5 必须执行且顺序固定。
- 阶段 3 是唯一分支点，可以返回阶段 2 进行递归调查。
- 递归强度从轻量（仅搜索）到完整研究（运行 Agent）不等。
- 最多递归两轮，之后必须升级处理。
- 产物累积在 `<artifacts-root>/<mission-slug>/`。
- 金字塔自底向上构建：档案 → 分析 → 摘要。
