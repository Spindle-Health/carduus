# Functions

## ::: carduus.token.tokenize
    handler: python
    options:
      show_root_heading: true
      show_source: false
      separate_signature: true
      show_signature_annotations: false

## ::: carduus.token.transcrypt_out
    handler: python
    options:
      show_root_heading: true
      show_source: false
      separate_signature: true
      show_signature_annotations: false

## ::: carduus.token.transcrypt_in
    handler: python
    options:
      show_root_heading: true
      show_source: false
      separate_signature: true
      show_signature_annotations: false

## ::: carduus.token.TokenInfo
    handler: python
    options:
      members_order: source
      show_root_heading: true
      show_source: false

# OPPRL Implementation

Carduus is an extensible framework for implementing tokenization and record linkage systems, that also provides
an implementation of the Open Privacy Preserving Record Linkage protocol. 

## ::: carduus.token.OpprlPii
    handler: python
    options:
      members_order: source
      show_root_heading: true
      show_source: false

## ::: carduus.token.OpprlToken
    handler: python
    options:
      members_order: source
      show_root_heading: true
      show_source: false

# Encryption Key Management

Carduus provides

## ::: carduus.keys.SparkConfKeyService
    handler: python
    options:
      members_order: source
      show_root_heading: true
      show_source: false

## ::: carduus.keys.InMemoryKeyService
    handler: python
    options:
      members_order: source
      show_root_heading: true
      show_source: false

# Interfaces

Carduus offers interfaces that can be extended by the user to add additional behaviors to the tokenization process.

The primary extention 

## ::: carduus.token.PiiTransform
    handler: python
    options:
      members_order: source
      show_root_heading: true
      show_source: false


## ::: carduus.keys.EncryptionKeyService
    handler: python
    options:
      members_order: source
      show_root_heading: true
      show_source: false