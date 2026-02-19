import time
import pytest
from unittest.mock import patch

from backend.console.utils.verification_code import VerificationCodeStore


class TestVerificationCodeStore:

    def setup_method(self):
        """每个测试方法前创建新的 store 实例"""
        self.store = VerificationCodeStore()

    def test_generate_code_returns_6_digits(self):
        # 修改点：拆分「生成验证码」和「保存验证码」（适配类的实际方法）
        code = self.store.generate_verification_code()
        self.store.save_verification_code("test@example.com", code)
        assert len(code) == 6
        assert code.isdigit()

    def test_verify_code_success(self):
        # 修改点：拆分生成+保存，验证方法名改为类的实际方法名
        code = self.store.generate_verification_code()
        self.store.save_verification_code("test@example.com", code)
        result = self.store.verify_verification_code("test@example.com", code)
        assert result is True

    def test_verify_code_wrong_code(self):
        # 修改点：拆分生成+保存，验证方法名修正
        code = self.store.generate_verification_code()
        self.store.save_verification_code("test@example.com", code)
        result = self.store.verify_verification_code("test@example.com", "000000")
        assert result is False

    def test_verify_code_email_not_found(self):
        # 修改点：验证方法名修正
        result = self.store.verify_verification_code("unknown@example.com", "123456")
        assert result is False

    def test_verify_code_expired(self):
        # 修改点1：拆分生成+保存；修改点2：适配类的存储结构（dict而非元组）
        code = self.store.generate_verification_code()
        self.store.save_verification_code("test@example.com", code)

        # 模拟时间过期（适配类的存储结构：{"code": 验证码, "expire_at": 过期时间}）
        self.store.store["test@example.com"]["expire_at"] = time.time() - 1

        result = self.store.verify_verification_code("test@example.com", code)
        assert result is False

    def test_verify_code_one_time_use(self):
        """验证码只能使用一次"""
        # 修改点：拆分生成+保存，验证方法名修正
        code = self.store.generate_verification_code()
        self.store.save_verification_code("test@example.com", code)

        # 第一次验证应该成功
        assert self.store.verify_verification_code("test@example.com", code) is True

        # 第二次验证应该失败（已被删除）
        assert self.store.verify_verification_code("test@example.com", code) is False

    def test_generate_code_overwrites_previous(self):
        """重新生成验证码会覆盖旧的"""
        # 修改点：拆分生成+保存（两次生成+保存，模拟覆盖）
        code1 = self.store.generate_verification_code()
        self.store.save_verification_code("test@example.com", code1)
        
        code2 = self.store.generate_verification_code()
        self.store.save_verification_code("test@example.com", code2)

        # 旧验证码不再有效
        if code1 != code2:
            assert self.store.verify_verification_code("test@example.com", code1) is False

    def test_clear_expired(self):
        # 修改点1：拆分生成+保存；修改点2：适配存储结构；修改点3：修正存储属性名（store而非_store）
        code = self.store.generate_verification_code()
        self.store.save_verification_code("test@example.com", code)
        
        # 手动设为过期
        self.store.store["test@example.com"]["expire_at"] = time.time() - 1

        self.store.clear_expired()
        assert "test@example.com" not in self.store.store