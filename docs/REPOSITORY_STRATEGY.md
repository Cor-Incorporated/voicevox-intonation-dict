# Repository Strategy

This document defines how this repository is maintained as a Cor.株式会社
general-purpose codebase without mixing in customer-specific confidential
materials.

## Repository Role

`voicevox-intonation-dict` is the canonical Cor.株式会社 implementation for the
VOICEVOX intonation dictionary extension server.

The repository may contain:

- general server code
- generic VOICEVOX integration logic
- API models and tests
- public documentation for setup and operation
- non-confidential historical records of Cor.株式会社 development
- third-party dependency and license notes

The repository must not contain:

- customer-specific prompts, scripts, or operating procedures
- private conversation logs
- customer data, generated logs, API metadata, or model outputs
- credentials, `.env` files, API keys, hostnames, tunnel settings, or device IDs
- delivery contracts, confidentiality agreement text, contract amounts, or
  private negotiation notes
- assets or source material supplied by a customer or other third party

## Branching

- `main`: generic public version only
- `release/*`: generic public releases derived from `main`
- `feature/*`: generic feature work only

Customer-specific deployment work must be kept outside this public repository.
If customer-specific delivery materials are required, use a separate private
delivery repository or local evidence folder with access controls.

## Evidence Boundary

Public evidence in this repository should be limited to facts that are safe to
publish:

- commit hashes and dates from this repository
- generic ownership notices
- OSS dependency notes
- source files that do not contain confidential customer information

Private evidence should be stored separately:

- contracts and confidentiality agreements
- delivery history
- customer communications
- dispute-prevention notes
- exact customer names and transaction details

## Code Separation Rules

Keep reusable implementation logic in this repository. Keep adapters and
delivery-specific code separate.

- Core logic: dictionary models, matching, AudioQuery modification, persistence,
  and API behavior
- Adapter logic: editor integration code, CLI helpers, import/export bridges
- Delivery logic: customer-specific setup, environment configuration, runbooks,
  and acceptance notes

Only Core logic belongs here by default. Adapter logic may be documented here
when it is generic. Delivery logic does not belong here.

## Review Checklist

Before committing, confirm:

- no customer names or private project names appear in public docs
- no `.env`, logs, generated metadata, or local state files are staged
- no ignored reference source is force-added
- no customer-provided materials are included
- public docs distinguish Git-confirmed facts from local/private records
- dependency and license notes match the local source evidence
