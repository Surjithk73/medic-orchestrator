# Data Sources - Medic Orchestrator

## Complete List of Data Sources

### Clinical Domain

1. **ClinicalTrials.gov v2 API**
   - Type: REST API
   - Data: 570,000+ clinical trials with phase, status, indication, endpoints, sponsors
   - URL: https://clinicaltrials.gov/api/v2/
   - Authentication: None required
   - Rate Limit: No published limit
   - Cost: Free

2. **PubMed Entrez API**
   - Type: REST API
   - Data: Scientific literature search, abstracts, full-text references
   - URL: https://eutils.ncbi.nlm.nih.gov/entrez/
   - Authentication: Optional API key (recommended for higher rate limits)
   - Rate Limit: 3 req/s free; 10 req/s with key
   - Cost: Free

### Patent Domain

3. **USPTO PatentsView API**
   - Type: REST API
   - Data: US patents with claims, assignees, expiry dates, IPC classification
   - URL: https://api.patentsview.org/
   - Authentication: None required
   - Rate Limit: No published limit
   - Cost: Free

4. **EPO OPS (European Patent Office Open Patent Services)**
   - Type: REST API
   - Data: European patents, legal status, patent families
   - URL: https://ops.epo.org/
   - Authentication: Free developer account required
   - Rate Limit: 2,500 requests/week
   - Cost: Free

### Market Domain

5. **OpenFDA Drug Labels API**
   - Type: REST API
   - Data: FDA-approved drug labels, indications, formulations
   - URL: https://api.fda.gov/drug/label.json
   - Authentication: Optional API key (recommended)
   - Rate Limit: 240 req/min free; 1,000 req/min with key
   - Cost: Free

6. **OpenFDA Adverse Events API**
   - Type: REST API
   - Data: Adverse event reports, safety signals
   - URL: https://api.fda.gov/drug/event.json
   - Authentication: Optional API key (recommended)
   - Rate Limit: 240 req/min free; 1,000 req/min with key
   - Cost: Free

7. **WHO Global Health Observatory (GHO) API**
   - Type: REST API
   - Data: Disease burden (DALYs), incidence rates, mortality data
   - URL: https://ghoapi.azureedge.net/api/
   - Authentication: None required
   - Rate Limit: No published limit
   - Cost: Free

### Regulatory Domain

8. **FDA DailyMed API**
   - Type: REST API
   - Data: Structured product labels, label history, regulatory changes
   - URL: https://dailymed.nlm.nih.gov/dailymed/services/v2/
   - Authentication: None required
   - Rate Limit: No published limit
   - Cost: Free

### Molecule Resolution & Identity

9. **ChEMBL REST API**
   - Type: REST API
   - Data: Molecule identity, synonyms, SMILES, bioactivity, targets
   - URL: https://www.ebi.ac.uk/chembl/api/data/
   - Authentication: None required
   - Rate Limit: Generous public limit
   - Cost: Free

10. **DrugBank Open Data**
    - Type: REST API
    - Data: Drug synonyms, mechanism of action, pharmacokinetics
    - URL: https://go.drugbank.com/
    - Authentication: Free non-commercial registration
    - Rate Limit: Moderate
    - Cost: Free (non-commercial)

### Disease-Target Associations

11. **Open Targets Platform GraphQL API**
    - Type: GraphQL API
    - Data: Disease-target associations, genetic evidence, drug-target links
    - URL: https://api.platform.opentargets.org/api/v4/graphql
    - Authentication: None required
    - Rate Limit: No published limit
    - Cost: Free

---

## Data Sources by Agent

### Clinical Agent Uses:
- ClinicalTrials.gov v2 API
- PubMed Entrez API

### Patent Agent Uses:
- USPTO PatentsView API
- EPO OPS (European Patent Office)
- Open Targets Platform (for target-disease validation)

### Market Agent Uses:
- OpenFDA Drug Labels API
- WHO Global Health Observatory API
- OpenFDA Adverse Events API (for market risk assessment)

### Regulatory Agent Uses:
- FDA DailyMed API
- OpenFDA Adverse Events API
- OpenFDA Drug Labels API (for regulatory history)

### Query Decomposer/Planner Uses:
- ChEMBL REST API (molecule resolution)
- DrugBank Open Data (mechanism of action, drug class)

---

## Summary Statistics

- **Total Data Sources**: 11 free APIs
- **Total Clinical Trials**: 570,000+
- **Total Patents**: Millions (US + European)
- **Total Drug Labels**: 100,000+
- **Total Adverse Event Reports**: Millions
- **Total Molecules in ChEMBL**: 2.3+ million

- **APIs Requiring No Authentication**: 7
- **APIs with Optional Authentication**: 3
- **APIs Requiring Free Registration**: 1

- **Total Monthly Cost**: $0 (all free tiers)

---

## Data Source Reliability & Update Frequency

| Source | Update Frequency | Data Quality | Reliability |
|--------|-----------------|--------------|-------------|
| ClinicalTrials.gov | Daily | High (government-verified) | 99.9% uptime |
| PubMed | Daily | High (peer-reviewed) | 99.9% uptime |
| USPTO PatentsView | Weekly | High (official records) | 99% uptime |
| EPO OPS | Daily | High (official records) | 99% uptime |
| OpenFDA | Monthly | High (FDA-verified) | 99.5% uptime |
| WHO GHO | Quarterly | High (WHO-verified) | 99% uptime |
| FDA DailyMed | Daily | High (FDA-verified) | 99.5% uptime |
| ChEMBL | Quarterly | High (EBI-curated) | 99.9% uptime |
| DrugBank | Quarterly | High (manually curated) | 99% uptime |
| Open Targets | Quarterly | High (consortium-curated) | 99% uptime |

---

## API Rate Limits & Quotas

| Source | Free Tier Limit | With API Key | Notes |
|--------|----------------|--------------|-------|
| ClinicalTrials.gov | Unlimited | N/A | No rate limit published |
| PubMed | 3 req/s | 10 req/s | Key recommended |
| USPTO PatentsView | Unlimited | N/A | Fair use policy |
| EPO OPS | 2,500/week | Same | Requires registration |
| OpenFDA | 240/min | 1,000/min | Key recommended |
| WHO GHO | Unlimited | N/A | No rate limit |
| FDA DailyMed | Unlimited | N/A | No rate limit |
| ChEMBL | Generous | N/A | No hard limit |
| DrugBank | Moderate | N/A | Non-commercial only |
| Open Targets | Unlimited | N/A | No rate limit |

---

## Data Coverage by Geography

### Global Coverage:
- WHO Global Health Observatory (worldwide disease data)
- PubMed (international literature)
- ChEMBL (global molecule database)
- Open Targets (global genetic evidence)

### US-Focused:
- ClinicalTrials.gov (US + international trials)
- USPTO PatentsView (US patents only)
- OpenFDA (US regulatory data)
- FDA DailyMed (US drug labels)

### Europe-Focused:
- EPO OPS (European patents)

### Multi-Regional:
- DrugBank (US, Canada, EU coverage)

---

## Data Formats

| Source | Format | Structured? | Requires Parsing? |
|--------|--------|-------------|-------------------|
| ClinicalTrials.gov | JSON | Yes | Minimal |
| PubMed | XML/JSON | Yes | Moderate |
| USPTO PatentsView | JSON | Yes | Minimal |
| EPO OPS | XML | Yes | Moderate |
| OpenFDA | JSON | Yes | Minimal |
| WHO GHO | JSON | Yes | Minimal |
| FDA DailyMed | XML/JSON | Yes | Moderate |
| ChEMBL | JSON | Yes | Minimal |
| DrugBank | XML/JSON | Yes | Moderate |
| Open Targets | GraphQL/JSON | Yes | Minimal |

---

## Compliance & Terms of Service

All data sources are used in compliance with their respective terms of service for:
- ✅ Non-commercial research purposes
- ✅ Educational use
- ✅ Academic projects
- ✅ Open-source development

For commercial deployment, the following may require licensing:
- DrugBank (commercial license available)
- EPO OPS (commercial terms available)

All other sources permit commercial use with proper attribution.

---

## Attribution Requirements

When using data from these sources, proper attribution is required:

**ClinicalTrials.gov**: "Data provided by ClinicalTrials.gov"
**PubMed**: "Literature from PubMed/NCBI"
**USPTO**: "Patent data from USPTO PatentsView"
**EPO**: "European patent data from EPO OPS"
**OpenFDA**: "Data provided by openFDA"
**WHO**: "Disease burden data from WHO GHO"
**ChEMBL**: "Molecule data from ChEMBL (EMBL-EBI)"
**DrugBank**: "Drug information from DrugBank"
**Open Targets**: "Target-disease data from Open Targets Platform"

---

## Backup & Redundancy Strategy

If a primary data source is unavailable:

1. **ClinicalTrials.gov down** → Use cached data + PubMed literature
2. **PubMed down** → Use ClinicalTrials.gov abstracts only
3. **USPTO down** → Use EPO OPS for US patent families
4. **EPO OPS down** → Use USPTO + Open Targets
5. **OpenFDA down** → Use FDA DailyMed + WHO data
6. **ChEMBL down** → Use DrugBank for molecule resolution

All agents implement graceful degradation and continue with available data sources.
