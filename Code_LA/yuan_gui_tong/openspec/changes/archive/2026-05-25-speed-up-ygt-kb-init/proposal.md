## Why

园规通知识库初始化时，用户点击"初始化规范库"后只看到一个静态 spinner "正在初始化规范库，请稍候..."，持续数分钟无反馈。首次运行还需下载 BGE-M3 (~2GB) 和 PaddleOCR 模型，用户不知道系统在做什么、卡在哪一步、还要等多久。需要细粒度进度反馈 + 必要的速度优化。

## What Changes

- **新增** 分步进度展示：解析 PDF → 切分条款 → 向量化 → 导入 ChromaDB，每步显示当前进度
- **新增** 模型预缓存：首次启动时检查并预下载 BGE-M3 模型，避免初始化中途超时
- **优化** OCR 兜底：缺字 PDF 先跳过 OCR，标记为"待处理"，不阻塞初始化流程
- **优化** 旧 ChromaDB 数据清理：初始化前提示是否覆盖，避免无效工作

## Capabilities

### New Capabilities
- `kb-init-progress`: 知识库初始化分步进度展示
- `model-preload`: BGE-M3 模型预检查和下载

### Modified Capabilities
- 无（现有 capability 行为不变）
