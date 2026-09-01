---
name: vmware-vcenter
description: >
  Full security audit for VMware vCenter / vSphere environments. Covers
  cluster configuration, ESXi host hardening, VM security, network (vDS,
  port groups), storage (datastores, SAN), HA/DRS configuration, and
  vCenter SSO/identity management.
domain: virtualization
connectors:
  - collect_vcenter_clusters.py
  - collect_vcenter_hosts.py
  - collect_vcenter_vms.py
  - collect_vcenter_networks.py
  - collect_vcenter_storage.py
  - collect_vcenter_ha_drs.py
benchmarks:
  - vcenter_best_practice
  - nis2_technical
authentication: service-account
transport: api
---

# VMware vCenter Audit Skill

## Overview

Audits VMware vCenter and ESXi hosts against best practice baselines.
Collects cluster topology, host configuration, VM security settings,
virtual networking, storage layout, and HA/DRS configuration.

## Collection

| Connector | What It Collects | Transport |
|-----------|------------------|-----------|
| `collect_vcenter_clusters.py` | Cluster topology, ESXi membership, resource pools | vSphere API (pyvmomi) |
| `collect_vcenter_hosts.py` | ESXi version, patches, NTP, DNS, syslog, lockdown mode | vSphere API |
| `collect_vcenter_vms.py` | VM config, encryption, TPM, VMtools, snapshots | vSphere API |
| `collect_vcenter_networks.py` | vDS/dVS, port groups, promiscuous mode, NIOC | vSphere API |
| `collect_vcenter_storage.py` | Datastores, SAN zoning, VSAN config, storage policies | vSphere API |
| `collect_vcenter_ha_drs.py` | HA settings, DRS rules, admission control, FT | vSphere API |

## Graph

Nodes:
  - name: collect-vcenter
    trigger: route("audit-planner")
    input: [scoping, credentials]
    role: You collect vCenter data via the vSphere API.
    skills: [virtualization/vmware-vcenter/connectors]
    output: work/evidence/{client}/vmware-vcenter/
    route: always -> evaluate-vcenter

  - name: evaluate-vcenter
    trigger: route("collect-vcenter")
    input: [evidence, benchmarks]
    role: You evaluate vCenter evidence against best practice benchmarks.
    skills: [core/benchmark-loader]
    output: work/findings/{client}/vmware-vcenter/
    route: always -> aggregator