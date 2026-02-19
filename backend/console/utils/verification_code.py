"""验证码存储工具（用于忘记密码、注册等场景）"""
import time
import random
from typing import Dict, Optional


class VerificationCodeStore:
    """验证码存储类（单例模式）"""
    def __init__(self):
        # 存储结构：{target: {"code": str, "expire_at": float}}
        self.store: Dict[str, Dict[str, str | float]] = {}
        self.code_expire_seconds: int = 300  # 验证码有效期5分钟

    def generate_verification_code(self, length: int = 6) -> str:
        """生成6位数字验证码"""
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])

    def save_verification_code(self, target: str, code: Optional[str] = None) -> str:
        """保存验证码，返回生成的验证码"""
        if code is None:
            code = self.generate_verification_code()
        expire_at = time.time() + self.code_expire_seconds
        self.store[target] = {"code": code, "expire_at": expire_at}
        return code

    def verify_verification_code(self, target: str, code: str) -> bool:
        """验证验证码是否有效（验证成功后删除，实现一次使用）"""
        if target not in self.store:
            return False
        
        record = self.store[target]
        # 检查是否过期
        if time.time() > record["expire_at"]:
            del self.store[target]
            return False
        
        # 检查验证码是否匹配
        if record["code"] == code:
            del self.store[target]  # 验证成功后删除，实现一次使用
            return True
        return False

    def clear_expired(self):
        """清理所有过期的验证码"""
        current_time = time.time()
        # 遍历所有记录，删除过期的
        expired_targets = [
            target for target, record in self.store.items()
            if record["expire_at"] < current_time
        ]
        for target in expired_targets:
            del self.store[target]


# 全局单例实例（核心：必须在文件顶层定义，且命名完全一致）
verification_code_store = VerificationCodeStore()