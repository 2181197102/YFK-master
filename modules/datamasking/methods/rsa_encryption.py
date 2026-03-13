"""
RSA加密方法实现
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat, PrivateFormat, NoEncryption
)
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
import base64
from typing import Tuple


class RSAEncryption:
    """RSA加密处理器"""
    
    def generate_rsa_keys(self) -> Tuple[bytes, bytes]:
        """
        生成RSA公钥和私钥
        
        Returns:
            Tuple[私钥PEM, 公钥PEM]
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        # 序列化私钥
        private_pem = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        )
        
        # 序列化公钥
        public_pem = public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    def encrypt_id_number(self, public_key_pem: bytes, id_number: str) -> str:
        """
        使用公钥加密身份证号
        
        Args:
            public_key_pem: 公钥PEM格式
            id_number: 身份证号
            
        Returns:
            加密后的身份证号(base64编码)
        """
        public_key = load_pem_public_key(public_key_pem)
        encrypted_id = public_key.encrypt(
            id_number.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted_id).decode('utf-8')
    
    def decrypt_id_number(self, private_key_pem: bytes, encrypted_id: str) -> str:
        """
        使用私钥解密身份证号
        
        Args:
            private_key_pem: 私钥PEM格式
            encrypted_id: 加密的身份证号(base64编码)
            
        Returns:
            解密后的身份证号
        """
        private_key = load_pem_private_key(private_key_pem, password=None)
        encrypted_id_bytes = base64.b64decode(encrypted_id)
        decrypted_id = private_key.decrypt(
            encrypted_id_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_id.decode('utf-8')

