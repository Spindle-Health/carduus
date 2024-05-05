from abc import ABC, abstractmethod
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.hashes import Hash, SHAKE256

from pyspark.sql import SparkSession


__all__ = [
    "generate_pem_keys",
    "EncryptionKeyProvider",
    "SparkConfKeyProvider",
    "SimpleKeyProvider",
]


def generate_pem_keys(key_size: int = 2048) -> tuple[bytes, bytes]:
    """Generates a fresh RSA key pair.

    Arguments:
        key_size:
            The size (in bits) of the key.

    Returns:
        A tuple containing the private key and public key bytes. Both in the PEM encoding.

    """
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    private = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private, public


class EncryptionKeyProvider(ABC):
    """Abstract base class for serving encryption keys to carduus. Can be implemented to call out to whichever
    service you use to manage encryption keys.
    """

    @abstractmethod
    def private_key(self) -> bytes:
        """Provides your private key."""
        ...

    @abstractmethod
    def public_key_of(self, recipient: str) -> bytes:
        """Provides the public key of a specific recipient that you share data with."""
        ...

    def aes_key(self) -> bytes:
        digest = Hash(SHAKE256(32))
        digest.update(self.private_key())
        return digest.finalize()


def _recipient_public_key_not_found(service: EncryptionKeyProvider, recipient: str):
    return KeyError(
        f"No public key for profile {recipient} found in {service.__class__.__qualname__}."
    )


class SimpleKeyProvider(EncryptionKeyProvider):
    def __init__(
        self,
        private_key: bytes,
        public_keys: dict[str, bytes],
    ):
        self._private_key = private_key
        self.public_keys = public_keys

    def private_key(self) -> bytes:
        return self._private_key

    def public_key_of(self, recipient: str) -> bytes:
        key = self.public_keys.get(recipient)
        if not key:
            raise _recipient_public_key_not_found(self, recipient)
        return key

    def add_profile(self, recipient: str, key: bytes):
        self.public_keys[recipient] = key


class SparkConfKeyProvider(EncryptionKeyProvider):
    PRIVATE_KEY_CONF = "carduus.token.privateKey"
    PUBLIC_KEY_CONF = "carduus.token.publicKey.{recipient}"

    def private_key(self) -> bytes:
        pem = self._read_conf()
        key = serialization.load_pem_private_key(pem, None)
        assert isinstance(key, rsa.RSAPrivateKey)
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    def public_key_of(self, recipient: str) -> bytes:
        pem = self._read_conf(recipient)
        key = serialization.load_pem_public_key(pem, None)
        assert isinstance(key, rsa.RSAPublicKey)
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def add_profile(self, recipient: str, key: bytes):
        SparkSession.active().conf.set(
            self.PUBLIC_KEY_CONF.format(recipient=recipient), key.decode("utf-8")
        )

    def _read_conf(self, recipient: str | None = None) -> bytes:
        conf_key = (
            self.PUBLIC_KEY_CONF.format(recipient=recipient)
            if recipient
            else self.PRIVATE_KEY_CONF
        )
        conf_val = SparkSession.active().conf.get(conf_key, None)
        if not conf_val:
            if recipient:
                raise _recipient_public_key_not_found(self, recipient)
            else:
                raise KeyError(
                    f'Carduus private key found. Did you set the Spark config "{self.PRIVATE_KEY_CONF}"?'
                )
        return conf_val.encode()
