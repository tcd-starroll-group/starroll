import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import backend.cronjob.send_stargazing_recommendation_email as email_module
from backend.cronjob.send_stargazing_recommendation_email import (
    send_stargazing_recommendation_email_handler,
    _send_one,
)
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob
from backend.console.dal.rds.user import User


# ---------------------------------------------------------------------------
# 测试辅助函数
# ---------------------------------------------------------------------------

def _mock_user(user_id=1, email="user@test.com", profile=None):
    """构造一个带有默认观星画像的模拟用户对象。"""
    user = MagicMock()
    user.id = user_id
    user.username = "stargazer"
    user.email = email
    user.profile = profile or {
        "stargazing_profile": {
            "preferred_constellations": ["Orion", "Leo"],  # 偏好星座列表
            "preferred_hours": [22, 23],                   # 偏好观测时段
            "last_lat": 53.35,                             # 上次观测纬度
            "last_lon": -6.26,                             # 上次观测经度
        }
    }
    return user


def _setup_send_one_mocks(monkeypatch, user=None, fetch_slots=None):
    """
    为 _send_one 的所有外部依赖打桩，返回 send_recommendation_email 的 mock 对象。
    默认行为：用户存在、未发送过邮件、天气接口返回空列表、发送成功。
    """
    monkeypatch.setattr(User, "get_by_id", MagicMock(return_value=user or _mock_user()))
    monkeypatch.setattr(
        email_module, "_fetch_top_slots",
        AsyncMock(return_value=fetch_slots or []),  # 替换天气接口，避免真实网络请求
    )
    monkeypatch.setattr(
        email_module, "_get_moon_info",
        MagicMock(return_value=MagicMock(phase="Waxing Crescent", illumination=0.25)),
    )
    monkeypatch.setattr(
        email_module, "_build_constellation_recommendations",
        MagicMock(return_value=[]),  # 替换推荐逻辑，返回空列表
    )
    monkeypatch.setattr(
        email_module, "_generate_tips",
        MagicMock(return_value=["Clear skies expected tonight."]),
    )
    # 替换实际 SMTP 发送，返回成功
    send_fn = MagicMock(return_value=True)
    monkeypatch.setattr(email_module, "send_recommendation_email", send_fn)
    monkeypatch.setattr(User, "update_profile_by_id", MagicMock())
    return send_fn


# ===========================================================================
# 测试：定时任务入口 send_stargazing_recommendation_email_handler
# ===========================================================================

class TestSendStargazingRecommendationEmailHandler:

    def test_runs_without_error_when_no_active_users(self, monkeypatch):
        """没有活跃用户时，任务应静默完成，不抛出任何异常。"""
        monkeypatch.setattr(email_module, "get_db", lambda: iter([MagicMock()]))
        monkeypatch.setattr(
            IdentifyStarsJob, "list_recent_user_ids", MagicMock(return_value=[])
        )
        send_stargazing_recommendation_email_handler()  # 不应抛出异常

    def test_calls_send_one_for_each_user(self, monkeypatch):
        """每个活跃用户都应被调用一次 _send_one。"""
        monkeypatch.setattr(email_module, "get_db", lambda: iter([MagicMock()]))
        monkeypatch.setattr(
            IdentifyStarsJob, "list_recent_user_ids", MagicMock(return_value=[1, 2, 3])
        )
        processed = []

        async def _mock_send(db, user_id, today):
            processed.append(user_id)

        monkeypatch.setattr(email_module, "_send_one", _mock_send)
        send_stargazing_recommendation_email_handler()
        assert sorted(processed) == [1, 2, 3]

    def test_continues_after_one_user_fails(self, monkeypatch):
        """单个用户处理失败时，不应中断其他用户的处理流程。"""
        monkeypatch.setattr(email_module, "get_db", lambda: iter([MagicMock()]))
        monkeypatch.setattr(
            IdentifyStarsJob, "list_recent_user_ids", MagicMock(return_value=[1, 2, 3])
        )
        attempted = []

        async def _flaky_send(db, user_id, today):
            attempted.append(user_id)
            if user_id == 2:
                raise Exception("SMTP error")  # 模拟第 2 个用户发送失败

        monkeypatch.setattr(email_module, "_send_one", _flaky_send)
        send_stargazing_recommendation_email_handler()  # 不应抛出异常
        assert sorted(attempted) == [1, 2, 3]  # 三个用户都被尝试处理

    def test_db_session_always_closed(self, monkeypatch):
        """即使查询活跃用户时抛出异常，数据库连接也必须被关闭。"""
        mock_db = MagicMock()
        monkeypatch.setattr(email_module, "get_db", lambda: iter([mock_db]))
        monkeypatch.setattr(
            IdentifyStarsJob, "list_recent_user_ids",
            MagicMock(side_effect=Exception("DB exploded")),
        )
        send_stargazing_recommendation_email_handler()
        mock_db.close.assert_called_once()  # 确保 finally 块中 close() 被调用


# ===========================================================================
# 测试：单用户发送逻辑 _send_one
# ===========================================================================

class TestSendOne:

    def test_skips_user_with_no_email(self, monkeypatch):
        """没有注册邮箱的用户应被跳过，不触发发送。"""
        user = _mock_user(email=None)
        monkeypatch.setattr(User, "get_by_id", MagicMock(return_value=user))
        send_fn = MagicMock()
        monkeypatch.setattr(email_module, "send_recommendation_email", send_fn)

        asyncio.run(_send_one(MagicMock(), 1, date.today()))
        send_fn.assert_not_called()

    def test_skips_if_already_sent_today(self, monkeypatch):
        """今天已经发送过推荐邮件的用户应被跳过，防止重复打扰。"""
        today = date.today()
        user = _mock_user(profile={
            "stargazing_profile": {
                "preferred_constellations": [],
                "preferred_hours": [],
                "last_email_sent": today.isoformat(),  # 今天已发送
            }
        })
        monkeypatch.setattr(User, "get_by_id", MagicMock(return_value=user))
        send_fn = MagicMock()
        monkeypatch.setattr(email_module, "send_recommendation_email", send_fn)

        asyncio.run(_send_one(MagicMock(), 1, today))
        send_fn.assert_not_called()

    def test_sends_email_when_not_sent_today(self, monkeypatch):
        """符合条件（有邮箱且今天未发送）的用户应触发一次邮件发送。"""
        send_fn = _setup_send_one_mocks(monkeypatch)
        asyncio.run(_send_one(MagicMock(), 1, date.today()))
        send_fn.assert_called_once()

    def test_records_last_email_sent_after_success(self, monkeypatch):
        """邮件发送成功后，应将今天的日期写入用户画像的 last_email_sent 字段。"""
        _setup_send_one_mocks(monkeypatch)
        update_fn = MagicMock()
        monkeypatch.setattr(User, "update_profile_by_id", update_fn)

        today = date.today()
        asyncio.run(_send_one(MagicMock(), 1, today))

        update_fn.assert_called_once()
        # 验证写入的画像中包含正确的 last_email_sent 日期
        updated_profile = update_fn.call_args[0][2]
        assert updated_profile["stargazing_profile"]["last_email_sent"] == today.isoformat()

    def test_does_not_record_if_send_fails(self, monkeypatch):
        """邮件发送失败时，不应更新用户画像，避免错误地标记为"已发送"。"""
        _setup_send_one_mocks(monkeypatch)
        monkeypatch.setattr(email_module, "send_recommendation_email", MagicMock(return_value=False))
        update_fn = MagicMock()
        monkeypatch.setattr(User, "update_profile_by_id", update_fn)

        asyncio.run(_send_one(MagicMock(), 1, date.today()))
        update_fn.assert_not_called()  # 发送失败，不写入画像

    def test_uses_default_location_when_none_in_profile(self, monkeypatch):
        """画像中没有位置信息时，应使用默认坐标（都柏林）获取天气数据。"""
        user = _mock_user(profile={
            "stargazing_profile": {
                "preferred_constellations": [],
                "preferred_hours": [],
                # 未设置 last_lat / last_lon，触发默认坐标逻辑
            }
        })
        monkeypatch.setattr(User, "get_by_id", MagicMock(return_value=user))
        fetch_mock = AsyncMock(return_value=[])
        monkeypatch.setattr(email_module, "_fetch_top_slots", fetch_mock)
        monkeypatch.setattr(
            email_module, "_get_moon_info",
            MagicMock(return_value=MagicMock(phase="New Moon", illumination=0.01)),
        )
        monkeypatch.setattr(email_module, "_build_constellation_recommendations", MagicMock(return_value=[]))
        monkeypatch.setattr(email_module, "_generate_tips", MagicMock(return_value=[]))
        monkeypatch.setattr(email_module, "send_recommendation_email", MagicMock(return_value=True))
        monkeypatch.setattr(User, "update_profile_by_id", MagicMock())

        asyncio.run(_send_one(MagicMock(), 1, date.today()))

        # 验证天气接口被传入了默认坐标
        call_args = fetch_mock.call_args[0]
        assert call_args[0] == email_module.DEFAULT_LAT
        assert call_args[1] == email_module.DEFAULT_LON

    def test_skips_user_not_in_db(self, monkeypatch):
        """数据库中不存在的用户 ID 应被安全跳过，不触发任何发送操作。"""
        monkeypatch.setattr(User, "get_by_id", MagicMock(return_value=None))
        send_fn = MagicMock()
        monkeypatch.setattr(email_module, "send_recommendation_email", send_fn)

        asyncio.run(_send_one(MagicMock(), 9999, date.today()))
        send_fn.assert_not_called()
