# Docker Permission Quick Fix

## 🚀 Instant Solution (No Logout Required!)

Run this **ONE command**:

```bash
./fix_docker_and_run.sh
```

This will:
- ✅ Add you to docker group (if needed)
- ✅ Start a new session with Docker access
- ✅ Run Pulse Agent with Docker metrics working
- ✅ **No logout/login required!**

## ✅ What You'll See

**Before (without Docker):**
```
WARNING - Failed to connect to Docker daemon: Permission denied
Docker not connected, returning minimal metrics
```

**After (with Docker):**
```
✅ Connected to Docker daemon
✅ Docker metrics collected successfully
```

## 📊 Docker Metrics Included

With Docker working, you'll get:
```json
"docker_metrics": {
  "system": {
    "daemon_status": "running",
    "version": "24.0.7",
    "containers": { "total": 5, "running": 3, "stopped": 2 }
  },
  "summary": {
    "total_containers": 5,
    "running_containers": 3,
    "healthy_containers": 3
  },
  "containers": [
    {
      "name": "web-server",
      "image": "nginx:latest",
      "state": "running",
      "status": "Up 2 hours (healthy)"
    }
  ]
}
```

## 🔄 All Available Scripts

| Script | What It Does | When to Use |
|--------|--------------|-------------|
| **./fix_docker_and_run.sh** | **Fixes Docker + Runs Agent** | **Use this!** No logout needed |
| ./setup_docker.sh | Diagnoses and fixes permissions | Manual Docker setup |
| ./run.sh | Just runs the agent | After Docker is fixed |

## 💡 Why This Works

The `fix_docker_and_run.sh` script uses `sg` (set group) command which:
- Creates a new session with docker group active
- No logout/login required
- Changes persist for the entire script execution
- Perfect for automated deployments

## 🔁 For Persistent Access (Optional)

If you want Docker to work in **all** terminals permanently:

### Option 1: Logout/Login (Most Reliable)
```bash
# Already added to docker group by the script
# Just logout and login to your system
```

### Option 2: Restart Shell
```bash
exec su -l $USER
cd /tmp/pulse_agent_v2
docker ps  # Should work now!
```

### Option 3: Add to .bashrc (Advanced)
Add this to your `~/.bashrc`:
```bash
# Auto-activate docker group
if groups | grep -q '\bdocker\b'; then
    if ! docker ps &>/dev/null 2>&1; then
        exec sg docker "$BASH_SOURCE"
    fi
fi
```

## 🧪 Test Docker Access

```bash
# Test if Docker works
docker ps

# Should show running containers
# If it works, you can use ./run.sh directly
```

## 📝 Quick Commands

```bash
# Fix Docker and run (recommended)
./fix_docker_and_run.sh

# Check if you're in docker group
groups | grep docker

# Test Docker access
docker ps

# Run normally (after Docker is fixed)
./run.sh

# Manual permission fix
./setup_docker.sh
```

## ❓ FAQ

**Q: Do I need to run `fix_docker_and_run.sh` every time?**
A: Only until you logout/login. After that, use `./run.sh` directly.

**Q: Can I schedule this with cron?**
A: Yes! Use `fix_docker_and_run.sh` in your cron job:
```bash
0 * * * * cd /tmp/pulse_agent_v2 && ./fix_docker_and_run.sh >> /var/log/pulse-agent.log 2>&1
```

**Q: What if I don't have Docker installed?**
A: The agent works fine without Docker. Docker metrics will just be empty.

**Q: Is this secure?**
A: Yes, it only uses the docker group you're already added to. Same as `newgrp docker` but automated.

**Q: Will this affect my system?**
A: No, it only affects the agent process. Your other terminals remain unchanged.

## 🎯 Recommended Workflow

### First Time Setup
```bash
cd /tmp/pulse_agent_v2
./install.sh              # Install dependencies
./fix_docker_and_run.sh  # Fix Docker + Run
```

### Daily Use (After Logout/Login)
```bash
./run.sh                  # Just run normally
```

### If Docker Breaks Again
```bash
./fix_docker_and_run.sh  # Instant fix
```

---

**TL;DR:** Just run `./fix_docker_and_run.sh` and Docker will work! 🚀
