# Docker Permission Setup Guide

This guide helps you fix Docker permission issues permanently.

## 🐛 The Problem

When you see this error:
```
permission denied while trying to connect to the Docker daemon socket
```

It means your user doesn't have permission to access Docker.

## ✅ The Solution (Permanent)

We provide an automated script that fixes this:

```bash
./setup_docker.sh
```

This script will:
1. Check if you're in the docker group
2. Add you to the docker group if needed
3. Provide instructions to make it active

## 🔄 Making It Active

After running `setup_docker.sh`, you need to **refresh your session** for the changes to take effect.

### Option 1: Full Logout (Recommended)
This is the **most reliable** method:

1. **Log out completely** from your system
   - GUI: Log out from your desktop session
   - SSH: Close the SSH connection

2. **Log back in**

3. **Test it works:**
   ```bash
   docker ps
   ```
   Should work without `sudo`!

4. **Run the agent:**
   ```bash
   cd /tmp/pulse_agent_v2
   ./run.sh
   ```

### Option 2: Restart Shell (Quick)
If you can't log out:

```bash
exec su -l $USER
```

Then navigate back:
```bash
cd /tmp/pulse_agent_v2
./run.sh
```

### Option 3: newgrp (Current Terminal Only)
Only affects the current terminal session:

```bash
newgrp docker
./run.sh
```

**Note:** This only works in the current terminal. If you open a new terminal, you'll need to run `newgrp docker` again.

## 🔍 Verification

Check if you're in the docker group:
```bash
groups
```

Should show `docker` in the list.

Test Docker access:
```bash
docker ps
```

Should work without `sudo`!

## 🛠️ Manual Setup

If the script doesn't work, do it manually:

### Step 1: Add user to docker group
```bash
sudo usermod -aG docker $USER
```

### Step 2: Verify it was added
```bash
groups $USER
```

Should show `docker` in the list.

### Step 3: Log out and back in
- **GUI:** Log out from your desktop session
- **SSH:** Close the SSH connection and reconnect
- **Console:** Press Ctrl+D and log back in

### Step 4: Test
```bash
docker ps
# Should work without sudo!
```

## 🔐 Security Note

Adding a user to the `docker` group grants them **root-equivalent** privileges because they can run containers with access to the host system.

Only add trusted users to the docker group.

## 📊 What Happens Without Docker

If Docker is not accessible, the Pulse Agent will:
- ✅ Still work perfectly
- ✅ Collect all database metrics
- ✅ Collect all system metrics
- ⚠️ Return empty Docker metrics:
  ```json
  "docker_metrics": {
    "system": {
      "daemon_status": "not_connected",
      "version": "unknown",
      "containers": { "total": 0, "running": 0, "stopped": 0 }
    },
    "summary": { "total_containers": 0, "running_containers": 0, "healthy_containers": 0 },
    "containers": []
  }
  ```

This is **completely fine** if you don't need Docker metrics!

## 🚀 Quick Reference

```bash
# Check if you're in docker group
groups | grep docker

# Check if Docker access works
docker ps

# Fix permissions
./setup_docker.sh

# After fixing, log out and back in, then:
docker ps
./run.sh

# Or restart shell:
exec su -l $USER
cd /tmp/pulse_agent_v2
./run.sh
```

## 🐧 Distribution-Specific Notes

### Ubuntu/Debian
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### CentOS/RHEL/Fedora
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Arch Linux
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

## 🔧 Troubleshooting

### "docker: command not found"
Docker is not installed. Install it:
- Ubuntu/Debian: `sudo apt-get install docker.io`
- CentOS/RHEL: `sudo yum install docker`
- Fedora: `sudo dnf install docker`

Or follow official guide: https://docs.docker.com/engine/install/

### "Cannot connect to the Docker daemon"
Docker daemon is not running:
```bash
sudo systemctl start docker
sudo systemctl enable docker  # Auto-start on boot
```

### "usermod: group 'docker' does not exist"
Create the docker group:
```bash
sudo groupadd docker
sudo usermod -aG docker $USER
```

### Changes not taking effect
Make sure you've logged out and back in completely:
```bash
# Check current groups (old session)
groups

# Start new login shell
exec su -l $USER

# Check groups again (should show docker)
groups
```

### Still not working after logout
Try these in order:
1. Reboot the system: `sudo reboot`
2. Check Docker daemon: `sudo systemctl status docker`
3. Check socket permissions: `ls -la /var/run/docker.sock`
4. Verify group membership: `id -nG`

## 💡 Best Practices

1. **Always log out and back in** after adding to docker group
2. **Don't use `newgrp` in production scripts** (it creates a new shell)
3. **Test with `docker ps`** before running the agent
4. **Consider using docker socket proxy** for enhanced security in production

## 📚 Additional Resources

- [Docker Post-Installation Steps](https://docs.docker.com/engine/install/linux-postinstall/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Docker Daemon Socket Permissions](https://docs.docker.com/engine/security/protect-access/)

---

**Questions?** Check the main README.md or contact the development team.
