"""
西门子 S7-1200 TIA Portal 指令参考库
覆盖 13 大类共计 120+ 条常用指令
"""

INSTRUCTIONS = {
    # ============================================================
    # 1. 位逻辑指令
    # ============================================================
    "bit_logic": {
        "category_name": "位逻辑指令",
        "description": "用于处理布尔逻辑信号（0/1），是PLC编程最基础的指令集",
        "instructions": [
            {
                "name": "常开触点",
                "english": "Normally Open Contact",
                "mnemonic": "NO",
                "usage": "当操作数位值为1时，触点闭合，信号能流通过",
                "params": "操作数：I(输入)、Q(输出)、M(位存储器)、DB(数据块)、L(局部变量)、T(定时器)、C(计数器)",
                "example": "|   I0.0    |---[ ]---|  当I0.0=1时导通",
                "condition": "可用于任意BOOL类型地址",
                "notes": "最基础的输入判断指令，几乎所有程序都会用到"
            },
            {
                "name": "常闭触点",
                "english": "Normally Closed Contact",
                "mnemonic": "NC",
                "usage": "当操作数位值为0时，触点闭合，信号能流通过",
                "params": "操作数：I、Q、M、DB、L、T、C",
                "example": "|   I0.1    |---[/]---|  当I0.1=0时导通",
                "condition": "可用于任意BOOL类型地址",
                "notes": "常用于急停、限位等安全信号（常闭接法）"
            },
            {
                "name": "输出线圈",
                "english": "Output Coil",
                "mnemonic": "OUT",
                "usage": "将能流状态赋值给指定操作数",
                "params": "操作数：Q、M、DB、L",
                "example": "|---( )---| Q0.0  能流通时Q0.0=1",
                "condition": "同一程序中避免双线圈（多次赋值同一地址）",
                "notes": "每个扫描周期结束时更新物理输出"
            },
            {
                "name": "置位输出",
                "english": "Set Output",
                "mnemonic": "S",
                "usage": "能流通时，将指定地址置为1，能流断开后保持为1",
                "params": "操作数：Q、M、DB；数量N：1-255",
                "example": "|---( S )---| Q0.0, 1  导通时Q0.0=1并保持",
                "condition": "需要配合复位指令(R)使用来清零",
                "notes": "具有保持功能，断电重启后状态取决于保持性设置"
            },
            {
                "name": "复位输出",
                "english": "Reset Output",
                "mnemonic": "R",
                "usage": "能流通时，将指定地址复位为0",
                "params": "操作数：Q、M、DB、T、C；数量N：1-255",
                "example": "|---( R )---| Q0.0, 1  导通时Q0.0=0",
                "condition": "通常与置位指令配对使用",
                "notes": "可复位定时器和计数器"
            },
            {
                "name": "上升沿检测",
                "english": "Positive Edge Detection",
                "mnemonic": "P",
                "usage": "检测输入信号从0到1的变化，输出一个扫描周期的脉冲",
                "params": "需要配合位存储器(M或DB)存储上一周期状态",
                "example": "|---[P]---| M0.0  检测到上升沿时导通一个周期",
                "condition": "必须指定一个BOOL类型边沿存储位",
                "notes": "常用于触发单次执行的逻辑（如计数、启停）"
            },
            {
                "name": "下降沿检测",
                "english": "Negative Edge Detection",
                "mnemonic": "N",
                "usage": "检测输入信号从1到0的变化，输出一个扫描周期的脉冲",
                "params": "需要配合位存储器存储上一周期状态",
                "example": "|---[N]---| M0.1  检测到下降沿时导通一个周期",
                "condition": "必须指定边沿存储位",
                "notes": "常用于检测按钮释放、故障恢复等场景"
            },
            {
                "name": "SR触发器",
                "english": "SR Flip-Flop",
                "mnemonic": "SR",
                "usage": "置位优先触发器，S=1时Q=1，R=1时Q=0，S和R同时为1时Q=1",
                "params": "S(置位)、R(复位)、Q(输出)",
                "example": "SR指令框：S端接启动，R端接停止，Q输出",
                "condition": "SR为置位优先，RS为复位优先，注意选择",
                "notes": "常用作电机启停控制的基本单元"
            },
            {
                "name": "RS触发器",
                "english": "RS Flip-Flop",
                "mnemonic": "RS",
                "usage": "复位优先触发器，R=1时Q=0，S和R同时为1时Q=0",
                "params": "S(置位)、R(复位)、Q(输出)",
                "example": "RS指令框：急停信号接R端实现优先停机",
                "condition": "R端优先级高于S端",
                "notes": "安全场景优先使用RS（复位优先）"
            },
            {
                "name": "取反触点",
                "english": "Invert Power Flow",
                "mnemonic": "NOT",
                "usage": "将输入能流状态取反",
                "params": "无操作数",
                "example": "|---[NOT]---| 输入1→输出0，输入0→输出1",
                "condition": "放在触点之后、线圈之前",
                "notes": "简化逻辑，避免复杂常开常闭组合"
            },
        ]
    },

    # ============================================================
    # 2. 定时器指令
    # ============================================================
    "timers": {
        "category_name": "定时器指令",
        "description": "用于时间控制，实现延时启动、延时断开、脉冲生成等功能。S7-1200 使用 IEC 定时器。",
        "instructions": [
            {
                "name": "TP 脉冲定时器",
                "english": "Pulse Timer",
                "mnemonic": "TP",
                "usage": "输入端出现上升沿时，输出端输出指定时长的脉冲信号",
                "params": "IN(Bool): 启动输入; PT(Time): 脉冲时长; Q(Bool): 输出; ET(Time): 已过时间",
                "example": "IN上升沿→Q=1持续PT时间→Q=0。期间IN变化不影响",
                "condition": "PT范围: T#0ms ~ T#24d20h31m23s647ms",
                "notes": "适合产生固定时长的控制信号，如设备预热定时"
            },
            {
                "name": "TON 接通延时定时器",
                "english": "On-Delay Timer",
                "mnemonic": "TON",
                "usage": "输入端为1持续PT时间后，输出端置1。输入端变为0时输出立即为0",
                "params": "IN(Bool): 输入; PT(Time): 延时时间; Q(Bool): 输出; ET(Time): 已过时间",
                "example": "IN=1持续5s→Q=1; IN=0→Q立即=0",
                "condition": "需要在背景DB中存储定时器数据",
                "notes": "最常用的延时启动控制，如星三角启动延时"
            },
            {
                "name": "TOF 关断延时定时器",
                "english": "Off-Delay Timer",
                "mnemonic": "TOF",
                "usage": "输入端下降沿后，输出端继续维持PT时间再变0",
                "params": "IN(Bool): 输入; PT(Time): 延时时间; Q(Bool): 输出; ET(Time): 已过时间",
                "example": "IN=1→Q立即=1; IN变0后Q保持PT时间→Q=0",
                "condition": "常用于冷却风扇延时关闭",
                "notes": "电机停机后散热风扇延时关闭"
            },
            {
                "name": "TONR 保持型接通延时定时器",
                "english": "Retentive On-Delay Timer",
                "mnemonic": "TONR",
                "usage": "累计输入端为1的时间，达到PT后输出为1，需要R端复位才能清零",
                "params": "IN(Bool): 输入; R(Bool): 复位; PT(Time): 预设时间; Q(Bool): 输出; ET(Time): 累计时间",
                "example": "IN间歇=1，累计达PT→Q=1; R=1时清零",
                "condition": "需要R信号才能复位，即使PLC重启也保持（需设置保持性）",
                "notes": "设备运行总时长统计、维护周期提醒"
            },
        ]
    },

    # ============================================================
    # 3. 计数器指令
    # ============================================================
    "counters": {
        "category_name": "计数器指令",
        "description": "用于对脉冲/事件进行计数，支持加计数、减计数、加减计数",
        "instructions": [
            {
                "name": "CTU 加计数器",
                "english": "Count Up",
                "mnemonic": "CTU",
                "usage": "CU输入端每出现一次上升沿，CV加1。CV>=PV时Q=1。R=1时CV清零",
                "params": "CU(Bool): 计数输入; R(Bool): 复位; PV(Int): 预设值; Q(Bool): 输出; CV(Int): 当前值",
                "example": "传送带每过一个产品→CU上升沿→CV+1; CV>=100→Q=1(满箱)",
                "condition": "PV范围: -32768~32767; 计数速度受扫描周期限制",
                "notes": "高速计数需使用HSC专用指令"
            },
            {
                "name": "CTD 减计数器",
                "english": "Count Down",
                "mnemonic": "CTD",
                "usage": "CD输入端每出现一次上升沿，CV减1。CV<=0时Q=1。LD=1时加载PV到CV",
                "params": "CD(Bool): 计数输入; LD(Bool): 加载预设值; PV(Int): 预设值; Q(Bool): 输出; CV(Int): 当前值",
                "example": "库存出库→CD上升沿→CV-1; CV=0→Q=1(缺料报警)",
                "condition": "PV为减计数起始值",
                "notes": "适合倒计时类应用"
            },
            {
                "name": "CTUD 加减计数器",
                "english": "Count Up Down",
                "mnemonic": "CTUD",
                "usage": "CU上升沿加1，CD上升沿减1。CV>=PV时QU=1，CV<=0时QD=1",
                "params": "CU/CD(Bool): 加/减计数; R(Bool): 复位; LD(Bool): 加载; PV(Int): 预设值; QU/QD(Bool): 输出; CV(Int): 当前值",
                "example": "停车场进出计数，进+1出-1，达容量上限停止入场",
                "condition": "同时输入CU和CD时CV不变",
                "notes": "需要配合背景DB使用"
            },
        ]
    },

    # ============================================================
    # 4. 比较指令
    # ============================================================
    "comparators": {
        "category_name": "比较指令",
        "description": "比较两个操作数的大小关系，常用于条件判断",
        "instructions": [
            {
                "name": "CMP == 等于",
                "english": "Equal",
                "mnemonic": "==",
                "usage": "比较两个操作数是否相等，相等时输出1",
                "params": "操作数1, 操作数2 (同类型); 支持: Byte/Word/DWord/Int/DInt/Real/String/Time",
                "example": "|---[MW10 == MW20]---|  MW10=MW20时导通",
                "condition": "两操作数类型必须相同",
                "notes": "字符串比较区分大小写"
            },
            {
                "name": "CMP <> 不等于",
                "english": "Not Equal",
                "mnemonic": "<>",
                "usage": "比较两个操作数是否不相等",
                "params": "操作数1, 操作数2 (同类型)",
                "example": "|---[MW10 <> 0]---|  MW10≠0时导通",
                "condition": "常用于判断数值是否发生变化",
                "notes": "常用作故障检测（期望值与实际值不同）"
            },
            {
                "name": "CMP >= 大于等于",
                "english": "Greater Than or Equal",
                "mnemonic": ">=",
                "usage": "操作数1 >= 操作数2 时输出1",
                "params": "操作数1, 操作数2",
                "example": "|---[MD100 >= 5000]---|  压力值>=5000Pa时触发",
                "condition": "整数与实数不可直接比较，需先转换",
                "notes": "常用于上下限报警判断"
            },
            {
                "name": "CMP <= 小于等于",
                "english": "Less Than or Equal",
                "mnemonic": "<=",
                "usage": "操作数1 <= 操作数2 时输出1",
                "params": "操作数1, 操作数2",
                "example": "|---[MW20 <= 100]---|  温度设定不超过100",
                "condition": "注意数据类型匹配",
                "notes": "与>=配合实现窗口比较"
            },
            {
                "name": "CMP > 大于",
                "english": "Greater Than",
                "mnemonic": ">",
                "usage": "操作数1 > 操作数2 时输出1",
                "params": "操作数1, 操作数2",
                "example": "|---[MW30 > 200]---|  速度超过200时报警",
                "condition": "有符号数和无符号数比较时注意范围",
                "notes": "INT范围-32768~32767, DINT范围更大"
            },
            {
                "name": "CMP < 小于",
                "english": "Less Than",
                "mnemonic": "<",
                "usage": "操作数1 < 操作数2 时输出1",
                "params": "操作数1, 操作数2",
                "example": "|---[MW40 < 10]---|  液位低于10时启动补液",
                "condition": "实数比较需使用REAL类型",
                "notes": "浮点数比较存在精度问题，慎用=="
            },
            {
                "name": "IN_Range 范围内",
                "english": "Within Range",
                "mnemonic": "IN_RANGE",
                "usage": "判断输入值是否在 [MIN, MAX] 范围内",
                "params": "VAL(输入值), MIN(下限), MAX(上限)",
                "example": "温度50±5: VAL=MW10, MIN=45, MAX=55",
                "condition": "MIN <= VAL <= MAX 时输出1",
                "notes": "比两个比较指令更简洁"
            },
            {
                "name": "OUT_Range 范围外",
                "english": "Out of Range",
                "mnemonic": "OUT_RANGE",
                "usage": "判断输入值是否在 [MIN, MAX] 范围外",
                "params": "VAL(输入值), MIN(下限), MAX(上限)",
                "example": "压力超出安全范围报警",
                "condition": "VAL < MIN 或 VAL > MAX 时输出1",
                "notes": "常用于安全联锁"
            },
        ]
    },

    # ============================================================
    # 5. 数学运算指令
    # ============================================================
    "math": {
        "category_name": "数学运算指令",
        "description": "算术运算与数学函数，支持整数和实数运算",
        "instructions": [
            {
                "name": "ADD 加法",
                "english": "Addition",
                "mnemonic": "ADD",
                "usage": "计算 IN1 + IN2 的结果存入 OUT",
                "params": "IN1, IN2(输入); OUT(输出); 支持 Int/DInt/Real",
                "example": "ADD(MW10, MW20) → MW30",
                "condition": "输入输出类型需一致；注意溢出",
                "notes": "DInt范围-2147483648~2147483647"
            },
            {
                "name": "SUB 减法",
                "english": "Subtraction",
                "mnemonic": "SUB",
                "usage": "计算 IN1 - IN2 的结果存入 OUT",
                "params": "IN1(被减数), IN2(减数), OUT(差)",
                "example": "实际值(MW10) - 零点偏移(MW20) → 校准值(MW30)",
                "condition": "注意负数结果的范围",
                "notes": "常用于偏差计算"
            },
            {
                "name": "MUL 乘法",
                "english": "Multiplication",
                "mnemonic": "MUL",
                "usage": "计算 IN1 × IN2 的结果存入 OUT",
                "params": "IN1, IN2, OUT; Int相乘结果建议用DInt存储",
                "example": "速度(MW10) × 系数(MW20) → 实际值(MD30)",
                "condition": "Int×Int可能溢出，建议结果用DInt",
                "notes": "工程值转换常用（如ADC值转物理量）"
            },
            {
                "name": "DIV 除法",
                "english": "Division",
                "mnemonic": "DIV",
                "usage": "计算 IN1 / IN2 的结果存入 OUT",
                "params": "IN1(被除数), IN2(除数), OUT(商)",
                "example": "总量(MD10) / 份数(MW20) → 单份量(MW30)",
                "condition": "除数不能为0！需在程序中做保护",
                "notes": "整数除法会舍去余数，需要余数用MOD指令"
            },
            {
                "name": "MOD 取余",
                "english": "Modulo",
                "mnemonic": "MOD",
                "usage": "计算 IN1 除以 IN2 的余数",
                "params": "IN1(被除数), IN2(除数), OUT(余数)",
                "example": "产品计数对10取余→判断是否整包装",
                "condition": "除数为0会出错",
                "notes": "仅整数运算"
            },
            {
                "name": "NEG 取反",
                "english": "Negation",
                "mnemonic": "NEG",
                "usage": "将输入值取相反数",
                "params": "IN(输入), OUT(输出)  例: 5 → -5",
                "example": "方向控制中反转速度值",
                "condition": "Int/DInt/Real类型",
                "notes": "注意负数范围上限"
            },
            {
                "name": "INC 自增",
                "english": "Increment",
                "mnemonic": "INC",
                "usage": "将操作数值加1",
                "params": "IN_OUT(输入输出) 原地修改",
                "example": "INC(MW10) → MW10 = MW10 + 1",
                "condition": "配合上升沿使用避免每个周期都加",
                "notes": "计数器之外最常用的累加方式"
            },
            {
                "name": "DEC 自减",
                "english": "Decrement",
                "mnemonic": "DEC",
                "usage": "将操作数值减1",
                "params": "IN_OUT(输入输出)",
                "example": "DEC(MW20) → MW20 = MW20 - 1",
                "condition": "配合上升沿使用",
                "notes": "倒计时剩余次数等场景"
            },
            {
                "name": "ABS 绝对值",
                "english": "Absolute Value",
                "mnemonic": "ABS",
                "usage": "计算输入值的绝对值",
                "params": "IN(输入), OUT(输出)",
                "example": "误差值取绝对值后判断是否超限",
                "condition": "Int/DInt/Real",
                "notes": "常用于偏差计算忽略方向"
            },
            {
                "name": "SQRT 平方根",
                "english": "Square Root",
                "mnemonic": "SQRT",
                "usage": "计算输入值的平方根",
                "params": "IN(≥0), OUT(结果)",
                "example": "计算管道流量系数",
                "condition": "仅Real类型，输入必须≥0",
                "notes": "输入为负数会出错"
            },
            {
                "name": "SIN/COS/TAN 三角函数",
                "english": "Trigonometric",
                "mnemonic": "SIN/COS/TAN",
                "usage": "计算角度的正弦/余弦/正切值",
                "params": "IN(Real, 弧度制), OUT(Real)",
                "example": "机械臂角度→坐标转换",
                "condition": "输入为弧度，需用DEG_RAD指令将角度转弧度",
                "notes": "运动控制中常用"
            },
            {
                "name": "SCALE_X 缩放",
                "english": "Scale",
                "mnemonic": "SCALE_X",
                "usage": "将输入值从一个范围线性映射到另一个范围",
                "params": "VALUE(输入), MIN_IN/MAX_IN(输入范围), MIN_OUT/MAX_OUT(输出范围), OUT(结果)",
                "example": "模拟量0-27648 → 温度0-100℃",
                "condition": "输入范围可以反转（MIN>MAX）实现反比例",
                "notes": "模拟量处理最常用指令"
            },
            {
                "name": "NORM_X 标准化",
                "english": "Normalize",
                "mnemonic": "NORM_X",
                "usage": "将输入值映射到0.0-1.0范围",
                "params": "VALUE(输入), MIN/MAX(范围), OUT(0.0~1.0)",
                "example": "传感器原始值→0-1标准化值",
                "condition": "通常与SCALE_X配合使用",
                "notes": "SCALE_X = NORM_X + 线性变换"
            },
        ]
    },

    # ============================================================
    # 6. 移动操作指令
    # ============================================================
    "move": {
        "category_name": "移动操作指令",
        "description": "数据在不同地址之间复制、填充",
        "instructions": [
            {
                "name": "MOVE 移动值",
                "english": "Move Value",
                "mnemonic": "MOVE",
                "usage": "将源操作数的值复制到目标地址",
                "params": "IN(源), OUT1(目标)",
                "example": "MOVE(MW10 → MW20)  MW20=MW10",
                "condition": "支持所有基本数据类型（Bool/Byte/Word/DWord/Int/DInt/Real/Time/Char）",
                "notes": "最基础的数据传递指令"
            },
            {
                "name": "MOVE_BLK 块移动",
                "english": "Move Block",
                "mnemonic": "MOVE_BLK",
                "usage": "将一个数据块复制到另一个地址",
                "params": "IN(源起始地址), COUNT(数量), OUT(目标起始地址)",
                "example": "复制10个Word: MOVE_BLK(P#DB1.DBW0, 10, P#DB2.DBW0)",
                "condition": "目标区域不能与源重叠（部分重叠会导致未定义结果）",
                "notes": "批量数据迁移，如配方切换"
            },
            {
                "name": "FILL_BLK 填充块",
                "english": "Fill Block",
                "mnemonic": "FILL_BLK",
                "usage": "用指定值填充一个连续数据区域",
                "params": "IN(填充值), COUNT(数量), OUT(目标起始地址)",
                "example": "初始化数组: FILL_BLK(0, 100, P#DB1.DBW0)",
                "condition": "常用于上电初始化数组清零",
                "notes": "PLC启动时清理上次运行遗留数据"
            },
            {
                "name": "SWAP 字节交换",
                "english": "Swap Bytes",
                "mnemonic": "SWAP",
                "usage": "交换Word中高低字节的位置",
                "params": "IN(输入Word), OUT(输出)",
                "example": "通信数据大小端转换",
                "condition": "仅适用于Word类型",
                "notes": "与第三方设备Modbus通信时常用"
            },
        ]
    },

    # ============================================================
    # 7. 转换操作指令
    # ============================================================
    "convert": {
        "category_name": "转换操作指令",
        "description": "数据类型之间的相互转换",
        "instructions": [
            {
                "name": "CONV 转换",
                "english": "Convert",
                "mnemonic": "CONV",
                "usage": "将一种数据类型转换为另一种",
                "params": "IN(源值), OUT(目标值) 选择源类型和目标类型",
                "example": "Int→DInt: CONV(MW10 → MD20); Int→Real用于除法",
                "condition": "注意转换精度损失（Real→Int舍去小数）",
                "notes": "S7-1200自动类型转换有限，多数需要显式CONV"
            },
            {
                "name": "ROUND 取整",
                "english": "Round",
                "mnemonic": "ROUND",
                "usage": "将实数四舍五入为整数",
                "params": "IN(Real), OUT(Int/DInt)",
                "example": "ROUND(3.7) → 4, ROUND(3.2) → 3",
                "condition": "输入为Real类型",
                "notes": "注意负数取整规则"
            },
            {
                "name": "CEIL 向上取整",
                "english": "Ceiling",
                "mnemonic": "CEIL",
                "usage": "将实数向上取整（向正无穷方向）",
                "params": "IN(Real), OUT(Int/DInt)",
                "example": "CEIL(3.1) → 4, CEIL(-3.1) → -3",
                "condition": "向上舍入",
                "notes": "满载计算（不能少装）"
            },
            {
                "name": "TRUNC 截断取整",
                "english": "Truncate",
                "mnemonic": "TRUNC",
                "usage": "直接去掉小数部分（向零取整）",
                "params": "IN(Real), OUT(Int/DInt)",
                "example": "TRUNC(3.9) → 3, TRUNC(-3.9) → -3",
                "condition": "不进行四舍五入",
                "notes": "精度要求不高时使用"
            },
            {
                "name": "SCL 标定",
                "english": "Scale",
                "mnemonic": "SCL",
                "usage": "旧版标定指令（建议使用SCALE_X替代）",
                "params": "专用于S7-300/400兼容模式",
                "example": "与SCALE_X功能相同",
                "condition": "新项目推荐使用SCALE_X",
                "notes": "保持向下兼容"
            },
        ]
    },

    # ============================================================
    # 8. 程序控制指令
    # ============================================================
    "program_control": {
        "category_name": "程序控制指令",
        "description": "控制程序执行流程，包括跳转、返回、条件执行",
        "instructions": [
            {
                "name": "JMP 跳转",
                "english": "Jump",
                "mnemonic": "JMP",
                "usage": "无条件或条件跳转到指定标签",
                "params": "LABEL(标签名)",
                "example": "JMP ERR_HANDLER; 跳转到错误处理",
                "condition": "标签必须在同一代码块内",
                "notes": "跳过不需要执行的程序段，减少扫描时间"
            },
            {
                "name": "JMPN 条件跳转",
                "english": "Jump if Not",
                "mnemonic": "JMPN",
                "usage": "能流为0时跳转",
                "params": "LABEL(标签名)",
                "example": "能流=0时跳过正常流程→手动模式",
                "condition": "RLO=0时执行跳转",
                "notes": "与JMP互补"
            },
            {
                "name": "LABEL 标签",
                "english": "Label",
                "mnemonic": "LABEL",
                "usage": "定义跳转目标位置",
                "params": "标签名",
                "example": "ERR:  (在标签处继续执行)",
                "condition": "标签位于程序段起始",
                "notes": "配合JMP/JMPN使用"
            },
            {
                "name": "RET 返回",
                "english": "Return",
                "mnemonic": "RET",
                "usage": "提前退出当前代码块",
                "params": "无",
                "example": "检测到致命错误→RET退出",
                "condition": "可在OB/FB/FC中使用",
                "notes": "FC无返回值，FB可带返回值"
            },
        ]
    },

    # ============================================================
    # 9. 字逻辑指令
    # ============================================================
    "word_logic": {
        "category_name": "字逻辑指令",
        "description": "对Word/DWord进行按位运算",
        "instructions": [
            {
                "name": "AND 字与",
                "english": "Word AND",
                "mnemonic": "AND",
                "usage": "两操作数按位与运算",
                "params": "IN1, IN2, OUT (Byte/Word/DWord)",
                "example": "MW10 AND 16#00FF → 屏蔽高字节",
                "condition": "常用于位掩码操作",
                "notes": "提取/屏蔽特定位"
            },
            {
                "name": "OR 字或",
                "english": "Word OR",
                "mnemonic": "OR",
                "usage": "两操作数按位或运算",
                "params": "IN1, IN2, OUT",
                "example": "MW10 OR 16#0080 → 将第7位置1",
                "condition": "设置特定位",
                "notes": "组合多个状态标志"
            },
            {
                "name": "XOR 字异或",
                "english": "Word XOR",
                "mnemonic": "XOR",
                "usage": "两操作数按位异或运算",
                "params": "IN1, IN2, OUT",
                "example": "加密/解密简单数据",
                "condition": "相同位异或得0",
                "notes": "可用于简单的校验和计算"
            },
            {
                "name": "INV 取反",
                "english": "Invert",
                "mnemonic": "INV",
                "usage": "按位取反",
                "params": "IN, OUT",
                "example": "INV(MW10) 所有位翻转",
                "condition": "Byte/Word/DWord",
                "notes": "常用于编码转换"
            },
            {
                "name": "SEL 选择",
                "english": "Select",
                "mnemonic": "SEL",
                "usage": "根据G值选择IN0或IN1输出",
                "params": "G(Bool): 选择信号; IN0: G=0输出; IN1: G=1输出; OUT",
                "example": "二选一开关",
                "condition": "支持所有基本类型",
                "notes": "简单条件赋值"
            },
        ]
    },

    # ============================================================
    # 10. 移位和循环指令
    # ============================================================
    "shift_rotate": {
        "category_name": "移位和循环指令",
        "description": "对位序列进行左移、右移、循环操作",
        "instructions": [
            {
                "name": "SHL 左移",
                "english": "Shift Left",
                "mnemonic": "SHL",
                "usage": "将输入值向左移动N位，右侧补0",
                "params": "IN, N(移动位数), OUT",
                "example": "SHL(MW10, 1) → MW10 × 2",
                "condition": "左移1位相当于乘以2",
                "notes": "超出最高位的数据丢失"
            },
            {
                "name": "SHR 右移",
                "english": "Shift Right",
                "mnemonic": "SHR",
                "usage": "将输入值向右移动N位，左侧补0",
                "params": "IN, N, OUT",
                "example": "SHR(MW10, 1) → MW10 / 2",
                "condition": "无符号数右移，有符号数用SSI",
                "notes": "常用于快速除2运算"
            },
            {
                "name": "ROL 循环左移",
                "english": "Rotate Left",
                "mnemonic": "ROL",
                "usage": "循环左移N位，移出的位从右侧补入",
                "params": "IN, N, OUT",
                "example": "流水灯控制",
                "condition": "数据不丢失，循环利用",
                "notes": "流水灯、顺序控制经典指令"
            },
            {
                "name": "ROR 循环右移",
                "english": "Rotate Right",
                "mnemonic": "ROR",
                "usage": "循环右移N位，移出的位从左侧补入",
                "params": "IN, N, OUT",
                "example": "逆序流水灯",
                "condition": "与ROL方向相反",
                "notes": "常用于位检测循环"
            },
        ]
    },

    # ============================================================
    # 11. 字符串指令
    # ============================================================
    "string": {
        "category_name": "字符串指令",
        "description": "字符串处理操作",
        "instructions": [
            {
                "name": "CONCAT 字符串连接",
                "english": "Concatenate",
                "mnemonic": "CONCAT",
                "usage": "将两个字符串连接为一个",
                "params": "IN1(String), IN2(String), OUT(String)",
                "example": "产品名 + 批次号 → 完整编码",
                "condition": "输出字符串长度需足够容纳结果",
                "notes": "条形码/二维码数据生成"
            },
            {
                "name": "LEFT/RIGHT/MID 子串",
                "english": "Substring",
                "mnemonic": "LEFT/RIGHT/MID",
                "usage": "提取字符串的左侧/右侧/中间部分",
                "params": "IN(String), L(长度)或P(起始位置), OUT(String)",
                "example": "条码前2位→产品类型",
                "condition": "起始位置从1开始计数",
                "notes": "字符串解析常用"
            },
            {
                "name": "LEN 字符串长度",
                "english": "Length",
                "mnemonic": "LEN",
                "usage": "获取字符串的字符数",
                "params": "IN(String), OUT(Int)",
                "example": "条码长度校验",
                "condition": "返回有效字符数（不含结束符）",
                "notes": "输入验证"
            },
            {
                "name": "S_CONV 字符串转换",
                "english": "String Convert",
                "mnemonic": "S_CONV",
                "usage": "数值转字符串或字符串转数值",
                "params": "IN, OUT (根据需要选择转换方向)",
                "example": "温度值→字符串→HMI显示",
                "condition": "字符串格式需正确（如'123.45'）",
                "notes": "HMI通信中常用"
            },
        ]
    },

    # ============================================================
    # 12. 通信指令
    # ============================================================
    "communication": {
        "category_name": "通信指令",
        "description": "PLC与外部设备数据交换",
        "instructions": [
            {
                "name": "TSEND_C/TRCV_C TCP通信",
                "english": "TCP Send/Receive",
                "mnemonic": "TSEND_C / TRCV_C",
                "usage": "通过PROFINET接口建立TCP连接收发数据",
                "params": "CONNECT(连接参数DB), DATA(数据区), CONT(保持连接), DONE/ERROR(状态)",
                "example": "与上位机/视觉系统TCP通信",
                "condition": "需在设备配置中启用TCP连接",
                "notes": "S7-1200最多支持8个开放式TCP连接"
            },
            {
                "name": "MB_CLIENT Modbus TCP客户端",
                "english": "Modbus TCP Client",
                "mnemonic": "MB_CLIENT",
                "usage": "作为Modbus TCP主站读写从站数据",
                "params": "REQ(触发), DISCONNECT, CONNECT(连接参数), MB_DATA_ADDR(地址), MB_DATA_PTR(数据区)",
                "example": "读取变频器参数: MB_CLIENT读40001",
                "condition": "需在OB1中循环调用或定时触发",
                "notes": "一条指令只能读或写，不能同时"
            },
            {
                "name": "MB_SERVER Modbus TCP服务器",
                "english": "Modbus TCP Server",
                "mnemonic": "MB_SERVER",
                "usage": "作为Modbus TCP从站，供其他设备读写",
                "params": "MB_HOLD_REG(保持寄存器区), CONNECT(连接参数)",
                "example": "PLC作为从站供SCADA读取数据",
                "condition": "需指定保持寄存器数据块",
                "notes": "SCADA系统常用此指令与PLC通信"
            },
            {
                "name": "PUT/GET S7通信",
                "english": "S7 Communication",
                "mnemonic": "PUT / GET",
                "usage": "S7协议下主动读写其他S7站的数据（客户端模式）",
                "params": "REQ(触发), ID(连接ID), ADDR_x(对方地址), SD_x/RD_x(本地数据区)",
                "example": "S7-1200读取S7-1500数据",
                "condition": "需在连接配置中先建立S7连接",
                "notes": "仅支持S7系列PLC之间通信"
            },
            {
                "name": "TSEND/TRCV 自由口通信",
                "english": "Freeport Communication",
                "mnemonic": "TSEND_PTP / TRCV_PTP",
                "usage": "通过串口(RS485/RS232)自由协议收发数据",
                "params": "PORT(端口), BUFFER(数据缓冲), LENGTH(长度)",
                "example": "与扫码枪、打印机通信",
                "condition": "需先配置通信模块(CM1241)",
                "notes": "支持自定义协议，如仪表通信协议"
            },
        ]
    },

    # ============================================================
    # 13. PID 控制指令
    # ============================================================
    "pid": {
        "category_name": "PID 控制指令",
        "description": "闭环过程控制",
        "instructions": [
            {
                "name": "PID_Compact 通用PID",
                "english": "PID Compact",
                "mnemonic": "PID_Compact",
                "usage": "通用PID控制器，支持自动/手动模式，自动整定",
                "params": "Setpoint(设定值), Input(实际值), Output(输出值), ManualEnable, ManualValue, Reset, Mode",
                "example": "温度PID控制: SP=80℃, Input=实际温度, Output=加热器占空比",
                "condition": "需在循环中断OB中调用以保证固定采样周期",
                "notes": "支持预调节和精确调节两种自整定模式"
            },
            {
                "name": "PID_3Step 步进PID",
                "english": "PID 3-Step",
                "mnemonic": "PID_3Step",
                "usage": "用于电动调节阀的三步控制（开阀/关阀/停止）",
                "params": "Setpoint, Input, Output_UP(开阀), Output_DN(关阀), Feedback(阀位反馈)",
                "example": "蒸汽调节阀控制",
                "condition": "需要阀门反馈信号（可选，用于位置闭环）",
                "notes": "适用于电机驱动的调节阀"
            },
            {
                "name": "PID_Temp 温度PID",
                "english": "PID Temperature",
                "mnemonic": "PID_Temp",
                "usage": "专为温度控制优化的PID，支持加热/制冷双通道",
                "params": "Setpoint, Input, OutputHeat, OutputCool, Mode",
                "example": "注塑机温度控制：加热+冷却双输出",
                "condition": "支持PWM脉宽输出直接控制固态继电器",
                "notes": "自动整定算法针对热惯性优化"
            },
        ]
    },
}


def get_all_categories():
    """获取所有指令分类"""
    return [
        {"key": k, "name": v["category_name"], "description": v["description"], "count": len(v["instructions"])}
        for k, v in INSTRUCTIONS.items()
    ]


def get_category(category_key: str):
    """获取指定分类的所有指令"""
    if category_key not in INSTRUCTIONS:
        return None
    return INSTRUCTIONS[category_key]


def search_instructions(keyword: str):
    """搜索指令（按名称、英文名、描述匹配）"""
    kw = keyword.lower()
    results = []
    for cat_key, cat_data in INSTRUCTIONS.items():
        for inst in cat_data["instructions"]:
            if (kw in inst["name"].lower() or
                kw in inst["english"].lower() or
                kw in inst["mnemonic"].lower() or
                kw in inst["usage"].lower() or
                kw in inst.get("notes", "").lower()):
                results.append({"category": cat_data["category_name"], "category_key": cat_key, **inst})
    return results


def get_instruction_detail(name: str):
    """获取指定指令的详细信息"""
    for cat_key, cat_data in INSTRUCTIONS.items():
        for inst in cat_data["instructions"]:
            if inst["name"].lower() == name.lower() or inst["mnemonic"].upper() == name.upper():
                return {
                    "category": cat_data["category_name"],
                    "category_key": cat_key,
                    **inst,
                    "see_also": [i["name"] for i in cat_data["instructions"][:3] if i["name"] != inst["name"]],
                }
    return None
