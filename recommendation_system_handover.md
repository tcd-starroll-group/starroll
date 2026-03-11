# Recommendation backend
 -- Fang huafu
 -- date: 11th March

## 1. 改动概览
包括：
- 基于用户历史观星习惯做个性化推荐
- 接入 `Open-Meteo` 做天气/云量实时判断
- 计算月相、最佳观测时段、推荐星座和提示文案
- 用 Redis 做天气结果缓存
- 用 cronjob 定时更新用户画像
- 用 cronjob 每天定时发送推荐邮件
- 提供 OpenAPI 接口，便于前端或调试调用
- 增加了相应测试

一句话概括：

**系统既能“算出推荐”，也能“定时发给用户邮箱”。**

---

## 2. 本次新增/修改的核心文件

### 2.1 后端业务逻辑

- `backend/console/handler/request_stargazing_time.py`
- `backend/console/handler/get_stargazing_recommendation.py`

### 2.2 邮件相关

- `backend/console/utils/email_sender.py`
- `backend/constant/email.py`

### 2.3 定时任务

- `backend/cronjob/precompute_stargazing.py`
- `backend/cronjob/update_user_stargazing_profile.py`
- `backend/cronjob/send_stargazing_recommendation_email.py`
- `backend/cronjob/main.py`

### 2.4 OpenAPI / 路由

- `idl/openapiv3.yaml`
- `gen/py/src/openapi_server/impl/starroll_impl.py`

### 2.5 数据访问层

- `backend/console/dal/rds/user.py`
- `backend/console/dal/rds/identify_stars_job.py`

### 2.6 测试

- `backend/console/tests/handler/test_request_stargazing_time.py`
- `backend/console/tests/handler/test_get_stargazing_recommendation.py`
- `backend/cronjob/tests/test_send_stargazing_recommendation_email.py`
- 同时更新了已有的 `cronjob` 测试

---

## 3. 系统现在的整体流程

### 3.1 基础推荐计算

先做一层“纯计算”的推荐：

输入：
- 用户 GPS
- 目标日期
- 用户画像 / 历史任务

输出：
- `bestTimeSlots`
- `recommendedConstellations`
- `moonPhase`
- `tips`

这部分由以下文件共同完成：

- `backend/console/handler/request_stargazing_time.py`
- `backend/console/handler/get_stargazing_recommendation.py`

### 3.2 用户画像更新

定时扫描近 30 天活跃用户的识别任务，写入 `user.profile["stargazing_profile"]`。

画像包括：
- 偏好星座 `preferred_constellations`
- 偏好观测时段 `preferred_hours`
- 成功观测次数 `observation_count`
- 最近更新时间 `last_updated`

### 3.3 邮件推送

每天 18:00 定时执行：
- 找近 30 天活跃用户（这个要进行修改）
- 跳过今天已发过的人
- 用画像 + 天气生成今晚推荐
- 发邮件
- 写回 `last_email_sent`

---

## 4. OpenAPI 新增内容

### 4.1 已有接口：观星时间推荐

接口：`/api/requestStargazingTime`

该接口偏基础能力，主要返回：
- 最佳时段
- 天空情况

这个接口在 OpenAPI 里原本就有定义，这次补齐了实现。

### 4.2 新增接口：个性化推荐

接口：`/api/getStargazingRecommendation`

输入：
- `userCredentials`
- `gps`
- `targetDate`

输出：
- 最佳时段列表
- 推荐星座列表
- 月相
- tips

可以理解为：
- `/api/requestStargazingTime`：偏天气 / 时段层
- `/api/getStargazingRecommendation`：偏完整个性化推荐层

---

## 5. 核心实现细节

### 5.1 `request_stargazing_time.py`

职责：给定地点和日期，算出“今晚什么时候最适合看星星”。

主要逻辑：
- 调 `Open-Meteo`
- 获取逐小时天气字段：
  - `cloud_cover`
  - `precipitation_probability`
- 计算月相亮度
- 按夜间时段评分
- 选出最优观星时间窗
- Redis 缓存结果

评分维度：
- 云量 50%
- 降水概率 30%
- 月相亮度 20%

缓存策略：
- Redis key：`stargazing:{lat}:{lon}:{date}`
- TTL：3 小时

### 5.2 `get_stargazing_recommendation.py`

职责：基于用户习惯生成完整推荐结果。

主要逻辑：
1. 校验用户 token
2. 优先读取 `user.profile["stargazing_profile"]`
3. 如果画像不存在，则回退扫描最近 100 条识别任务
4. 只统计 `Succeeded` 的识别任务
5. 解析用户偏好星座
6. 结合目标月份的北半球季节星座表
7. 获取最佳观测时段
8. 生成 tips

#### 星座偏好提取增强

支持两类识别：

- 常见恒星专名映射
  - 例如：`Sirius -> Canis Major`
  - `Betelgeuse -> Orion`
  - `Polaris -> Ursa Minor`

- IAU 三字母缩写扫描
  - 例如：`alphOri -> Ori`
  - `108Vir -> Vir`
  - `alphaCMa -> CMa`



#### 时段评分修复

之前的问题：
- 2 小时时窗只用第 1 小时的分数代表整个窗口

现在改成：
- 对 2 小时窗口取平均云量、平均降水，再算平均分
- 再做非重叠窗口的 Top N 选择

#### Tips 修复

之前 tips 引用的是“最早的时段”，现在改成：
- 引用 `score` 最高的那个时段
---

## 6. 用户画像设计

画像保存在：

- `user.profile["stargazing_profile"]`

结构示例：

```json
{
  "stargazing_profile": {
    "preferred_constellations": ["Orion", "Leo"],
    "preferred_hours": [22, 23, 0],
    "observation_count": 42,
    "last_updated": "2026-03-11",
    "last_email_sent": "2026-03-11",
    "last_lat": 53.3498,
    "last_lon": -6.2603
  }
}
```

字段说明：
- `preferred_constellations`：用户最常观测的星座
- `preferred_hours`：最常观测时段
- `observation_count`：成功识别任务数
- `last_updated`：画像最近更新时间
- `last_email_sent`：防止同一天重复发邮件
- `last_lat/lon`：预留作为最近观测位置

当前说明：
- `last_lat/lon` 在邮件任务中会读取
- 如果没有值，会回退到默认地点（都柏林）
- 真实写入链路仍然比较弱，主要作为预留字段存在

---

## 7. 邮件推送设计

### 7.1 邮件模板

位置：`backend/constant/email.py`

新增内容：
- `RECOMMENDATION_EMAIL_SUBJECT`
- `RECOMMENDATION_EMAIL_TEXT_TEMPLATE`
- `RECOMMENDATION_EMAIL_HTML_TEMPLATE`

邮件内容包含：
- 日期
- 月相
- 最佳时间窗
- 推荐星座
- tips



### 7.2 邮件发送函数

位置：`backend/console/utils/email_sender.py`

新增函数：
- `send_recommendation_email(...)`

与验证码邮件共用 SMTP 配置：
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`

### 7.3 邮件任务

位置：`backend/cronjob/send_stargazing_recommendation_email.py`

逻辑：
- 查近 30 天活跃用户
- 跳过无邮箱用户
- 跳过今天已发过的人
- 用画像和天气生成推荐
- 发邮件
- 成功后写入 `last_email_sent`

默认位置：
- 如果画像里没有位置，就用都柏林坐标
- `DEFAULT_LAT = 53.3498`
- `DEFAULT_LON = -6.2603`

---

## 8. 定时任务注册情况

`backend/cronjob/main.py` 现在总共注册了 4 个任务：

1. `identify_stars_handler`
   - 每 5 秒执行一次
   - 用于轮询识别任务

2. `precompute_stargazing_handler`
   - 每 3 小时执行一次
   - 用于预热天气推荐缓存

3. `update_user_stargazing_profile_handler`
   - 每 6 小时执行一次
   - 用于更新用户画像

4. `send_stargazing_recommendation_email_handler`
   - 每天 18:00 执行一次
   - 用于发送推荐邮件

---

## 9. DAL 层变更

### 9.1 `user.py`

新增两个方法：
- `get_by_id(db, user_id)`
- `update_profile_by_id(db, user_id, profile)`

用途：
- 邮件任务和画像任务都要按 `user_id` 直接读 / 写 profile

### 9.2 `identify_stars_job.py`

新增：
- `list_recent_user_ids(db, days=30)`

用途：
- 找出近 30 天活跃用户，作为推荐邮件和画像任务的入口用户集

---

## 10. 测试覆盖情况

### 10.1 `test_request_stargazing_time.py`

覆盖内容：
- 月相计算
- 时段打分
- 夜间判断
- 天空情况分类
- Redis 缓存 key
- API 成功 / 失败 / 缓存命中 / 缓存降级

### 10.2 `test_get_stargazing_recommendation.py`

覆盖内容：
- 星座提取
- proper name 映射
- IAU 缩写解析
- 月相模型
- 推荐星座生成
- tips 生成
- 个性化推荐接口
- 只统计 `Succeeded` job
- 优先使用画像缓存
- 画像写入逻辑

### 10.3 `test_send_stargazing_recommendation_email.py`

覆盖内容：
- 邮件任务主入口
- 批量发送
- 单用户失败不中断
- 无邮箱跳过
- 当天已发跳过
- 默认位置回退
- 发送成功后写入 `last_email_sent`

### 10.4 其他测试修复

- `test_main.py` 跟进了新的 4 个 job 注册
- `test_update_user_stargazing_profile.py` 跟进了新的异常行为和关闭连接逻辑

---

## 11. 当前系统的前提和限制

### 11.1 业务前提

这次实现默认：
- 用户主要在北半球
- 推荐通过邮件发送
- OpenAPI 接口主要用于调试、后台调用或前端查看，不是最终触达手段

### 11.2 当前限制

- 没有自动建表 / 自动 migration，需要手动执行 SQL
- 邮件发送依赖 SMTP 环境变量，未配置不会发送成功
- 用户必须是“近 30 天活跃用户”才会收到邮件
- 如果当天已经发过，会被跳过
- 默认位置回退到都柏林，不一定适合所有用户
- `last_lat/lon` 的真实写入链路目前比较弱，更多是预留字段
- 星座偏好虽已增强，但仍依赖任务结果里的 `names` 字段，不是天文级精确映射

---

## 12. 手动联调用到的关键条件

如果后续要实际测试邮件发送，必须满足：

1. MySQL 中有表：
   - `user`
   - `identify_stars_jobs`

2. `backend/.env` 中配置好 SMTP：
   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_USER`
   - `SMTP_PASSWORD`
   - `SMTP_FROM_EMAIL`

3. 用户有真实邮箱地址

4. 用户近 30 天内至少有一条 `identify_stars_jobs` 记录
   - 最简单方式是手动插入一条 `Succeeded` 记录

5. 手动执行：
   - `send_stargazing_recommendation_email_handler()`

---

## 13. 关键代码入口

### 13.1 推荐接口入口

位置：`gen/py/src/openapi_server/impl/starroll_impl.py`

包含：
- `api_request_stargazing_time_post(...)`
- `api_get_stargazing_recommendation_post(...)`

### 13.2 个性化推荐主入口

位置：`backend/console/handler/get_stargazing_recommendation.py`

职责：
- 优先读取画像
- 回退扫描成功任务
- 生成月相、最佳时段、推荐星座、tips

### 13.3 邮件发送主入口

位置：`backend/cronjob/send_stargazing_recommendation_email.py`

函数：
- `send_stargazing_recommendation_email_handler()`

### 13.4 用户画像更新主入口

位置：`backend/cronjob/update_user_stargazing_profile.py`

函数：
- `update_user_stargazing_profile_handler()`

---

## 14. 易错点

1. **先确认 SMTP 能发**
   - 邮件推荐链路最容易卡在这里

2. **确认数据库表和活跃用户条件**
   - 很多接口 / 任务不生效不是代码坏，而是：
     - 没建表
     - 用户没活跃记录

3. **如果要继续扩展推荐质量**
   - 优先改进：
     - 用户最近地点写回 profile
     - 更精确的星座 / 星体映射
     - 邮件模板美化
     - 发送结果审计 / 失败重试



---


