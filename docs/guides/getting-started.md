# Getting Started

This guide provides a quick tour of the main features of Carduus, including instructions for how most users will be interacting with the library.

> :warning: Carduus has not reached a v1.0 release yet and therefore the API and behaviors are subject to change. **Use at your own risk!** See the [contributing](../CONTRIBUTING.md) guide if you would like to help the project.

## Installation

Carduus is a cross-platform python library built on top of PySpark. It supports the following range of versions:

- Python: 3.10+
- PySpark: 3.5+

The latest stable release of carduus can be installed from [PyPI](https://pypi.org/project/carduus/) into your active Python environment using `pip`.

```
pip install carduus
```

You can also build Carduus from source using [Poetry](https://python-poetry.org/). The source code is hosted [on Github](https://github.com/Spindle-Health/carduus). Checkout the commit you wish to build and run  `poetry build` in the project's root.

## Encryption Keys

Carduus's tokenization capabilities require the use of private and public encryption keys. Carduus users are expected to manage their own encryption keys.

There are 3 kinds of encryption keys that play different roles:

  1. Your private RSA key - Used to transcrypt incoming data and derive a symmetric encryption key used to tokenize PII. **This key must never be shared or accessed by untrusted parties.**
  2. Your public RSA key - The public key counterpart to your private key. Will be shared with trusted parties that will be sending you tokenized data.
  3. Trusted partner public keys - A collection of public keys from the various trusted parties that you will be sending tokenized to.

### Generating New Keys

Carduus expects encryption keys to be represented the [PEM](https://en.wikipedia.org/wiki/Privacy-Enhanced_Mail) encoding. Private keys should use the [PKCS #8](https://en.wikipedia.org/wiki/PKCS_8) format and public keys should be formatted as [SubjectPublicKeyInfo](https://www.rfc-editor.org/rfc/rfc5280#section-4.1). Carduus recommends a key size of 2048 bits.

You can generate these keys using tools like [`openssl`](https://www.openssl.org/) or by calling the `generate_pem_keys` function provided by Carduus. This function will return a `tuple` containing 2 instances of `bytes`. The first is the PEM data for your private key that you must keep secret. The second is the PEM data for your public key that can may share with the parties you intend to receive data from.

You can decode these keys into strings of text (using UTF-8) or write them into a `.pem` file for later use. 

``` python
from carduus.keys import generate_pem_keys

private, public = generate_pem_keys()  # Or provide key_size= 

print(private.decode())
# -----BEGIN PRIVATE KEY-----
# ... [ Base64-encoded private key ] ...
# -----END PRIVATE KEY-----

print(public.decode())
# -----BEGIN PUBLIC KEY-----
# ... [ Base64-encoded public key ] ...
# -----END PUBLIC KEY-----
```

## Tokenization

Tokenization refers to the process of replacing PII with encrypted tokens using a one-way cryptographic function. Carduus implements the OPPRL tokenization protocol, which performs a standard set of PII normalizations and enhancements such that records pertaining to the same subject are more likely to receive the same token despite minor differences in PII representation across records. The OPPRL protocol hashes the normalized PII and then encrypts the hashes with a symmetric encryption based on a secret key derived from your private RSA key. In the event that the private encryption key of one party is compromised, there risk to all other parties is mitigated by the fact that everyone's tokens are encrypted with a different key.

To demonstrate the tokenization process, we will use a dataset of 5 records shown below. Each record is assigned a `label` that corresponds to the true identity of the subject.

```python
pii = spark.createDataFrame(
    [
        (1, "Jonas", "Salk", "male", "1914-10-28"),
        (1, "jonas", "salk", "M", "1914-10-28"),
        (2, "Elizabeth", "Blackwell", "F", "1821-02-03"),
        (3, "Edward", "Jenner", "m", "1749-05-17"),
        (4, "Alexander", "Fleming", "M", "1881-08-06"),
    ],
    ("label", "first_name", "last_name", "gender", "birth_date")
)
pii.show()
# +-----+----------+---------+------+----------+
# |label|first_name|last_name|gender|birth_date|
# +-----+----------+---------+------+----------+
# |    1|     Jonas|     Salk|  male|1914-10-28|
# |    1|     jonas|     salk|     M|1914-10-28|
# |    2| Elizabeth|Blackwell|     F|1821-02-03|
# |    3|    Edward|   Jenner|     m|1749-05-17|
# |    4| Alexander|  Fleming|     M|1881-08-06|
# +-----+----------+---------+------+----------+
```

To perform tokenization, call the `tokenize` function and pass it the PII `DataFrame`, a column mapping, and a collection of specifications for token you want to generate. You may optionally pass an instance of `EncryptionKeyProvider`, but all code snippets shown in this guide assume the default key service is used (unless otherwise specified) and therefore encryption keys will be read from the spark session properties.

```python
from carduus.token import tokenize, OpprlPii, OpprlToken
tokens = tokenize(
    pii,
    pii_transforms=dict(
        first_name=OpprlPii.first_name,
        last_name=OpprlPii.last_name,
        gender=OpprlPii.gender,
        birth_date=OpprlPii.birth_date,
    ),
    tokens=[OpprlToken.token1, OpprlToken.token2],
    private_key=b"""-----BEGIN PRIVATE KEY----- ...""",
)
# +-----+--------------------+--------------------+
# |label|       opprl_token_1|       opprl_token_2|
# +-----+--------------------+--------------------+
# |    1|d2tUj3yRFPIBSwR/n...|DQhKG+AMgrFh16dLi...|
# |    1|d2tUj3yRFPIBSwR/n...|DQhKG+AMgrFh16dLi...|
# |    2|2wnRWhN9Y4DBMeuvw...|A7fUKAZi/Ra2T6p8y...|
# |    3|I17X+CT3kjqB9l0rA...|qGCUVyI7MJLkQ9SSr...|
# |    4|6Ee3NabHaa/lyKsrp...|dbwNqy0rN6hFoHJYn...|
# +-----+--------------------+--------------------+
```

Notice that both records with `label = 1` received the same pair of tokens despite slight representation differences in the original PII.

The `pii_transforms` argument is a dictionary that maps column names from the `pii` DataFrame to the corresponding OPPRL PII field. This tells Carduus how to normalize and enhance the values found in that column. For example, the `OpprlPii.first_name` object will apply name cleaning rules to the values found in the `first_name` column and automatically derive additional PII columns called `first_initial` and `first_soundex` which are used to create both OPPRL tokens.

The `tokens` argument is collection of OPPRL token specifications that tell Carduus which PII fields to jointly hash and encrypt to create each token. The current OPPRL protocol supports three token specifications, described below:

| Token | Fields to jointly encrypt |
|-|-|
| `OpprlToken.token1` | `first_initial`, `last_name`, `gender`, `birth_date` |
| `OpprlToken.token2` | `first_soundex`, `last_soundex`, `gender`, `birth_date` |
| `OpprlToken.token3` | `first_metaphone`, `last_metaphone`, `gender`, `birth_date` |

> :bulb: **Why multiple tokens?** 
>
> Each use case has a different tolerance for false positive and false negative matches. By producing multiple tokens for each record using PII attributes, each user can customize their match logic to trade-off between different kinds of match errors. Linking records that match on _any_ token will result in fewer false negatives, and linking records that match _all_ tokens will result in fewer false positives. User can design their own match strategies by using subsets of tokens.

## Transcryption

> :book: noun: _trans-_ (latin: across) _-crypt_ (greek: hidden, secret)
>
> The process of transforming a ciphertext produced by one encryption into a ciphertext of a different encryption without emitting the original plaintext.

Transcryption is performed when a user wants to share tokenized data with another party. The sender and recipient each have a corresponding transcryption function that must be invoked to ensure safe transfer of data between trusted parties. The sender performs transcryption to replace their tokens with "ephemeral tokens" that are specific to the transaction. In other words, the ephemeral tokens do not match the sender's tokens, the recipients data, or the ephemeral tokens from prior transactions between _any_ sender and recipient. 

Furthermore, records from the same dataset that have identical PII will be assigned unique ephemeral tokens. This destroys the utility of the tokens until the recipient performs the reverse transcryption process using their private key. This is beneficial in the event that a third party gains access to the dataset during transfer (eg. an if transcrypted datasets are delivered over an insecure connection) because records pertaining to the same subject cannot be associated with each other.

### Sender

Carduus provides the `transcrypt_out` function in for the sender to call on their tokenized datasets. In the following code snippet, notice the 2 records pertaining to the same subject (`label = 1`) no longer have identical tokens. The `tokens_to_send` DataFrame can safely be written files or a database and delivered to the recipient.

```python
tokens_to_send = transcrypt_out(
    tokens, 
    token_columns=("opprl_token_1", "opprl_token_3"), 
    recipient_public_key=b"""-----BEGIN PUBLIC KEY----- ...""".
    # This is the private key of the sender
    # It is NOT the private key associated with the recipient_public_key.
    private_key=b"""-----BEGIN PRIVATE KEY----- ...""",
)
tokens.to_send.show()
# +-----+--------------------+--------------------+
# |label|       opprl_token_1|       opprl_token_3|
# +-----+--------------------+--------------------+
# |    1|IL17HgISJv5ol+ftJ...|YPnfuGBBhbOZChlhR...|
# |    1|IVwfYY0dbmFc6cf0/...|jF8N2HYEYPr5lFSSx...|
# |    2|I5Oe3oC0heF8L+Zcy...|BkBPzMDXeKlprUd8l...|
# |    3|dOQtYZZV8j/E6wGMB...|FU6MbMjsU8WrJoiXa...|
# |    4|N0VzhvFHrTtWNt+P7...|jvbFTWbmBzB06lDpv...|
# +-----+--------------------+--------------------+
```

The `token_columns` argument is a iterable collection containing the column names of the `tokens` DataFrame that correspond to tokens that need to be transcrypted.

The `recipient` argument denotes the name given to the public key associated with the intended recipient. If using the default encryption key provider (via Spark session properties) the above code snippet will grab the public key from `carduus.token.publicKey.AcmeCorp` spark session property.

### Recipient

The `transcrypt_in` function provides the transcryption process for the recipient. It is called on a dataset produced by the sender using `transcrypt_out` to convert ephemeral tokens into normal tokens that will match other tokenized datasets maintained by the recipient, including prior datasets delivered from the same sender.

Notice that the first 2 records pertaining to the same subject (label = 1) have identical tokens again, but do these tokens are not the same as the original tokens because they are encrypted with the scheme for the recipient.

```python
from carduus.token import transcrypt_in

tokens_received = transcrypt_in(
    tokens_to_send, 
    token_columns=("opprl_token_1", "opprl_token_3"),
    # This is the private key corresponding to the public key used to the prepare the data.
    # It is NOT the private key used to tokenize the PII.
    private_key=b"""-----BEGIN PRIVATE KEY----- ...""",
)
tokens_received.show()
# +-----+--------------------+--------------------+
# |label|       opprl_token_1|       opprl_token_3|
# +-----+--------------------+--------------------+
# |    1|O47siK/9rItAv6lwa...|uoPojmvjl3Mk734Ul...|
# |    1|O47siK/9rItAv6lwa...|uoPojmvjl3Mk734Ul...|
# |    2|LfRQxBPEW0tEskwxt...|P9PLhpSz+kWSSVmYQ...|
# |    3|QWvpT0wMEezlurVFM...|W9BxmxZf1/yqIDx3W...|
# |    4|aS/BfI5qw8UnhOWUX...|nWfWyxQcrSfeiMEHr...|
# +-----+--------------------+--------------------+
```

As with `transcrypt_out`, the `token_columns` argument is a iterable collection containing the column names of the `tokens` DataFrame that correspond to tokens that need to be transcrypted. 

## Deployment

Carduus is a Python library that uses PySpark to parallelize and distribute the tokenization and transcryption workloads. Your application that uses Carduus can be submitted to any compatible Spark cluster, or use a connection to a remote spark cluster. Otherwise, Carduus will start a local Spark process that uses the resources of the host machine.

For more information about different modes of deployment, see the official Spark documentation.

- [Submitting Applications to a Spark cluster](https://spark.apache.org/docs/latest/submitting-applications.html)
- [Spark Connect](https://spark.apache.org/docs/latest/spark-connect-overview.html)
- [Spark Standalone Mode](https://spark.apache.org/docs/latest/spark-standalone.html)

## Next Steps

- Reference the full [API](../api.md)
- Learn more about using Carduus and extending it's functionality from the advanced user guides:
    - [Using Carduus on Databricks](./databricks.ipynb)
    - [Defining custom token specifications](./custom-tokens.md)
    - [Adding support for custom PII attributes](./custom-pii.md)
