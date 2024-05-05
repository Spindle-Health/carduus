# OPPRL Protocol

> :warning: Warning! :warning: 
> This specification is incomplete. Many sections are missing and the existing details may change.
> If you are interested in contributing to the specification, see the [Contributing Guide](https://spindle-health.github.io/carduus/opprl/contrib/)

# Overview

This document is a specification for the Open Privacy Preserving Record Linkage (OPPRL) protocol, which brings ______. This capability is often refered to as "tokenization".  The protocol is designed with the following goals:

- **Interoperability -** Implementations can be created in many data systems while 
- **Security -** Carefully selected encryption algorithms are used at each point in the process to mitigate any chance of catastrophic failure or information leakage.
- **Decentralization -** No trusted third parties are needed to act as centralized authories. No single point of failure.
- **Scalability -** Tokenization is an embarrassingly parallel task that should scale efficently to billions of records.

Privacy Preserving Record Linkage (PPRL) is crucial component to data de-identification systems. PPRL obfuscate identifying attributes or other sensitive information about the subjects described in the records of a dataset while still preserving the ability to link records pertaining to the same subject through the use of an encrypted token. This practice is sometimes referred to as "tokenization" and is one of the components of data deidenfication.

The task of PPRL is to replace the attributes of a every record denoting Personally Identifiable Information (PII) with a token produced by a one-way cryptographic function. This prevents observers of the tokenized data from obtaining the PII. The tokens are produced deterministically such that input records with the same, or similar, PII attributes will produce an identical token. This allows practitioners to associate records across datasets that are highly likely to belong to the same data subject without having acces to PII.

Tokenization is also used when data is shared between organizations to limit, or in some cases fully mitigate, the risk of subject re-identification in the event that an untrusted third party gains access to a dataset containing sensitive data. Each party produced encrypted tokens using a different secret key so that any compromised data asset is, at worst, only matchable to other datasets mantained by the same party. During data sharing transactions, a specific "transcryption" data flow is used to first re-encrypt the sender's tokens into ephemeral tokens that do not match tokens in any other dataset and can only be ingested using the receipiants secret key. At no point in the "transcryption" data flow is the orginoal PII used.

## Glossary

| Term | Definition |
|-|-|
| Data Asset | A collection of records with attributes. Can be a single dataset, or a collection of related datasets. |
| Subject | A person who is being decribed by one or more recoreds in a data asset. PPRL attempts to obfuscate the identity of the subject. |
| Attribute | A single field of a record denoting one piece of information about the subject. |
| PII | Personally Identifying Information. Attributes of a data asset that can be used to determine the identity of a subject. Examples include name, residential address, gender, age, phone number, email, as well as other demographic or socio-ecominic attributes. |
| Token | An string of text derived deterministically by a one-way cryptographic function. |
| Implementer | An individual or organization that creates a software tool that implements this specification. |
| User | The end user of an OPPRL implementation. |
| Custodian | An individual or organization in possession of a data asset. |
| Receipient | An individual or organization that receives a data asset from a custodian. |

# Encryption Keys

Every user of an OPPRL implementation must have asymmetric encryption key pair consisting of a public key and corresponding private key. The public key is not secret and can be shared with parties that the user intends to share data with. A custodian will use the public key of a specific receiptiant to encrypt ephemeral tokens that can only be decrypted by the receiptiant using their private key.

Implementers may choose any asymettric encryption algorithm that is sufficiently safe, however users must 

The private key is also used to derive a third encryption key via a hash function. This key is a random 


# Tokenization

## Normalization

## Enhancement

## Tokens

| Token | Fields |
|-|-|
| 1 | First initial, Last name, Gender, Birth date |
| 2 | First soundex, Last soundex, Gender, Birth date |

# Transcryption

## Sender

## Receipiant