#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compatibility layer for rsa module using cryptography library
This provides basic RSA functionality for Python 3.13+ compatibility
"""

try:
    import rsa
    # If rsa is available, use it directly
    from rsa import *
    from rsa.key import *
    from rsa.pkcs1 import *
    
except ImportError:
    # Fallback implementation using cryptography library
    from cryptography.hazmat.primitives.asymmetric import rsa as crypto_rsa
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    
    class DecryptionError(Exception):
        """RSA decryption error"""
        pass
    
    class PublicKey:
        """RSA Public Key compatible with rsa module"""
        
        def __init__(self, n, e):
            self.n = n
            self.e = e
            # Create cryptography public key
            public_numbers = crypto_rsa.RSAPublicNumbers(e, n)
            self._key = public_numbers.public_key()
        
        @classmethod
        def load_pkcs1(cls, pem_data):
            """Load public key from PEM format"""
            if isinstance(pem_data, str):
                pem_data = pem_data.encode('utf-8')
            
            key = serialization.load_pem_public_key(pem_data)
            public_numbers = key.public_numbers()
            return cls(public_numbers.n, public_numbers.e)
        
        def save_pkcs1(self, format='PEM'):
            """Save public key to PEM format"""
            pem = self._key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.PKCS1
            )
            return pem
    
    class PrivateKey:
        """RSA Private Key compatible with rsa module"""
        
        def __init__(self, n, e, d, p, q):
            self.n = n
            self.e = e
            self.d = d
            self.p = p
            self.q = q
            # Create cryptography private key
            private_numbers = crypto_rsa.RSAPrivateNumbers(
                p, q, d, crypto_rsa.RSAPublicNumbers(e, n).public_key().public_numbers()
            )
            self._key = private_numbers.private_key()
        
        @classmethod
        def load_pkcs1(cls, pem_data):
            """Load private key from PEM format"""
            if isinstance(pem_data, str):
                pem_data = pem_data.encode('utf-8')
            
            key = serialization.load_pem_private_key(pem_data, password=None)
            private_numbers = key.private_numbers()
            public_numbers = private_numbers.public_key().public_numbers()
            
            return cls(
                public_numbers.n,
                public_numbers.e,
                private_numbers.private_value,
                private_numbers.p,
                private_numbers.q
            )
        
        def save_pkcs1(self, format='PEM'):
            """Save private key to PEM format"""
            pem = self._key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            return pem
    
    def encrypt(message, pub_key):
        """Encrypt message with RSA public key"""
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        try:
            ciphertext = pub_key._key.encrypt(
                message,
                padding.PKCS1v15()
            )
            return ciphertext
        except Exception as e:
            raise DecryptionError(f"Encryption failed: {e}")
    
    def decrypt(ciphertext, priv_key):
        """Decrypt message with RSA private key"""
        try:
            plaintext = priv_key._key.decrypt(
                ciphertext,
                padding.PKCS1v15()
            )
            return plaintext
        except Exception as e:
            raise DecryptionError(f"Decryption failed: {e}")
    
    def newkeys(keysize):
        """Generate new RSA keypair"""
        private_key = crypto_rsa.generate_private_key(
            public_exponent=65537,
            key_size=keysize
        )
        
        private_numbers = private_key.private_numbers()
        public_numbers = private_numbers.public_key().public_numbers()
        
        pub_key = PublicKey(public_numbers.n, public_numbers.e)
        priv_key = PrivateKey(
            public_numbers.n,
            public_numbers.e,
            private_numbers.private_value,
            private_numbers.p,
            private_numbers.q
        )
        
        return pub_key, priv_key
    
    # Create compatibility module-level objects
    class pkcs1:
        DecryptionError = DecryptionError
    
    class key:
        PublicKey = PublicKey
        PrivateKey = PrivateKey