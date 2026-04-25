# Scaling Roadmap: Moving from 1K to 100K Users

This document outlines the technical scaling triggers and infrastructure maturation required for MentalFlow's first year of growth on Google Cloud Platform (GCP).

## 📊 Performance Benchmarks
| Metric | Baseline (1K) | Target (100K) |
| :--- | :--- | :--- |
| **API Latency (p95)** | < 300ms | < 100ms |
| **Concurrent Players** | 50 | 5,000 |
| **Database Uptime** | 99.9% | 99.99% |

---

## 🏗️ Infrastructure Phases

### Phase 1: Managed Baseline (Months 1-3)
- **Compute**: GKE (Standard) with 3-5 nodes.
- **Database**: Cloud SQL (PostgreSQL) - 4 CPU / 16GB RAM.
- **CDN**: Cloud CDN for static frontend assets.

### Phase 2: High Availability (Months 4-6)
- **Compute**: Regional GKE with Multi-AZ deployments.
- **Auto-scaling**: HPA (Horizontal Pod Autoscaler) triggered at 70% CPU.
- **Database**: Enable HA (Failover instance) and 1 Read Replica.
- **Cache**: Cloud Memorystore (Redis) for session and RL state caching.

### Phase 3: Enterprise Scale (Months 7-12)
- **Compute**: Anthos for multi-region GKE clusters (US-East, US-West, EU).
- **Database**: Migration to **Cloud Spanner** for global consistency or sophisticated sharding by UserID.
- **Edge**: WAF (Google Cloud Armor) for DDoS protection and IP rate-limiting.

---

## 📉 Scaling Triggers
- **Trigger A**: DB Connection count > 80% → Deploy new read replica.
- **Trigger B**: API Response Time > 500ms → Increase GKE Node Pool capacity.
- **Trigger C**: Cost/User > $0.50 → Optimize RL inference runtime or DB queries.

## 💰 Resource Projections
- **Year 1 Total Infrastructure Cost**: $240K (Est. $20K/month average).
- **Projected Unit Economics**: $0.20 infra cost per active user.
