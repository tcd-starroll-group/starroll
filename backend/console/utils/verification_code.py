"""验证码存储工具（用于忘记密码、注册等场景）"""
from typing import Optional

from backend.config import settings
from backend.console.dal.cache import VerificationCodeDAO


class VerificationCodeStore:
    """验证码存储类（使用DAL层获取Redis操作）"""
    def __init__(self):
        # 使用DAL层的验证码操作类
        self.dao = VerificationCodeDAO(settings)

    def generate_verification_code(self, length: int = 6) -> str:
        """生成6位数字验证码"""
        return self.dao.generate_code(length)

    def save_verification_code(self, target: str, code: Optional[str] = None) -> str:
        """保存验证码到Redis，返回生成的验证码"""
        return self.dao.save_code(target, code)

    def verify_verification_code(self, target: str, code: str) -> bool:
        """验证验证码是否有效（验证成功后删除，实现一次使用）"""
        return self.dao.verify_code(target, code)


# 全局单例实例（核心：必须在文件顶层定义，且命名完全一致）
verification_code_store = VerificationCodeStore()