"""
rag2 数据集
===========
与逻辑代码剥离：PARENT_DOCS / SCENE_VARIANTS / TEST_SET / STOPWORDS / TERM_MAP / DEMO_DAG
"""

# ============ 1. 父块：完整范式（不向量化，只存）============
PARENT_DOCS = [
    {
        "id": "P_crm",
        "title": "团队 CRM / 客户跟进范式",
        "plan_steps": [
            "数据建模:customers / follow_ups / team_members 三张表",
            "认证:Supabase Auth 邮箱登录",
            "权限:RLS 按 team_id 隔离",
            "页面:客户列表、客户详情、跟进时间线、新增跟进表单",
            "逻辑:跟进状态流转(待跟进→跟进中→已成交)",
        ],
        "pitfalls": ["忘记做 team 维度隔离", "跟进记录没做软删除"],
        "metadata": {
            "domain": "CRM", "complexity": "中",
            "multi_user": True, "need_auth": True, "entity_count": 3,
        },
    },
    {
        "id": "P_ecommerce",
        "title": "电商在线商城范式",
        "plan_steps": [
            "数据建模:products / orders / cart_items 表",
            "商品列表/详情页", "购物车逻辑", "下单流程 + 支付接入",
        ],
        "pitfalls": ["库存并发扣减", "支付回调幂等性"],
        "metadata": {
            "domain": "Ecommerce", "complexity": "高",
            "multi_user": True, "need_auth": True, "entity_count": 3,
        },
    },
    {
        "id": "P_admin",
        "title": "多角色后台管理范式",
        "plan_steps": [
            "数据建模:users / roles / permissions 表",
            "RBAC 权限模型", "通用数据表格 CRUD", "角色与权限管理页",
        ],
        "pitfalls": ["权限粒度过细难维护", "前后端权限要一致"],
        "metadata": {
            "domain": "Admin", "complexity": "中",
            "multi_user": True, "need_auth": True, "entity_count": 3,
        },
    },
    {
        "id": "P_blog",
        "title": "个人博客 / 内容发布范式",
        "plan_steps": [
            "数据建模:posts / categories / tags 表",
            "Markdown 编辑器", "文章列表/详情页", "分类标签筛选",
        ],
        "pitfalls": ["SEO 元信息缺失", "Markdown XSS 防护"],
        "metadata": {
            "domain": "Blog", "complexity": "低",
            "multi_user": False, "need_auth": True, "entity_count": 3,
        },
    },
    {
        "id": "P_todo",
        "title": "个人任务待办清单范式",
        "plan_steps": [
            "数据建模:tasks 表", "任务 CRUD",
            "完成状态切换", "截止日期与提醒",
        ],
        "pitfalls": ["提醒时区问题"],
        "metadata": {
            "domain": "Tool", "complexity": "低",
            "multi_user": False, "need_auth": False, "entity_count": 1,
        },
    },
    {
        "id": "P_ticket",
        "title": "客服工单系统范式",
        "plan_steps": [
            "数据建模:tickets / agents 表", "工单提交表单",
            "分配逻辑", "状态流转:待处理→处理中→已解决",
        ],
        "pitfalls": ["工单分配负载不均", "状态变更审计"],
        "metadata": {
            "domain": "Support", "complexity": "中",
            "multi_user": True, "need_auth": True, "entity_count": 2,
        },
    },
    {
        "id": "P_booking",
        "title": "预约预订系统范式",
        "plan_steps": [
            "数据建模:bookings / slots 表", "日历选时间段",
            "预约确认流程", "防重叠校验",
        ],
        "pitfalls": ["并发预约同一时段", "时区与跨天处理"],
        "metadata": {
            "domain": "Booking", "complexity": "中",
            "multi_user": True, "need_auth": True, "entity_count": 2,
        },
    },
    {
        "id": "P_inventory",
        "title": "库存进销存管理范式",
        "plan_steps": [
            "数据建模:products / stock_records 表",
            "入库/出库表单", "库存实时统计", "低库存预警",
        ],
        "pitfalls": ["库存负数", "批量操作事务"],
        "metadata": {
            "domain": "Inventory", "complexity": "中",
            "multi_user": True, "need_auth": True, "entity_count": 2,
        },
    },
    {
        "id": "P_chat",
        "title": "实时通讯 / 在线聊天范式",
        "plan_steps": [
            "数据建模:users / conversations / messages 表",
            "认证:Supabase Auth + JWT",
            "实时通道:WebSocket 或 Supabase Realtime",
            "页面:会话列表、聊天窗口、联系人搜索",
            "逻辑:消息已读/未读、输入状态提示、文件分享",
        ],
        "pitfalls": ["消息时序乱序", "WebSocket 断连重连状态丢失", "大量并发连接扩缩容"],
        "metadata": {
            "domain": "Chat", "complexity": "高",
            "multi_user": True, "need_auth": True, "entity_count": 3,
        },
    },
    {
        "id": "P_social",
        "title": "社区 / 社交动态流范式",
        "plan_steps": [
            "数据建模:users / posts / comments / likes / follows 表",
            "认证:Supabase Auth 邮箱登录",
            "页面:动态流首页、个人主页、帖子详情",
            "逻辑:点赞/评论/关注关系、Feed 聚合与排序",
        ],
        "pitfalls": ["Feed 流 N+1 查询", "点赞计数的最终一致性", "内容审核与垃圾过滤"],
        "metadata": {
            "domain": "Social", "complexity": "高",
            "multi_user": True, "need_auth": True, "entity_count": 5,
        },
    },
    {
        "id": "P_lms",
        "title": "在线课程 / 学习管理范式",
        "plan_steps": [
            "数据建模:users / courses / lessons / progress / quizzes 表",
            "认证:支持学员和讲师两种角色",
            "页面:课程目录、视频播放页、测验答题页、学习进度看板",
            "逻辑:课时解锁、自动判分、结课证书生成",
        ],
        "pitfalls": ["视频防盗链", "进度同步覆盖冲突", "测验答题防作弊"],
        "metadata": {
            "domain": "LMS", "complexity": "高",
            "multi_user": True, "need_auth": True, "entity_count": 5,
        },
    },
    {
        "id": "P_kanban",
        "title": "看板 / 项目任务管理范式",
        "plan_steps": [
            "数据建模:projects / tasks / columns / members 表",
            "认证:Supabase Auth 邮箱登录",
            "页面:项目列表、看板拖拽视图、任务详情弹窗",
            "逻辑:拖拽排序持久化、任务分配、截止日期提醒",
        ],
        "pitfalls": ["拖拽排序并发冲突", "大量任务时列表性能", "看板列数量增长失控"],
        "metadata": {
            "domain": "Kanban", "complexity": "中",
            "multi_user": True, "need_auth": True, "entity_count": 4,
        },
    },
    {
        "id": "P_analytics",
        "title": "数据看板 / BI 分析范式",
        "plan_steps": [
            "数据建模:dashboards / charts / data_sources 表",
            "认证:Supabase Auth 邮箱登录",
            "页面:看板列表、图表编辑器、数据源配置",
            "逻辑:SQL/API 数据查询、图表渲染、定时刷新与导出",
        ],
        "pitfalls": ["大查询拖垮数据库", "图表渲染内存溢出", "数据源凭证安全存储"],
        "metadata": {
            "domain": "Analytics", "complexity": "高",
            "multi_user": True, "need_auth": True, "entity_count": 3,
        },
    },
    {
        "id": "P_subscription",
        "title": "会员订阅 / 付费墙范式",
        "plan_steps": [
            "数据建模:users / plans / subscriptions / payments 表",
            "认证:Supabase Auth 邮箱登录",
            "支付:Stripe/Paddle 集成、Webhook 回调处理",
            "页面:定价页、订阅管理页、账单历史",
            "逻辑:套餐升降级 proration、试用期自动转付费、过期降级",
        ],
        "pitfalls": ["Webhook 幂等性", "Proration 边界计算", "支付回调超时重试"],
        "metadata": {
            "domain": "Subscription", "complexity": "中",
            "multi_user": False, "need_auth": True, "entity_count": 4,
        },
    },
]

# ============ 2. 子块：多视角场景描述（只有 content 入向量库）============
SCENE_VARIANTS = {
    "P_crm": [
        "团队协作的客户关系管理系统,记录客户信息和跟进状态",
        "销售人员跟进客户、记录沟通历史与成交进展",
        "多人共享维护的客户资料库与跟进时间线",
    ],
    "P_ecommerce": [
        "在线商城,商品展示购物车下单支付完整流程",
        "电商网站,用户浏览商品、加购物车、结账付款",
        "面向消费者的在线零售平台,含商品订单支付",
    ],
    "P_admin": [
        "后台管理系统,多角色权限控制与数据增删改查",
        "企业内部管理平台,按角色分配不同操作权限",
        "RBAC 权限模型的管理后台,支持多角色协作",
    ],
    "P_blog": [
        "个人博客与内容发布站点,撰写文章并展示",
        "Markdown 写作发布平台,支持分类与标签",
        "面向读者的文章发布与阅读站点",
    ],
    "P_todo": [
        "个人任务待办清单工具,记录与完成任务",
        "个人事项管理,创建任务、打勾完成、设提醒",
        "轻量待办清单,跟踪每日要做的事情",
    ],
    "P_ticket": [
        "客服工单系统,客户提单、客服处理与跟踪",
        "工单提交与处理流程,分配给客服跟进解决",
        "技术支持工单平台,从提交到解决的状态跟踪",
    ],
    "P_booking": [
        "预约预订系统,用户选时间段进行预约",
        "在线预约平台,日历选时间、确认预订",
        "时间段预订与防冲突的预约管理",
    ],
    "P_inventory": [
        "库存进销存管理,商品入库出库与实时统计",
        "仓库存货管理,跟踪入库、出库与库存量",
        "商品库存系统,管理进货、出货与剩余数量",
    ],
    "P_chat": [
        "多人实时聊天通讯平台,支持文字消息和文件分享",
        "在线即时通讯系统,会话列表、消息已读和输入状态",
        "WebSocket 驱动的实时消息应用,支持群聊和私聊",
    ],
    "P_social": [
        "社区社交平台,用户发帖、点赞、评论和关注动态流",
        "内容社区,用户可以发布动态、互动和查看关注人 feed",
        "社交媒体应用,支持帖子互动和个性化信息流",
    ],
    "P_lms": [
        "在线课程平台,学员选课、看视频、做测验和查进度",
        "学习管理系统,支持课程发布、课时管理和学员进度追踪",
        "教育平台,讲师上传课程内容、学员完成学习并获取证书",
    ],
    "P_kanban": [
        "看板项目管理工具,拖拽任务卡在不同列之间流转",
        "项目任务协作平台,支持分列管理、任务分配与截止日期",
        "团队看板应用,可视化任务流从待办到完成的状态迁移",
    ],
    "P_analytics": [
        "数据分析看板平台,连接数据源并生成可视化图表",
        "BI 分析工具,用户创建图表和仪表盘来监控业务指标",
        "数据可视化系统,支持 SQL 查询、图表渲染与定时报表",
    ],
    "P_subscription": [
        "会员订阅付费系统,用户选套餐、在线支付和管理订阅",
        "SaaS 订阅平台,支持多档套餐、试用期和自动续费",
        "付费墙服务,控制内容访问权限、处理订阅生命周期",
    ],
}

# ============ 3. 测试集（含难度分层）============
# difficulty: easy=完整句子+明确领域词 / medium=口语绕圈表达 / hard=单字query+边界混淆
TEST_SET = [
    # ———————— easy（16 条）：完整句子，有明确领域关键词 ————————
    {"raw": "帮我做个能让团队记录客户跟进情况的小工具", "answer": "P_crm", "difficulty": "easy"},
    {"raw": "我想搞一个卖东西的网站,能下单付款那种", "answer": "P_ecommerce", "difficulty": "easy"},
    {"raw": "做个能管不同用户权限的后台", "answer": "P_admin", "difficulty": "easy"},
    {"raw": "弄个可以写文章发出去的地方", "answer": "P_blog", "difficulty": "easy"},
    {"raw": "整个记事情的清单,能打勾那种", "answer": "P_todo", "difficulty": "easy"},
    {"raw": "客户有问题能提单子,我们这边处理跟进", "answer": "P_ticket", "difficulty": "easy"},
    {"raw": "搞个让人选时间来预约的系统", "answer": "P_booking", "difficulty": "easy"},
    {"raw": "管仓库进货出货还有剩多少的东西", "answer": "P_inventory", "difficulty": "easy"},
    {"raw": "做个销售团队跟进客户、看进展的玩意儿", "answer": "P_crm", "difficulty": "easy"},
    {"raw": "我要一个网店,客人能加购物车结账", "answer": "P_ecommerce", "difficulty": "easy"},
    # —— v2 新范式 ——
    {"raw": "做个能跟人实时发消息聊天的东西", "answer": "P_chat", "difficulty": "easy"},
    {"raw": "搞个类似小红书的社区,能发帖点赞关注", "answer": "P_social", "difficulty": "easy"},
    {"raw": "做个在线网课平台,老师上传视频学生看", "answer": "P_lms", "difficulty": "easy"},
    {"raw": "做一个拖拽任务的看板,像 Trello 那种", "answer": "P_kanban", "difficulty": "easy"},
    {"raw": "弄个数据看板,把数据库里的数画成图表", "answer": "P_analytics", "difficulty": "easy"},
    {"raw": "做个会员订阅付费的功能,不同套餐按月收钱", "answer": "P_subscription", "difficulty": "easy"},
    # ———————— hard（12 条）：单字 query + 边界混淆 ————————
    {"raw": "聊天", "answer": "P_chat", "difficulty": "hard"},
    {"raw": "社交", "answer": "P_social", "difficulty": "hard"},
    {"raw": "上课", "answer": "P_lms", "difficulty": "hard"},
    {"raw": "看板", "answer": "P_kanban", "difficulty": "hard"},
    {"raw": "报表", "answer": "P_analytics", "difficulty": "hard"},
    {"raw": "付费", "answer": "P_subscription", "difficulty": "hard"},
    {"raw": "做个能提交工单然后有人处理的东西", "answer": "P_ticket", "difficulty": "hard"},
    {"raw": "我们团队需要分工干活,能看到每件事谁在做", "answer": "P_kanban", "difficulty": "hard"},
    {"raw": "搞个能预定会议室的东西", "answer": "P_booking", "difficulty": "hard"},
    {"raw": "帮销售看他的客户群和最近跟进情况", "answer": "P_crm", "difficulty": "hard"},
    {"raw": "我要一个后台,不同角色看到不同菜单", "answer": "P_admin", "difficulty": "hard"},
    {"raw": "记录我们仓库里每个东西进出了多少", "answer": "P_inventory", "difficulty": "hard"},
    # ———————— medium（6 条）：口语绕圈表达 ————————
    {"raw": "我们团队内部用,想随时能聊,别发邮件了", "answer": "P_chat", "difficulty": "medium"},
    {"raw": "搞个大家能发东西、互相点赞的平台", "answer": "P_social", "difficulty": "medium"},
    {"raw": "我要卖课,学生买了能看视频还能做测试题", "answer": "P_lms", "difficulty": "medium"},
    {"raw": "帮团队管理任务,能看到每个人在干什么", "answer": "P_kanban", "difficulty": "medium"},
    {"raw": "老板想看数据,能不能把 SQL 结果画成图", "answer": "P_analytics", "difficulty": "medium"},
    {"raw": "我想收会员费,不同等级不同权益那种", "answer": "P_subscription", "difficulty": "medium"},
    # ———————— multi（8 条）：一句话涵盖多个意图 ————————
    {"raw": "搞个既能管客户又能处理工单的系统", "answers": ["P_crm", "P_ticket"], "difficulty": "multi"},
    {"raw": "做个在线商城同时带个博客发文章", "answers": ["P_ecommerce", "P_blog"], "difficulty": "multi"},
    {"raw": "帮销售团队管理任务看板", "answers": ["P_crm", "P_kanban"], "difficulty": "multi"},
    {"raw": "我想看报表数据也要能管理库存", "answers": ["P_analytics", "P_inventory"], "difficulty": "multi"},
    {"raw": "搞个团队聊天 + 任务看板的东西", "answers": ["P_chat", "P_kanban"], "difficulty": "multi"},
    {"raw": "做个课程平台,学生买课上课还要做测验", "answers": ["P_lms", "P_subscription"], "difficulty": "multi"},
    {"raw": "既要能预约也要能收会员费", "answers": ["P_booking", "P_subscription"], "difficulty": "multi"},
    {"raw": "做个后台管理系统,不同角色不同权限,还要有数据看板", "answers": ["P_admin", "P_analytics"], "difficulty": "multi"},
]

# ============ 4. query 改写 ============
STOPWORDS = ["帮我", "做个", "搞一个", "搞个", "弄个", "整个", "我想", "我要",
             "的小工具", "那种", "玩意儿", "东西", "地方", "系统", "能", "可以",
             "一个", "做", "的", "一下", "那种", "一下", "给我", "来一个",
             "有没有", "怎么样", "想想", "这么", "那么", "啥"]

TERM_MAP = {
    "客户跟进": "客户关系管理 CRM 销售跟进",
    "跟进客户": "客户关系管理 CRM 销售跟进",
    "团队记录客户": "团队协作 客户关系管理 CRM",
    "卖东西的网站": "电商 在线商城",
    "网店": "电商 在线商城",
    "下单付款": "下单 支付",
    "加购物车结账": "购物车 下单 支付",
    "管不同用户权限": "多角色 权限控制 RBAC 后台管理",
    "写文章发出去": "内容发布 博客 文章",
    "记事情的清单": "任务 待办 清单",
    "打勾": "完成状态",
    "提单子": "工单 提交",
    "处理跟进": "工单 处理 状态跟踪",
    "选时间来预约": "预约 预订 时间段",
    "进货出货": "库存 进销存 入库 出库",
    "剩多少": "库存统计",
    "看进展": "状态跟踪",
    # —— v2 新增领域 ——
    "聊天": "实时通讯 在线聊天 即时消息",
    "发消息": "实时通讯 WebSocket 消息",
    "社交": "社区 社交平台 动态流",
    "发帖": "社区 社交 帖子 动态",
    "点赞": "社交 互动 点赞",
    "关注": "社交 关注 动态流",
    "上课": "在线课程 学习管理 LMS",
    "网课": "在线课程 视频播放 学习管理",
    "视频": "课程 视频播放",
    "测验": "学习管理 测验 自动判分",
    "课程": "在线课程 LMS 学习管理",
    "看板": "看板 项目管理 拖拽",
    "拖拽": "看板 拖拽 任务管理",
    "任务分配": "看板 项目管理 任务分配",
    "报表": "数据分析 BI 看板 图表",
    "画成图": "数据可视化 图表 BI 分析",
    "SQL": "数据分析 数据查询 BI",
    "图表": "数据可视化 看板 图表",
    "数据": "数据分析 看板 BI",
    "会员": "订阅 付费 会员",
    "订阅": "会员 订阅 付费墙",
    "付费": "订阅 会员 付费墙 Stripe",
    "套餐": "订阅 会员 套餐",
    "收钱": "订阅 支付 付费",
    "收会员费": "订阅 会员 付费 套餐",
    "等级": "会员 套餐 权益 订阅",
    "权益": "订阅 会员 权限",
    # —— 跨范式模糊词 ——
    "提单子": "工单 提交",
    "处理跟进": "工单 处理 状态跟踪",
    "团队用": "团队协作 多用户",
    "团队": "团队协作 多用户",
    "分工": "任务分配 项目管理 看板",
    "预定": "预约 预订 时间段",
    "会议室": "预约 预订 日程",
}

# ============ 5. Demo DAG（模拟 Planner 输出的任务图）============
DEMO_DAG = {
    "tasks": [
        {"id": "T1", "type": "schema", "action": "创建数据表",
         "detail": "customers/follow_ups/team_members", "depends_on": [],
         "source": "pattern"},
        {"id": "T2", "type": "auth", "action": "配置认证",
         "detail": "Supabase Auth 邮箱登录", "depends_on": ["T1"],
         "source": "pattern"},
        {"id": "T3", "type": "rls", "action": "权限隔离",
         "detail": "RLS 按 team_id 隔离", "depends_on": ["T1", "T2"],
         "source": "pattern"},
        {"id": "T4", "type": "page", "action": "生成页面",
         "detail": "客户列表", "depends_on": ["T1"], "source": "pattern"},
        {"id": "T5", "type": "page", "action": "生成页面",
         "detail": "跟进进度看板", "depends_on": ["T1"], "source": "requirement"},
        {"id": "T6", "type": "logic", "action": "状态流转逻辑",
         "detail": "待跟进→跟进中→已成交", "depends_on": ["T3", "T5"],
         "source": "pattern"},
    ],
}

DEMO_DAG_LMS = {
    "tasks": [
        {"id": "T1", "type": "schema", "action": "创建数据表",
         "detail": "users/courses/lessons/progress/quizzes", "depends_on": [],
         "source": "pattern"},
        {"id": "T2", "type": "auth", "action": "配置多角色认证",
         "detail": "学员+讲师双角色登录/注册", "depends_on": ["T1"],
         "source": "pattern"},
        {"id": "T3", "type": "page", "action": "生成页面",
         "detail": "课程目录与课程详情页", "depends_on": ["T1"], "source": "pattern"},
        {"id": "T4", "type": "page", "action": "生成页面",
         "detail": "视频播放页(含防盗链)", "depends_on": ["T1", "T3"],
         "source": "pattern"},
        {"id": "T5", "type": "logic", "action": "课时解锁逻辑",
         "detail": "上一课时完成后解锁下一课时", "depends_on": ["T3", "T4"],
         "source": "pattern"},
        {"id": "T6", "type": "page", "action": "生成页面",
         "detail": "测验答题页(选择题+自动判分)", "depends_on": ["T1", "T4"],
         "source": "requirement"},
        {"id": "T7", "type": "logic", "action": "结课证书生成",
         "detail": "全部课时+测验通过 → 自动生成证书", "depends_on": ["T5", "T6"],
         "source": "requirement"},
        {"id": "T8", "type": "page", "action": "生成页面",
         "detail": "讲师后台:课程管理+学员进度查看", "depends_on": ["T2", "T3"],
         "source": "requirement"},
    ],
}
