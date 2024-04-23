# Carduus

The open source implementation of the Open Privacy Preserving Record Linkage (OPPRL) protocol build on Spark.

## Rationale

Privacy Preserving Record Linkage (PPRL) systems are used to obfuscate identifying attributes or other sensitive information about the subjects described in the records of a dataset while still preserving the ability to link records pertaining to the same subject through the use of an encrypted token. This practice is sometimes referred to as "tokenization" and is one of the components of data deidenfication.

The task of PPRL is to replace the attributes of a every record denoting Personally Identifiable Information (PII) with a token produced by a one-way cryptographic function. This prevents observers of the tokenized data from reversing the token into the sensitive PII attributes. The tokens are produced deterministically such that input records with the same, or similar, PII attributes will produce an identical token. This allows user of multiple tokenized data assets to associate records that are highly likely to belong to the same data subject without having acces to PII.

Tokenization is also used when data is shared between organizations to limit the scope of damages in the event that one organization's data is compromised. Each party's tokens are created via encryption using a different secret key so that any compromised data asset is only matchable to other datasets mantained by the same party. During data sharing transactions, a specific "transcryption" data flow is used to re-encrpt the sender's tokens into tokens that match the receipient's data without recovering the underlying PII.

Carduus is the first (and canonical) implemenation of the Open Privacy Preserving Record Linkage (OPPRL) specification. This specification presents a standardized methodology for tokenization that can be implemented in any data system to increase interoperability. The carduus implementation is a python library that distributes the tokenization workload using apache [Spark](https://spark.apache.org/).

## Getting Started

> Warning: The first release `carduus` library has not yet been published to PyPi but can be installed from source.

You can install the `carduus` library into your Python environment using `pip`

```
pip install carduus
```

See the full API documentation and an example usage for further documentaiton.

## Contributing

See `CONTRIBUTING.md` for a guide on how to contribute to Carduus.
