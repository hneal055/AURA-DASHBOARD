# AURA Dashboard - Production Deployment

A secure, containerized web dashboard built with Nginx and modern security best practices.

## 📋 Project Overview

AURA Dashboard is a production-ready web application deployed as a Docker container with:
- Secure Nginx configuration with security headers
- Resource limits and auto-restart capabilities
- Health monitoring and diagnostics
- Automated backup system
- Vulnerability scanning

## 🚀 Current Status

**Production Container:** ✅ Running
- **Image:** `aura-dashboard-prod:latest`
- **Port:** 80 (HTTP)
- **Memory:** 512MB limit
- **CPU:** 1.0 core limit
- **Restart Policy:** unless-stopped (auto-recovery)
- **HTTP Status:** 200 OK ✅

## 📦 What's Included

### Configuration Files
- **nginx.conf** - Standard Nginx web server configuration with security headers
- **nginx-secure.conf** - Enhanced security configuration with CSP, HSTS, and other headers
- **Dockerfile** - Standard container image (nginx:alpine)
- **Dockerfile.secure** - Production-hardened container image
- **Dockerfile.dev** - Development container image

### Deployment Scripts
- **deploy-production.ps1** - Complete production deployment with pre-checks, security scan, backup, and health verification
- **deploy-secure.ps1** - Secure version deployment
- **deploy-docker.ps1** - Standard Docker deployment
- **security-scan.ps1** - Vulnerability scanning (Docker Scout / Trivy)
- **system-health.ps1** - System and Docker health diagnostics
- **diagnose-docker.ps1** - Container-specific diagnostics
- **test-dashboard.ps1** - Operational test suite
- **test-docker.ps1** - Basic Docker functionality test

### Management Scripts
- **auto-backup.ps1** - Automated backup creation
- **restore-backup.ps1** - Backup restoration
- **start-docker.ps1** - Start containers
- **stop-docker.ps1** - Stop containers
- **restart-aura.ps1** - Restart the AURA Dashboard
- **cleanup-docker.ps1** - Clean up unused Docker resources

## 🛠️ Quick Start

### Prerequisites
- Docker Desktop (v29.2.0+)
- PowerShell 7+
- 2GB RAM minimum
- 5GB free disk space

### Deploy Production Container

```powershell
.\deploy-production.ps1
```

This script will:
1. ✅ Check system resources (memory, disk)
2. ✅ Run security vulnerability scan
3. ✅ Create production backup
4. ✅ Build production container
5. ✅ Deploy with resource limits
6. ✅ Verify health check

### Check System Health

```powershell
.\system-health.ps1
```

Shows:
- Docker daemon status
- Disk space usage
- Container resource limits
- Network configuration

### Run Diagnostics

```powershell
.\diagnose-docker.ps1
```

Diagnoses:
- Container status
- Port mapping
- Application logs
- HTTP connectivity

### Run Tests

```powershell
.\test-dashboard.ps1
```

Tests:
- Container status
- Port binding
- HTTP endpoint
- Resource usage
- Error logs
- Restart resilience
- Content validation

## 🔍 Recent Fixes (Commit: 8f108ec)

### Fixed Issues
1. **nginx-secure.conf** - Corrected `try_files` directive
   - **Before:** `try_files \ \/ =404;` (syntax error)
   - **After:** `try_files $uri $uri/ /index.html;` (proper SPA routing)

2. **Dockerfile.secure** - Removed config deletion
   - **Before:** `RUN rm -f /etc/nginx/conf.d/default.conf` (deleted copied config)
   - **After:** Removed the problematic RUN command

### Results
- ✅ Container now responds with HTTP 200
- ✅ Health endpoint operational
- ✅ Secure configuration properly applied
- ✅ Production deployment successful

## 📊 System Status (as of February 18, 2026)

### Container Status
```
CONTAINER ID    IMAGE                      STATUS
ed7454975c7e    aura-dashboard-prod       Up 5+ minutes
```

### Disk Usage
- **Images:** 11.46GB (100% reclaimable if cleaned)
- **Containers:** 371.4MB
- **Volumes:** 3.76GB (31% reclaimable)
- **Build Cache:** 96.27MB
- **Free Space:** 509.88GB ✅

### System Resources
- **Available Memory:** 31.71GB ✅
- **Free Disk:** 509.88GB ✅
- **Docker Version:** 29.2.0 ✅

## 🔐 Security Features

### Headers Configured (nginx-secure.conf)
- `Strict-Transport-Security` - HSTS (max-age: 1 year)
- `X-Frame-Options` - SAMEORIGIN
- `X-Content-Type-Options` - nosniff
- `X-XSS-Protection` - 1; mode=block
- `Referrer-Policy` - strict-origin
- `Content-Security-Policy` - Strict self-only policy
- `Permissions-Policy` - Disable geolocation, microphone, camera

### Container Security
- ✅ Not running in privileged mode
- ✅ Resource limits enforced
- ✅ Read-only file system options available
- ✅ Auto-restart on failure enabled

## 📈 Monitoring & Maintenance

### Health Check Endpoint
```bash
curl http://localhost/health
# Returns: "healthy\n"
```

### View Container Logs
```powershell
docker logs -f aura-dashboard-prod
```

### View Resource Usage
```powershell
docker stats aura-dashboard-prod
```

### Backup System
```powershell
# Backup created in: Backups/backup-20260218-085209/
.\restore-backup.ps1  # Restore from backup if needed
```

## 🚨 Troubleshooting

### Container not responding
```powershell
.\diagnose-docker.ps1
```

### Check for errors
```powershell
docker logs --tail 50 aura-dashboard-prod
```

### Port already in use
```powershell
.\cleanup-docker.ps1  # Cleans up unused containers/images
docker ps  # Check running containers
docker stop <container_id>  # Stop conflicting container
```

### System health issues
```powershell
.\system-health.ps1
```

### Free up disk space
```powershell
docker system prune -a --volumes -f
```

## 📋 Configuration Details

### Port Mappings
- **HTTP:** 0.0.0.0:80 → container:80
- **HTTPS:** 0.0.0.0:443 → container:443 (with secure config)

### Resource Limits
- **Memory:** 512MB (hard limit)
- **CPU:** 1.0 core (hard limit)
- **Swap:** Disabled

### Restart Policy
- **Policy:** unless-stopped
- **Max Retries:** N/A (always restart on failure)
- **Delay:** 0 seconds

### File Structure
```
├── Dockerfile              # Standard Nginx image
├── Dockerfile.secure       # Production-hardened image
├── nginx.conf             # Standard Nginx config
├── nginx-secure.conf      # Enhanced security config
├── index.html             # Web content
├── deploy-production.ps1  # Production deployment
├── system-health.ps1      # Health check
├── test-dashboard.ps1     # Test suite
├── diagnose-docker.ps1    # Diagnostics
├── auto-backup.ps1        # Backup system
└── Backups/               # Backup storage
```

## 🔧 Advanced Configuration

### Modify Resource Limits
Edit `deploy-production.ps1`:
```powershell
docker run -d `
  --memory "512m" `      # Change memory limit
  --cpus "1.0" `         # Change CPU limit
  aura-dashboard-prod
```

### Update Security Headers
Edit `nginx-secure.conf`:
```nginx
add_header X-Custom-Header "value" always;
```

### Rebuild Container
```powershell
docker build -t aura-dashboard-prod -f Dockerfile.secure .
docker stop aura-dashboard-prod
docker run -d --name aura-dashboard-prod -p 80:80 aura-dashboard-prod
```

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Run `.\diagnose-docker.ps1` to gather diagnostics
3. Check logs with `docker logs aura-dashboard-prod`
4. Review system health with `.\system-health.ps1`

## 📝 Version History

### v1.0 - Production Release (Feb 18, 2026)
- ✅ Fixed nginx-secure.conf try_files directive
- ✅ Fixed Dockerfile.secure config deletion bug
- ✅ Deployed production container with resource limits
- ✅ Verified health checks and HTTP 200 response
- ✅ Committed fixes to main branch (8f108ec)

### Improvements Made
- Recovered 99GB of disk space via `docker system prune`
- Stabilized configuration files
- Implemented resource limits for production
- Added comprehensive test suite
- Enabled auto-restart capability

## ✅ Deployment Checklist

- [x] System resources verified (31.71GB RAM, 509.88GB disk)
- [x] Security scan completed
- [x] Backup created
- [x] Production container built
- [x] Health check passing
- [x] HTTP 200 response verified
- [x] Resource limits configured
- [x] Auto-restart enabled
- [x] Changes committed to git

---

**Last Updated:** February 18, 2026  
**Status:** ✅ Production Ready  
**Commit:** 8f108ec
