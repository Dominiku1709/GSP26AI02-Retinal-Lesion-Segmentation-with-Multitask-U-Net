# OCT Image Analysis API - Deployment & Operations Checklist

## 🚀 Pre-Deployment

### Code Quality

- [ ] Run linting: `flake8 app/`
- [ ] Check formatting: `black --check app/`
- [ ] Run type checks: `mypy app/`
- [ ] Run tests: `pytest tests/ --cov=app`
- [ ] Test coverage > 80%
- [ ] No critical security warnings in dependencies
- [ ] All TODOs and FIXMEs addressed
- [ ] Code review completed (2+ approvals)

### Documentation

- [ ] README.md updated
- [ ] API specification complete
- [ ] Deployment guide written
- [ ] Architecture diagram created
- [ ] Environment variables documented
- [ ] Database schema documented
- [ ] API examples provided (Python, JS, cURL)

### Testing

- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] E2E tests with real model passing
- [ ] Performance tests completed
- [ ] Load test: 100+ concurrent requests
- [ ] Error scenarios tested (invalid files, etc.)
- [ ] Database recovery tested

### Security

- [ ] File upload validation tested
- [ ] SQL injection tests passed
- [ ] CORS properly configured
- [ ] Sensitive data not logged
- [ ] Secrets not in git repo
- [ ] API rate limiting ready (not deployed yet)
- [ ] Authentication design complete (not implemented yet)

---

## 🐳 Docker Deployment

### Local Docker Build

```bash
# Build image
docker build -t oct-api:latest .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/storage:/app/storage \
  -v $(pwd)/weights:/app/weights \
  -e DATABASE_URL="sqlite:///./oct_analysis.db" \
  oct-api:latest

# Test
curl http://localhost:8000/api/v1/health
```

### Deployment Checklist

- [ ] Dockerfile tested locally
- [ ] Image builds without errors
- [ ] Container runs without errors
- [ ] Health check endpoint responds
- [ ] All ports exposed correctly
- [ ] Volume mounts tested
- [ ] Environment variables injectable
- [ ] `.dockerignore` configured
- [ ] Multi-stage builds optimized (optional)

### Image Optimization

- [ ] Image size < 500MB
- [ ] No unnecessary layers
- [ ] Non-root user configured (optional)
- [ ] Health check configured
- [ ] Signals handled properly

---

## ☁️ Cloud Deployment (AWS/GCP/Azure)

### Container Registry

- [ ] Image pushed to registry (ECR/GCR/ACR)
- [ ] Image tagged with version
- [ ] Image tagged as `latest`
- [ ] Registry access configured
- [ ] Image scanning enabled

### Kubernetes (if using K8s)

- [ ] `deployment.yaml` created
- [ ] `service.yaml` configured
- [ ] `ingress.yaml` for routing
- [ ] Resource limits set
  - CPU: 500m-1000m request
  - Memory: 512Mi-1Gi request
- [ ] Health checks configured
  - Liveness probe: /api/v1/health
  - Readiness probe: /api/v1/health
- [ ] Autoscaling configured (2-10 replicas)
- [ ] ConfigMap for environment variables
- [ ] Secrets for sensitive data
- [ ] PersistentVolume for storage/
- [ ] PersistentVolume for weights/

### Database

- [ ] PostgreSQL database provisioned
- [ ] Connection pooling configured (pgBouncer)
- [ ] Backups configured (daily)
- [ ] Restore testing completed
- [ ] Read replicas configured (optional)
- [ ] DATABASE_URL secret stored
- [ ] Connection timeout: 5s
- [ ] Query timeout: 30s

### Storage

- [ ] S3/GCS bucket created for uploads
- [ ] Bucket policy configured
- [ ] Lifecycle rules (auto-delete old files)
- [ ] CORS configured if needed
- [ ] Encryption enabled
- [ ] Versioning enabled
- [ ] Access logs enabled

### Network

- [ ] Load balancer configured
- [ ] SSL/TLS certificate installed
- [ ] HTTPS enforced
- [ ] CORS origins configured for all frontends
- [ ] Firewall rules configured
- [ ] DDoS protection enabled (optional)

---

## 📊 Monitoring & Logging

### Metrics

- [ ] Prometheus endpoint configured
- [ ] Metrics exposed:
  - Request count (by method, status, endpoint)
  - Request latency (p50, p95, p99)
  - Error rate
  - Model inference time
  - Database query time
  - Active database connections
  - Disk usage
  - Memory usage
  - CPU usage

### Dashboards

- [ ] Grafana dashboard created
- [ ] Key metrics displayed
- [ ] Drill-down dashboards available
- [ ] Dashboard shared with team

### Logging

- [ ] Structured logging (JSON)
- [ ] Log aggregation (ELK/Datadog/CloudWatch)
- [ ] Log retention policy: 30 days
- [ ] Log rotation configured
- [ ] Sensitive data filtered
- [ ] Request IDs for tracing
- [ ] Error alerts configured
- [ ] Dashboard for log analysis

### Alerts

- [ ] High error rate > 5%: Slack/PagerDuty
- [ ] API latency p95 > 1s: Slack
- [ ] Database disconnected: PagerDuty
- [ ] Model inference failed: Slack
- [ ] Disk usage > 80%: Slack
- [ ] Memory usage > 80%: Slack
- [ ] Pod restart loops: PagerDuty
- [ ] Out of memory errors: PagerDuty

---

## 🔐 Security Hardening

### Application Level

- [ ] Input validation on all endpoints
- [ ] Rate limiting per IP/user
- [ ] HTTPS enforced
- [ ] Security headers configured
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security: max-age=31536000
- [ ] CORS properly configured
- [ ] API versioning implemented
- [ ] API keys rotated monthly
- [ ] Secret rotation policy

### Infrastructure Level

- [ ] Secrets not in environment (use Secret Manager)
- [ ] Network policies configured (K8s)
- [ ] Pod security policies enabled
- [ ] Image scanning enabled
- [ ] Vulnerability scanning on deploy
- [ ] No root containers
- [ ] Read-only filesystem (if possible)
- [ ] Security group/firewall rules minimal

### Data

- [ ] Database encryption at rest
- [ ] Database encryption in transit
- [ ] Backup encryption enabled
- [ ] PII data not logged
- [ ] Database access restricted
- [ ] Storage bucket encryption enabled
- [ ] Data retention policy configured
- [ ] GDPR compliance verified (if applicable)

### Access Control

- [ ] Role-based access control (RBAC)
- [ ] API authentication implemented
- [ ] API key validation on all requests
- [ ] Admin access restricted
- [ ] Audit logging enabled
- [ ] Access logs reviewed weekly
- [ ] SSH access restricted to admins

---

## 📈 Performance Tuning

### Application

- [ ] Connection pooling configured
- [ ] Image caching implemented (optional)
- [ ] Database query optimization
- [ ] N+1 queries eliminated
- [ ] Indexes created on common queries
- [ ] Slow query log monitored
- [ ] Request profiling enabled

### Inference

- [ ] Model quantization evaluated (optional)
- [ ] GPU acceleration tested (if available)
- [ ] Batch processing evaluated
- [ ] Model caching implemented
- [ ] Inference latency < 300ms (p95)

### Database

- [ ] Connection pool size: 5-20
- [ ] Query timeout configured
- [ ] Slow query log enabled
- [ ] Vacuum/analyze scheduled (PostgreSQL)
- [ ] Statistics updated regularly

### Caching

- [ ] Redis cache setup (optional)
- [ ] Cache invalidation strategy
- [ ] Cache hit rates monitored
- [ ] Warm cache on startup

---

## 👥 Team & Processes

### Documentation

- [ ] Runbook created
- [ ] Troubleshooting guide written
- [ ] On-call playbook created
- [ ] Architecture decision records (ADRs) written
- [ ] API documentation updated

### Knowledge Transfer

- [ ] Team trained on deployment
- [ ] Team trained on monitoring
- [ ] Team trained on incident response
- [ ] Documentation reviewed by team
- [ ] Pair programming session completed

### Processes

- [ ] Release process documented
- [ ] Rollback procedure tested
- [ ] Zero-downtime deployment tested
- [ ] Change log maintained
- [ ] Semantic versioning used
- [ ] Release notes template created

### Incidents

- [ ] Incident response plan written
- [ ] Escalation procedure defined
- [ ] Post-mortem process defined
- [ ] Blameless culture established
- [ ] Incident severity levels defined

---

## 🔍 Post-Deployment Verification

### Smoke Tests (First Hour)

```bash
# Health check
curl https://api.example.com/api/v1/health

# Test analysis endpoint with sample image
curl -X POST https://api.example.com/api/v1/analyze \
  -F "file=@test_image.png"

# Verify database connectivity
curl https://api.example.com/api/v1/scans

# Check API documentation
curl https://api.example.com/docs
```

- [ ] Health endpoint returns 200
- [ ] Analysis endpoint works
- [ ] Scans retrieval works
- [ ] API docs accessible
- [ ] No error logs in first hour
- [ ] Response times normal
- [ ] Database responding
- [ ] Model inference working

### Integration Tests

- [ ] Analyze → retrieve workflow works
- [ ] File uploads persist correctly
- [ ] Database transactions commit
- [ ] File cleanup works on errors
- [ ] CORS headers present
- [ ] Authentication working (if implemented)

### Load Testing (Staging)

```bash
# Example with Apache Bench
ab -n 100 -c 10 \
  -p image.bin \
  https://staging-api.example.com/api/v1/analyze
```

- [ ] 100+ req/sec sustained
- [ ] p95 latency < 1s
- [ ] Error rate < 0.1%
- [ ] No memory leaks
- [ ] Database handles load
- [ ] GPU/CPU at reasonable levels

### Security Verification

- [ ] SSL/TLS certificate valid
- [ ] HTTPS enforced
- [ ] CORS properly restricted
- [ ] Security headers present
- [ ] No sensitive data in logs
- [ ] API keys cannot be guessed
- [ ] File upload validation works

---

## 📋 Ongoing Operations

### Daily

- [ ] Monitor error rates
- [ ] Check system health dashboard
- [ ] Review critical alerts
- [ ] Verify backups completed

### Weekly

- [ ] Review performance metrics
- [ ] Analyze slow queries
- [ ] Check disk usage trends
- [ ] Review security logs
- [ ] Update status page

### Monthly

- [ ] Patch dependencies
- [ ] Security scan (dependencies)
- [ ] Database vacuum/optimize
- [ ] Rotate API keys
- [ ] Review cost metrics
- [ ] Capacity planning review

### Quarterly

- [ ] Disaster recovery test
- [ ] Load testing
- [ ] Security audit
- [ ] Architecture review
- [ ] Team retrospective

---

## 🆘 Incident Checklist

### During Incident

- [ ] Declare incident
- [ ] Open incident channel (Slack/Teams)
- [ ] Assign incident commander
- [ ] Assign technical lead
- [ ] Assign communications lead
- [ ] Update status page
- [ ] Start collecting data/logs
- [ ] Document timeline

### Investigation

- [ ] Check health endpoint
- [ ] Review recent logs
- [ ] Check metrics (CPU, memory, DB)
- [ ] Check recent deployments
- [ ] Check database status
- [ ] Check external dependencies
- [ ] Reproduce issue locally

### Resolution

- [ ] Implement fix
- [ ] Test fix in staging
- [ ] Deploy fix
- [ ] Verify fix in production
- [ ] Monitor error rates
- [ ] Update status page
- [ ] Notify stakeholders

### Post-Incident

- [ ] Collect logs/metrics
- [ ] Schedule post-mortem
- [ ] Schedule within 24 hours
- [ ] Create action items
- [ ] Fix root cause
- [ ] Update runbooks
- [ ] Share learnings

---

## 🎯 Success Criteria

- [ ] API uptime ≥ 99.9%
- [ ] P95 latency < 500ms
- [ ] Error rate < 0.1%
- [ ] Model accuracy maintained
- [ ] No data loss
- [ ] Security incidents: 0
- [ ] Team can deploy independently
- [ ] On-call rotation sustainable

---

## 📞 Escalation Contacts

**On-Call:** [Name] - [Phone] - [Slack]

**Lead Engineer:** [Name] - [Email]

**DevOps Lead:** [Name] - [Email]

**Manager:** [Name] - [Email]

**Executive Sponsor:** [Name] - [Email]

---

## 📝 Sign-Off

- [ ] Engineering: _________________ Date: _______
- [ ] Product: _________________ Date: _______
- [ ] Operations: _________________ Date: _______
- [ ] Security: _________________ Date: _______
- [ ] Executive: _________________ Date: _______

---

**Deployment Ready: [ ] YES [ ] NO**

**Next Review Date:** _______________

**Version:** 1.0  
**Last Updated:** 2024-01-15
