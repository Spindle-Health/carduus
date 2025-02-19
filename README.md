# Carduus

[![PyPI version](https://badge.fury.io/py/carduus.svg)](https://badge.fury.io/py/carduus)

The open source implementation of the Open Privacy Preserving Record Linkage (OPPRL) protocol build on Spark.

> :warning: Carduus has not reached a v1.0 release yet and therefore the API and behaviors are subject to change. See the [contributing](./CONTRIBUTING.md) guide if you would like to help the project.

## Rationale

Privacy Preserving Record Linkage (PPRL) is crucial component to data de-identification systems. PPRL obfuscate identifying attributes or other sensitive information about the subjects described in the records of a dataset while still preserving the ability to link records pertaining to the same subject through the use of an encrypted token. This practice is sometimes referred to as "tokenization" and is one of the components of data de-identification.

The task of PPRL is to replace the attributes of a every record denoting Personally Identifiable Information (PII) with a token produced by a one-way cryptographic function. This prevents observers of the tokenized data from obtaining the PII. The tokens are produced deterministically such that input records with the same, or similar, PII attributes will produce an identical token. This allows practitioners to associate records across datasets that are highly likely to belong to the same data subject without having access to PII.

Tokenization is also used when data is shared between organizations to limit, or in some cases fully mitigate, the risk of subject re-identification in the event that an untrusted third party gains access to a dataset containing sensitive data. Each party produced encrypted tokens using a different secret key so that any compromised data asset is, at worst, only matchable to other datasets maintained by the same party. During data sharing transactions, a specific "transcryption" data flow is used to first re-encrypt the sender's tokens into ephemeral tokens that do not match tokens in any other dataset and can only be ingested using the recipients secret key. At no point in the "transcryption" data flow is the original PII used.

Carduus is the first (and canonical) implementation of the [Open Privacy Preserving Record Linkage](https://spindle-health.github.io/carduus/opprl/) (OPPRL) protocol. This protocol presents a standardized methodology for tokenization that can be implemented in any data system to increase interoperability. The carduus implementation is a python library that distributes the tokenization workload using apache [Spark](https://spark.apache.org/) across multiple cores or multiple machines in a high performance computing cluster for efficient tokenization of any scale datasets.

**Why the name "Carduus"?** The [carduus](https://en.wikipedia.org/wiki/Carduus) is a genus of thistle plants that was used to brush fibrous materials so that individual fibres align in preparation for spinning the material into thread or yarn. Today this process is known as "carding" and is done by specialized machines.

## Getting Started

See the [getting started guide](https://spindle-health.github.io/carduus/guides/getting-started/) on the project's web page for an detailed explanation of how carduus is used including example code snippets.

The full [API](https://spindle-health.github.io/carduus/api/) and an [example usage on Databricks](https://spindle-health.github.io/carduus/databricks/) are also provided on the project's web page.

## Contributing

Please refer to the carduus [contributing guide](https://spindle-health.github.io/carduus/CONTRIBUTING/) for information on how to get started contributing to the project.

### Organizations that have contributed to Carduus

<a href="https://spindlehealth.com/">
    <img src="https://spindlehealth.com/wordmark_color_dark.png"
        alt="Spindle Health"
        style="padding: 10px; height: 64px"
    />
</a>