# Domain: Campaign Finance

## Core entities

-   CampaignCommittee
-   Candidate
-   Donor (individual or organization)
-   Filing (report)
-   Contribution (transaction)
-   Expenditure

## Relationships

-   committeeRepresentsCandidate(Committee, Candidate)
-   contributesTo(Donor, Committee)
-   filesReport(Committee, Filing)
-   reportedIn(Contribution, Filing)
-   paysTo(Committee, Payee)

## Vocabulary seed (codes / types)

Example controlled vocabulary campaign-finance-entity-type.json:

-   CF_COMMITTEE_CANDIDATE – Candidate committee
-   CF_COMMITTEE_PAC – Political action committee
-   CF_COMMITTEE_PARTY – Party committee
-   CF_DONOR_INDIVIDUAL
-   CF_DONOR_ORGANIZATION
-   CF_FILING_QUARTERLY
-   CF_FILING_ANNUAL
-   CF_CONTRIBUTION_MONETARY
-   CF_CONTRIBUTION_IN_KIND

## Rewrite Problems

Name canonicalization:

- “Committee to Elect Jane Doe”, “Friends of Jane Doe”, “Jane Doe for Congress” all rewrite to a canonical legalNameNormalized for the committee and relate to a candidate entity.

Corporate forms + punctuation:

- PAC, P.A.C., “Political Action Committee”, variations in multiple languages.

Identifier normalization:

- FEC IDs (C12345678), state committee IDs, their prefixes, and zero-padding.

Purpose/description normalization:

- Harmonizing “contribution to candidate”, “contrib cand”, etc. into the CF_CONTRIBUTION_* vocab.

## Good Test For

- Canonicalization of messy strings
- Combining multiple identifiers
- Merge strategies (same donor across filings)