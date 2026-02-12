# Pulse Agent v2 - Quick Start Guide

Get up and running in 3 minutes!

## 🚀 Installation (1 minute)

```bash
cd /tmp/pulse_agent_v2
./install.sh
```

This will:
- ✅ Install all Python dependencies
- ✅ Create `.env` file from template
- ✅ Create data directory
- ✅ Make scripts executable

## ⚙️ Configuration (1 minute)

Edit the `.env` file with your settings:

```bash
nano .env
```

**Required fields:**
```bash
# Database Connection
PA_DB_HOST=localhost           # Your database host
PA_DB_PORT=5432               # Your database port
PA_DB_NAME=platform2          # Your database name
PA_DB_USER=postgres           # Your database user
PA_DB_PASSWORD=your_password  # Your database password

# API Endpoint
PA_PUSH_URL=https://your-api.com/endpoint
PA_PUSH_TOKEN=your-bearer-token-here

# Client Information
PA_CLIENT_ID=your-client-id
PA_SITE_ID=your-site-id
```

**Optional fields:**
```bash
PA_DB_TYPE=postgresql         # or mysql
PA_DB_SSL_MODE=prefer        # disable, allow, prefer, require
PA_DATA_DIR=/tmp/pulse-agent-data
PA_TIMEOUT=30
```

Save and exit (Ctrl+X, then Y, then Enter).

## ▶️ Run (30 seconds)

```bash
./run.sh
```

You should see:
```
✅ Database connection successful
✅ Queries executed
✅ Metrics collected
✅ HTTP 201 Created
✅ Pulse Agent completed successfully
```

## ✅ Verify

Check the output:
- **Database metrics** collected (images, tasks, etc.)
- **System metrics** collected (CPU, memory, disks)
- **Docker metrics** collected (containers)
- **HTTP 201** response from API
- **State file** updated with batch_index and timestamp

## 🔄 Schedule (Optional)

### Using Cron

Run every hour:
```bash
crontab -e
```

Add this line:
```bash
0 * * * * cd /tmp/pulse_agent_v2 && ./run.sh >> /var/log/pulse-agent.log 2>&1
```

### Using Systemd

See `README.md` for systemd timer setup.

## 🧪 Test Commands

### Test Database Connection
```bash
python3 -c "
from pulse_agent_complete.config import Config
from pulse_agent_complete.db_client import DatabaseClient

db = DatabaseClient(
    db_type=Config.DB_TYPE,
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    database=Config.DB_NAME,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD
)
db.connect()
print('✓ Database connection successful')
db.disconnect()
"
```

### Test Configuration
```bash
python3 -c "
from pulse_agent_complete.config import Config
print('Database:', Config.DB_HOST)
print('Push URL:', Config.PUSH_URL)
print('Client ID:', Config.CLIENT_ID)
"
```

### View Logs
```bash
./run.sh 2>&1 | tee pulse-agent.log
```

## 🐛 Common Issues

### "No module named 'dotenv'"
```bash
pip install python-dotenv
```

### "Database connection failed"
- Check database credentials in `.env`
- Verify database is running
- Test with: `psql -h localhost -U postgres -d platform2`

### "Permission denied: /var/lib/pulse-agent"
Change data directory in `.env`:
```bash
PA_DATA_DIR=/tmp/pulse-agent-data
```

### "Docker permission denied"
```bash
sudo usermod -aG docker $USER
newgrp docker
```

## 📊 Expected Output

```
2026-02-10 12:00:00 - INFO - Pulse Agent v2.0.0
2026-02-10 12:00:00 - INFO - Push URL: https://your-api.com/endpoint
2026-02-10 12:00:00 - INFO - Database: postgresql://user@host:5432/db
2026-02-10 12:00:00 - INFO - Current batch_index: 1
2026-02-10 12:00:00 - INFO - Query time range: 2026-02-10T11:00:00.000Z to 2026-02-10T12:00:00.000Z
2026-02-10 12:00:00 - INFO - Connected to postgresql database
2026-02-10 12:00:00 - INFO - Docker metrics collected successfully
2026-02-10 12:00:00 - INFO - System metrics collected successfully
2026-02-10 12:00:00 - INFO - Pushing data to: https://your-api.com/endpoint
2026-02-10 12:00:00 - INFO - HTTP Status Code: 201
2026-02-10 12:00:00 - INFO - [SUCCESS] PUSH: Data delivered successfully
2026-02-10 12:00:00 - INFO - Updated batch_index to 2
2026-02-10 12:00:00 - INFO - Pulse Agent execution completed successfully
```

## 📚 Next Steps

- **Customize queries**: Edit `queries.json` to add/modify SQL queries
- **Schedule execution**: Set up cron or systemd timer
- **Monitor logs**: Set up log rotation and monitoring
- **Production deployment**: Move to proper directory and secure credentials

## 📖 Full Documentation

See `README.md` for complete documentation including:
- Detailed configuration options
- Payload format specification
- Advanced features
- Deployment options
- Troubleshooting guide

---

**Need Help?** Check `README.md` or contact the development team.
