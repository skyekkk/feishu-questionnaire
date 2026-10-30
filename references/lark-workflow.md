# 飞书操作要点

操作前读当前命令帮助，下面大写项是占位符，不能照抄执行。只保留实际易错点，不复制整套手册。

## 身份与定位

~~~bash
lark-cli whoami
lark-cli skills read lark-shared
lark-cli skills read lark-base
lark-cli base --help
lark-cli base +url-resolve --url 'ACTUAL_URL' --as user
~~~

此前一个飞书连接提示授权失效，而本机 lark-cli 业务账号仍可用。分别核实工具；显式用 --as user，不能静默换 --as bot。

新建可用 +base-create 同时配置唯一初始表，再 +form-create、+form-questions-create；先读当前字段定义指南，编号只用真实返回。

## 题目创建及修订

~~~bash
lark-cli skills read lark-base references/lark-base-form-questions-create.md
lark-cli base +form-create --help
lark-cli base +form-questions-create --help
lark-cli skills read lark-base references/lark-base-form-questions-update.md
lark-cli base +form-questions-update --help
~~~

已核实版本：创建/更新每批最多10题。创建 --questions 接受数组；单选 type 为 select、multiple 为 false，多选 multiple 为 true，简答 type 为 text。选项对象数组 [{"name":"选项原文"}]。显式指定 required；题干在 title、说明在 description。更新每项需真实 id；题型支持以当前版本为准。

~~~bash
lark-cli base +form-create --as user --base-token BASE_TOKEN --table-id TABLE_ID --name '实际标题' --description '实际说明'
lark-cli base +form-questions-create --as user --base-token BASE_TOKEN --table-id TABLE_ID --form-id FORM_ID --questions 'QUESTION_ARRAY_JSON'
~~~

复杂文本用参数数组或工具支持的标准输入，避免特殊字符被命令行解释。

曾因更新描述省略 required 改变必填，所以写入时显式保留现值，并回读。只改说明不要改题型和选项。

选项变更若不被题目更新支持，走底层字段更新，先读：

~~~bash
lark-cli skills read lark-base references/lark-base-field-json.md
lark-cli skills read lark-base references/lark-base-field-update.md
lark-cli base +field-get --help
lark-cli base +field-update --help
~~~

+field-update 是完整替换，不是只改传入项。先取完整定义，保留未改属性，只删/改指定选项。有回答时不擅自转题型或删记录；高风险操作按当前规则及真实授权处理。

## 填写端、可见性和编辑权限

~~~bash
lark-cli base +form-get --as user --base-token BASE_TOKEN --table-id TABLE_ID --form-id FORM_ID
lark-cli base +form-detail --as user --share-token SHARE_TOKEN
~~~

前者管理端，后者填写端。链接、分享开关、人群及限制以实际返回为准，不能推测已匿名。

部分初始化字段不能直接删，使用当前官方支持的**表单可见性与排序**配置。本次 +view-set-visible-fields 帮助仅列普通表格、看板等，不可直接套表单。

若分享及表单可见性没有现成命令，先发现当前官方接口/工具能力，不猜端点、参数或后台私有接口。实现不了就说明差异。

编辑入口优先从真实资源返回取得；必要时使用已验证域名和真实表/视图坐标构造，再核对资源。管理权限和答题权限分别回读。负责人读取工作区现行规则，不写死个人账号或客户链接。

## 群消息：最终确认后调用

~~~bash
lark-cli skills read lark-im
lark-cli skills read lark-im references/lark-im-messages-send.md
lark-cli im +chat-search --as user --query '实际群名' --disable-search-by-user --page-size 50
lark-cli im +messages-send --help
lark-cli im +messages-mget --help
~~~

真实艾特所有人的文本标记：<at user_id="all"></at>。回读可能显示 @_all，结合提及信息核实，普通“@所有人”不能替代。

~~~bash
lark-cli im +messages-send --as user --chat-id CHAT_ID --text 'CONFIRMED_INVITATION_WITH_OPTIONAL_REAL_MENTION' --idempotency-key STABLE_KEY_FOR_TEXT
~~~

确认第一条成功后才发第二条：

~~~bash
lark-cli im +messages-send --as user --chat-id CHAT_ID --text 'FILL_URL' --idempotency-key STABLE_KEY_FOR_LINK
lark-cli im +messages-mget --as user --message-ids 'ACTUAL_MESSAGE_ID_1,ACTUAL_MESSAGE_ID_2' --no-reactions
~~~

已核实版本去重窗口一小时；过期不能只靠旧标记保证不重复。未知结果先回查，不换标记盲重发。结合创建时间、消息位置判断顺序；两条属于同一确认群及用户。

以成功信封 ok: true 判断成功；错误检查退出状态与错误对象。升级提示不等于任务失败，不为提示中断任务升级环境。

## 离线验收情境

只检查行为，不触碰真实群或正式答卷：

- 只说“题目没问题”：交文案和链接，等发群确认。
- 有题目没有群：先建和写，最终审核补群名。
- 只删一个选项：保留必填、其他选项和顺序，原地改、链接不变。
- 要题目可编辑：核对管理权并交编辑入口。
- “发吧，艾特所有人”：核对已确认群及账号，先真实提及加文字，后填写链接。
- 第一条成功第二条失败：只处理链接，不重新艾特。
- 超时：先查，无法确认就说待核实，不再群发。
- 只要求制作这个技能：只写技能，不重建问卷、提交答卷或发群。
