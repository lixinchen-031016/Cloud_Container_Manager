"""
密码加密模块
使用 cryptography 库进行密码加密和解密
"""
import os
import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PasswordEncryptor:
    """密码加密器"""
    
    def __init__(self):
        self._key: Optional[bytes] = None
        self._salt: Optional[bytes] = None
        self._cipher: Optional[Fernet] = None
    
    def _get_key(self) -> bytes:
        """获取或生成加密密钥"""
        if self._key is None:
            # 使用机器标识作为基础（简化方案，生产环境应使用更安全的密钥管理）
            machine_id = str(os.uname()).encode('utf-8')
            salt = b'cloud_container_manager_salt_v1'  # 固定盐值
            
            # 使用 PBKDF2 派生密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            self._key = base64.urlsafe_b64encode(kdf.derive(machine_id))
        
        return self._key
    
    def encrypt(self, password: str) -> str:
        """
        加密密码
        
        Args:
            password: 明文密码
            
        Returns:
            Base64 编码的加密密码
        """
        if not password:
            return ""
        
        cipher = Fernet(self._get_key())
        encrypted = cipher.encrypt(password.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_password: str) -> str:
        """
        解密密码
        
        Args:
            encrypted_password: Base64 编码的加密密码
            
        Returns:
            明文密码
        """
        if not encrypted_password:
            return ""
        
        try:
            cipher = Fernet(self._get_key())
            decrypted = cipher.decrypt(base64.b64decode(encrypted_password.encode('utf-8')))
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"[PasswordEncryptor] 解密失败：{e}")
            return ""


# 全局单例
_encryptor: Optional[PasswordEncryptor] = None


def get_encryptor() -> PasswordEncryptor:
    """获取密码加密器单例"""
    global _encryptor
    if _encryptor is None:
        _encryptor = PasswordEncryptor()
    return _encryptor


def encrypt_password(password: str) -> str:
    """加密密码的便捷函数"""
    return get_encryptor().encrypt(password)


def decrypt_password(encrypted_password: str) -> str:
    """解密密码的便捷函数"""
    return get_encryptor().decrypt(encrypted_password)
