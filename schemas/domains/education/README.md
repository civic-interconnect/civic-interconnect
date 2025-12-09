# Domain: Eduction

## Core entities

-   Institution (university, college)
-   Campus
-   Program (degree program, certificate)
-   Course
-   Credential (degree awarded)
-   Accreditor

## Relationships

-   institutionHasCampus(Institution, Campus)
-   institutionOffersProgram(Institution, Program)
-   programIncludesCourse(Program, Course)
-   programLeadsToCredential(Program, Credential)
-   accredits(Accreditor, Institution)

## Vocabulary seed (codes / types)

Example education-program-level.json:

-   EDU_PROGRAM_ASSOCIATE
-   EDU_PROGRAM_BACHELOR
-   EDU_PROGRAM_MASTER
-   EDU_PROGRAM_DOCTORAL
-   EDU_PROGRAM_CERTIFICATE

Example education-institution-type.json:

-   EDU_INST_PUBLIC_4_YEAR
-   EDU_INST_PRIVATE_NONPROFIT_4_YEAR
-   EDU_INST_PUBLIC_2_YEAR
-   EDU_INST_PRIVATE_FOR_PROFIT

## Rewrite Problems

Degree names:

-   “B.S.”, “BSc”, “Bachelor of Science” → EDU_PROGRAM_BACHELOR.

Institution names:

-   “Univ. of Minnesota Duluth”, “University of MN – Duluth”, “UMD” → canonical legalNameNormalized.

Accreditor codes:

-   Accreditors with code vs full name; multiple legacy names.

Program titles:

-   “Data Analytics”, “Data Analytics (Online)”, “MS in Data Analytics” → canonical program + delivery-mode attribute.

## Good Test For

-   Name + abbreviation canonicalization
-   Crosswalks to external code lists (IPEDS, accreditor lists)
-   Multi-level identifiers (institution, campus, program)
