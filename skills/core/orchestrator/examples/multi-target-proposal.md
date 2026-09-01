# Graph Topology — Multi-Target Audit Proposal

```
[GRAPH ENGINE — TOPOLOGY PROPOSAL]
Client: acme-corp
Request: audit Azure (subscriptions prod-eu and prod-us) plus Active Directory
         against CIS Azure v2.0 Level 1, NIS2 Technical, and AD Best Practice

Resolved topology:

Phase 1 — Collection (parallel):
- collect-azure       (skill: azure, model: haiku): collect Azure subscriptions
- collect-ad          (skill: active-directory, model: haiku): collect AD domain

Phase 2 — Evaluation (parallel, after collection):
- evaluate-azure-cis  (skill: azure, benchmark: cis_azure_v2.0, model: sonnet)
- evaluate-azure-nis2 (skill: azure, benchmark: nis2_technical, model: sonnet)
- evaluate-ad-bp      (skill: active-directory, benchmark: ad_best_practice, model: sonnet)

Phase 3 — Synthesis:
- aggregator          (skill: core/finding-aggregator): merge findings
- report-compiler     (skill: core/report-compiler): generate audit report
- consolidator: present final output

Edges:
- collect-azure → evaluate-azure-cis (evidence)
- collect-azure → evaluate-azure-nis2 (evidence)
- collect-ad → evaluate-ad-bp (evidence)
- evaluate-azure-cis → aggregator (findings)
- evaluate-azure-nis2 → aggregator (findings)
- evaluate-ad-bp → aggregator (findings)
- aggregator → report-compiler (consolidated findings)
- report-compiler → consolidator (report)

Topology: two-phase diamond (fan-out 2 → fan-out 3 → fan-in 1 → sequential)
Cost estimate: ~15K-25K tokens

Proceed with this topology, or describe modifications:
```