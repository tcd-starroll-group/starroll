"""
每日定时任务：向活跃用户发送个性化观星推荐邮件。

执行流程：
  1. 查询近 30 天内有过识别任务的活跃用户。
  2. 跳过今天已发送过邮件的用户（通过 profile 中的 last_email_sent 字段判断）。
  3. 对每位符合条件的用户，结合其存储的画像数据和实时天气计算今晚的推荐内容。
  4. 格式化并通过 SMTP 发送推荐邮件。
  5. 将今天的日期写入 profile["stargazing_profile"]["last_email_sent"]，防止重复发送。
"""

import asyncio
import logging
from datetime import date

from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob
from backend.console.dal.rds.user import User
from backend.console.handler.get_stargazing_recommendation import (
    _get_moon_info,
    _fetch_top_slots,
    _build_constellation_recommendations,
    _generate_tips,
)
from backend.console.utils.email_sender import send_recommendation_email

logger = logging.getLogger(__name__)

# 用户画像中无位置记录时使用的默认坐标（爱尔兰都柏林）
DEFAULT_LAT = 53.3498
DEFAULT_LON = -6.2603


def send_stargazing_recommendation_email_handler():
    """APScheduler 同步入口，在新事件循环中运行异步发送逻辑。"""
    try:
        asyncio.run(_send_all())
    except Exception as e:
        logger.error(f"Recommendation email job failed: {e}", exc_info=True)


async def _send_all():
    """批量处理：获取所有活跃用户并逐一发送推荐邮件。"""
    db_session = next(get_db())
    today = date.today()

    try:
        # 查询近 30 天内有过识别任务记录的用户 ID 列表
        user_ids = IdentifyStarsJob.list_recent_user_ids(db_session, days=30)
        logger.info(f"Sending recommendation emails to up to {len(user_ids)} users")

        for user_id in user_ids:
            try:
                await _send_one(db_session, user_id, today)
            except Exception as e:
                # 单个用户失败不影响其他用户，记录错误后继续
                logger.error(f"Failed to send recommendation to user {user_id}: {e}")
    finally:
        # 无论是否出错都确保关闭数据库连接
        db_session.close()


async def _send_one(db_session, user_id: int, today: date):
    """为单个用户计算并发送今晚的观星推荐邮件。"""
    # 查询用户基本信息，没有邮箱则跳过
    user = User.get_by_id(db_session, user_id)
    if not user or not user.email:
        logger.debug(f"Skipping user {user_id}: no email address")
        return

    profile = user.profile or {}
    sg = profile.get("stargazing_profile", {})

    # 今天已经发送过，跳过避免重复推送
    last_sent = sg.get("last_email_sent")
    if last_sent == today.isoformat():
        logger.debug(f"Skipping user {user_id}: email already sent today")
        return

    # 优先使用画像中记录的最近观测位置，否则回退到默认坐标
    lat = sg.get("last_lat", DEFAULT_LAT)
    lon = sg.get("last_lon", DEFAULT_LON)

    # 从画像中读取偏好星座和时间段，构建计数器供推荐函数使用
    from collections import Counter
    preferred_constellations = sg.get("preferred_constellations", [])
    preferred_hours = sg.get("preferred_hours", [])

    # 排名靠前的星座权重更高（第 1 位权重 5，之后依次递减，最低为 1）
    constellation_counter = Counter(
        {name: max(5 - i, 1) for i, name in enumerate(preferred_constellations)}
    )
    # 偏好观测时段统一赋予固定权重
    hour_counter = Counter({h: 10 for h in preferred_hours})

    # 计算月相、最佳观测时段、推荐星座及观测提示
    moon_phase = _get_moon_info(today)
    best_slots = await _fetch_top_slots(lat, lon, today, moon_phase.illumination)
    recommended_constellations = _build_constellation_recommendations(
        constellation_counter, today
    )
    tips = _generate_tips(moon_phase, best_slots, hour_counter, today)

    # 将模型对象转换为字典，供邮件模板填充
    slots_payload = [
        {
            "startTime": s.start_time.strftime("%H:%M"),
            "endTime": s.end_time.strftime("%H:%M"),
            "skyCondition": s.sky_condition or "",
            "score": s.score or 0,
        }
        for s in best_slots
    ]
    constellations_payload = [
        {"name": c.name, "reason": c.reason}
        for c in recommended_constellations
    ]

    # 发送邮件
    success = send_recommendation_email(
        to_email=user.email,
        username=user.username,
        date_str=today.strftime("%B %d, %Y"),
        moon_phase=moon_phase.phase,
        moon_illumination=int(moon_phase.illumination * 100),
        time_slots=slots_payload,
        constellations=constellations_payload,
        tips=tips,
    )

    if success:
        # 发送成功后将今天日期写入画像，防止当天重复发送
        current_profile = dict(profile)
        current_sg = dict(sg)
        current_sg["last_email_sent"] = today.isoformat()
        current_profile["stargazing_profile"] = current_sg
        User.update_profile_by_id(db_session, user_id, current_profile)
        logger.info(f"Recommendation email sent and recorded for user {user_id}")
