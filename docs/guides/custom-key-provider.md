# Implementing Custom Key Providers

One of Carduus's primary design goals is to be usable in any context with a compatible Python environment. A wide variety of users and organizations may want to use Carduus and this implies many different preferred ways of managing secrets, including encryption keys. The direct users of Carduus may not be authorized to see all encryption keys and there may be layers of authentication and access control that are required before Carduus can be deployed within an organization.

Over time, Carduus hopes to provide built-in integrations to commonly used secret management services. For example, Carduus's default method of retrieving keys from Spark session properties is well aligned with the model of how [Databricks manages secrets](https://docs.databricks.com/en/security/secrets/secrets.html).

In scenarios where Carduus does not supply a method of accessing secrets that meets your organization's requirements, you can extend the `EncryptionKeyProvider` abstract base class with your own implementation and provide an instance of your implementation to all of the relevant Carduus functions.

## The `EncryptionKeyProvider` Interface

The `EncryptionKeyProvider` base class has two abstract methods that must be defined in it's concrete implementations. The following code snippet shows the signatures of these methods.

```python
class EncryptionKeyProvider(ABC):

    @abstractmethod
    def private_key(self) -> bytes:
        """Provides your private key."""
        ...

    @abstractmethod
    def public_key_of(self, recipient: str) -> bytes:
        """Provides the public key of a specific recipient that you share data with."""
        ...
```

The `private_key` method returns a instance of `bytes` that contains your organization's private RSA key in the [PKCS #8](https://en.wikipedia.org/wiki/PKCS_8) format using the [PEM](https://en.wikipedia.org/wiki/Privacy-Enhanced_Mail) encoding. This Should begin with `b"-----BEGIN PRIVATE KEY-----\n"` and end with `b"\n-----END PRIVATE KEY-----\n"` with base64 encoded bytes in between.

The `public_key_of` method should perform some kind of lookup to return the public RSA key of the given recipient. If found, the public key should be represented as an instance of `bytes` in the [SubjectPublicKeyInfo](https://www.rfc-editor.org/rfc/rfc5280#section-4.1) format using the [PEM](https://en.wikipedia.org/wiki/Privacy-Enhanced_Mail) encoding. This Should begin with `b"-----BEGIN PUBLIC KEY-----\n"` and end with `b"\n-----END PUBLIC KEY-----\n"` with base64 encoded bytes in between. If the lookup fails to find a public key for the given recipient, it is recommended that a Python `KeyError` is raised.

## Contributing Key Providers

If you implement an `EncryptionKeyProvider` for a general purposes and publicly available secret management system, a contribution Carduus is encouraged. See the [contributing](../CONTRIBUTING.md) guide for more information.
