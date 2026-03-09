import pytest
from backend.console.utils.snowflake import id_worker


def test_snowflake_generate_id():
    """测试 Snowflake ID 是否能正常生成，且为整数"""
    new_id = id_worker.get_id()
    assert isinstance(new_id, int)
    assert new_id > 0


def test_snowflake_id_is_increasing():
    """测试连续生成的 ID 是否严格递增"""
    id1 = id_worker.get_id()
    id2 = id_worker.get_id()
    id3 = id_worker.get_id()

    assert id2 > id1
    assert id3 > id2