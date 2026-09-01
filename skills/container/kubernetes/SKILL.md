---
name: kubernetes
description: >
  Full security audit for Kubernetes clusters. Covers RBAC, network policies,
  Pod Security Standards (PSS/PSA), OPA/Gatekeeper policies, resource
  configuration, secrets management, storage classes, and audit logging.
domain: container
connectors:
  - collect_k8s_policies.py
  - collect_k8s_network.py
  - collect_k8s_rbac.py
  - collect_k8s_security.py
  - collect_k8s_storage.py
  - collect_k8s_workloads.py
benchmarks:
  - cis_k8s_v1.24
  - nis2_technical
authentication: kubeconfig
transport: api
---

# Kubernetes Audit Skill

## Overview

Audits Kubernetes clusters against CIS Kubernetes Benchmark and NIS2 technical
measures. Collects cluster-wide configuration data via kubectl and evaluates
RBAC, network policies, pod security, admission controllers, resource limits,
and more.

## Collection

| Connector | What It Collects | Requires |
|-----------|------------------|----------|
| `collect_k8s_policies.py` | OPA/Gatekeeper, Kyverno, PSA, PodSecurityPolicies | cluster-reader |
| `collect_k8s_network.py` | NetworkPolicies, CNI config, service mesh | cluster-reader |
| `collect_k8s_rbac.py` | Roles, ClusterRoles, bindings, service accounts | cluster-reader |
| `collect_k8s_security.py` | PodSecurity, seccomp, apparmor, security contexts | cluster-reader |
| `collect_k8s_storage.py` | StorageClasses, PVCs, CSI drivers | cluster-reader |
| `collect_k8s_workloads.py` | Deployments, resource quotas, HPAs, node status | cluster-reader |

## Evaluation

Evaluates against:
- **CIS Kubernetes Benchmark v1.24** — 100+ controls across control plane, worker nodes, RBAC, network, security
- **NIS2 Technical** — cross-cuts with network segmentation, logging, RBAC controls

## Graph

Nodes:
  - name: collect-k8s
    trigger: route("audit-planner")
    input: [scoping, credentials]
    role: You collect Kubernetes cluster data via kubectl.
    skills: [container/kubernetes/connectors]
    output: work/evidence/{client}/kubernetes/
    route: always -> evaluate-k8s

  - name: evaluate-k8s
    trigger: route("collect-k8s")
    input: [evidence, benchmarks]
    role: You evaluate K8s evidence against CIS and NIS2 benchmarks.
    skills: [core/benchmark-loader]
    output: work/findings/{client}/kubernetes/
    route: always -> aggregator