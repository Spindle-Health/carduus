# OPPRL v0.1 Specification

> :warning: Warning
>
> This specification is incomplete and actively being written collaboratively in the open. Many sections are missing and the specifics may change dramatically.
>
> If you would like to join 
>
> Authors of OPPRL implementations should expect breaking changes, and interoperability between implementation cannot be guarenteed until an official version 1.0 is published.

Privacy Preserving Record Linkage (PPRL) systems are used to obfuscate identifying attributes or other sensitive information about the subjects described in the records of a dataset while still preserving the ability to link records pertaining to the same subject through the use of an encrypted token. This practice is sometimes referred to as "tokenization" and is one of the components of data deidenfication.

The task of PPRL is to replace the attributes of a every record denoting Personally Identifiable Information (PII) with a token produced by a one-way cryptographic function. This prevents observers of the tokenized data from reversing the token into the sensitive PII attributes. The tokens are produced deterministically such that input records with the same, or similar, PII attributes will produce an identical token. This allows user of multiple tokenized data assets to associate records that are highly likely to belong to the same data subject without having acces to PII.

Tokenization is also used when data is shared between organizations to limit the scope of damages in the event that one organization's data is compromised. Each party's tokens are created via encryption using a different secret key so that any compromised data asset is only matchable to other datasets mantained by the same party. During data sharing transactions, a specific "transcryption" data flow is used to re-encrpt the sender's tokens into tokens that match the receipient's data without recovering the underlying PII.

## About this specification

- SemVer

## Glossary

- **Data Asset:** A collection of records with attributes. Can be a single dataset, or a collection of related datasets.
- **Subject:** A person who is being decribed by one or more recoreds in a data asset.
- **PII:** Personally Identifying Information. Attributes of a data asset that can be used to determine the identity of a subject. Examples include name, residential address, gender, age, phone number, email, as well as other demographic, socio-ecominic, and 
- **Token:** An arbitrary string of text derived deterministically from PII that can be used to identify records pertaining the same subject. Tokens provide nearly no information about the underlying PII they are generated from and thus can be used to replace PII in a data asset

## 1 Tokenization

Convertion of PII attributes into tokens.

### Requirements

### 1.1 Data Flow

Inputs:

1. An AES encryption key unique to data asset.
2. PII Transformations
3. Token specificaitnos.

#### 1.1.1 Normalization

#### 1.1.2 Enhancement

#### 1.1.3 Fragmentation

#### 1.1.4 Hashing

#### 1.1.5 Encryption

#### 1.1.6 Base64 Encoding

## 2 Transcyption

The re-encryption of tokens for the purpose of safely delivering tokenized data between parties.

### Requirements

### 2.1 Sender Data Frow 

Inputs:

1. The AES encryption key used to encrypt the PII hashes.
3. The public RSA key of the receiver.

The entire data flow must be performed by the sender with no malicious observers intercepting intermediate values.

#### 2.1.1 Decode Base64

#### 2.1.2 AES Decryption

#### 2.1.3 RSA Encryption

#### 2.1.4 Encode Base64

### 2.2 Receiver Data Flow

Inputs:

1. The private RSA key of the receiver. It must corresponds to the public key used by the sender.
3. An AES encryption key unique to the receiver.

#### 2.2.1 Decode Base64

#### 2.2.2 RSA Decryption

#### 2.2.3 AES Encryption

#### 2.2.4 Encode Base64

## 3 OPPRL PII Transformations

### 3.1 Normalizations

#### Person Names

#### Gender

#### Dates

### 3.2 Enhancements

#### Person Names

#### Dates

## 5 OPPRL Token Specifications
