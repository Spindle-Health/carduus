from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.hashes import Hash, SHAKE256

from pyspark.sql import SparkSession


__all__ = [
    "generate_pem_files",
    "EncryptionKeyService",
    "SparkConfKeyService",
    "InMemoryKeyService",
]


def generate_pem_files(
    private_key_filename: PathLike,
    public_key_filename: PathLike,
    passphrase: bytes | None = None,
):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    if Path(private_key_filename).exists():
        raise IOError(
            f"{private_key_filename} already exists. Be careful when changing PEM files; existing tokens may become unreadable."
        )
    with open(private_key_filename, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=(
                    serialization.BestAvailableEncryption(passphrase)
                    if passphrase
                    else serialization.NoEncryption()
                ),
            )
        )
    with open(public_key_filename, "wb") as f:
        f.write(
            private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )


class EncryptionKeyService(ABC):
    """Abstract base class for key services. Can be implemented to call out whichever
    service you use to manage encryption keys.
    """

    @abstractmethod
    def private_key(self) -> bytes:
        """Provides your private key."""
        pass

    @abstractmethod
    def public_key_of(self, profile: str) -> bytes:
        """Provides the public key of a specific profiles (aka partner) that you share data with."""
        pass

    def aes_key(self) -> bytes:
        digest = Hash(SHAKE256(32))
        digest.update(self.private_key())
        return digest.finalize()


def _profile_public_key_not_found(service: EncryptionKeyService, profile: str):
    return KeyError(
        f"No public key for profile {profile} found in {service.__class__.__qualname__}."
    )


class InMemoryKeyService(EncryptionKeyService):
    def __init__(
        self,
        private_key: bytes,
        public_keys: dict[str, bytes],
    ):
        self._private_key = private_key
        self.public_keys = public_keys

    def private_key(self) -> bytes:
        return self._private_key

    def public_key_of(self, profile: str) -> bytes:
        key = self.public_keys.get(profile)
        if not key:
            raise _profile_public_key_not_found(self, profile)
        return key

    def add_profile(self, profile: str, key: bytes):
        self.public_keys[profile] = key


class SparkConfKeyService(EncryptionKeyService):
    ENCRYPTED_PRIVATE_KEY_CONF = "carduus.token.privateKey"
    PUBLIC_KEY_PROFILE_CONF = "carduus.token.publicKey.{profile}"

    def private_key(self) -> bytes:
        pem = self._read_conf()
        key = serialization.load_pem_private_key(pem, None)
        assert isinstance(key, rsa.RSAPrivateKey)
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    def public_key_of(self, profile: str) -> bytes:
        pem = self._read_conf(profile)
        key = serialization.load_pem_public_key(pem, None)
        assert isinstance(key, rsa.RSAPublicKey)
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def add_profile(self, profile: str, key: bytes):
        SparkSession.active().conf.set(
            self.PUBLIC_KEY_PROFILE_CONF.format(profile=profile), key.decode("utf-8")
        )

    def _read_conf(self, profile: str | None = None) -> bytes:
        conf_key = (
            self.PUBLIC_KEY_PROFILE_CONF.format(profile=profile)
            if profile
            else self.ENCRYPTED_PRIVATE_KEY_CONF
        )
        # @TODO Consider improving the error message when conf key is not found.
        conf_val = SparkSession.active().conf.get(conf_key)
        assert conf_val, f"No spark config {conf_key} set."
        return conf_val.encode()
