# Changelog

All notable changes to Pulse Agent will be documented in this file.

## [2.0.0] - 2026-02-10

### 🎉 Major Release - Complete Restructuring

#### Added
- ✅ **Automatic .env loading** using python-dotenv
- ✅ **Enhanced Docker metrics** with detailed container information
  - Daemon status and version
  - Container health checks
  - Individual container details (name, image, state, status)
- ✅ **Improved system metrics** structure
  - Simplified system info (hostname, cpu_count, load_average_1min, uptime_seconds, os_version)
  - Simplified memory info (total_bytes, used_bytes, usage_percent)
  - Disk list with filtering (excludes snap mounts and squashfs)
  - Service metrics (total_services, running_services, failed_services)
- ✅ **Installation script** (`install.sh`)
- ✅ **Run script** (`run.sh`)
- ✅ **Comprehensive documentation**
  - README.md with complete guide
  - QUICKSTART.md for fast setup
  - CHANGELOG.md (this file)

#### Changed
- 🔄 **Restructured payload format** (Breaking Change)
  - Moved `status`, `start_time`, `end_time` inside `stats` object
  - Nested `system_metrics` inside `stats`
  - Nested `docker_metrics` inside `stats`
  - Top-level structure: `client_id`, `site_id`, `batch_index`, `uuid`, `stats`, `additional`

- 🔄 **Enhanced data collection**
  - Docker metrics now collected once with `get_detailed_metrics()`
  - System metrics return disks as array instead of single object
  - Filtered out snap mounts and squashfs from disk list

- 🔄 **Field name updates**
  - `percent_used` → `usage_percent` (memory)
  - `percent_used` → `usage_percent` (disk)
  - `active` → `running_services` (services)
  - `total` → `total_services` (services)
  - `failed` → `failed_services` (services)

#### Fixed
- 🐛 Fixed .env file not being loaded automatically
- 🐛 Fixed Docker client to handle connection errors gracefully
- 🐛 Fixed system metrics to work when psutil is unavailable
- 🐛 Fixed state file permission issues with configurable data directory

#### Removed
- ❌ Removed individual Docker container count fields from top-level stats
  - `containers_running`, `containers_exited`, `containers_paused`, `containers_total`
  - Now grouped under `docker_metrics` object
- ❌ Removed `processes` from system metrics output (not in required format)
- ❌ Removed redundant fields from system info
  - `platform`, `platform_version`, `platform_release`, `architecture`
  - `cpu_count_physical`, `cpu_count_logical` (now just `cpu_count`)
  - `cpu_percent`, `load_average_5m`, `load_average_15m`, `boot_time`
- ❌ Removed redundant fields from memory info
  - `available_bytes`, `free_bytes`
  - `swap_total_bytes`, `swap_used_bytes`, `swap_free_bytes`, `swap_percent_used`

### 📦 Payload Format Changes

#### Before (v1.x)
```json
{
  "client_id": "...",
  "site_id": "...",
  "start_time": "...",
  "end_time": "...",
  "duration_ms": 3600000,
  "stats": {
    "images_pending_current": 5,
    "containers_running": 3
  },
  "system_metrics": {
    "system": {...},
    "memory": {...},
    "disk": {...}
  }
}
```

#### After (v2.0)
```json
{
  "client_id": "...",
  "site_id": "...",
  "batch_index": 23,
  "uuid": "...",
  "stats": {
    "status": "success",
    "start_time": "...",
    "end_time": "...",
    "images_pending_current": 5,
    "system_metrics": {
      "system": {...},
      "memory": {...},
      "disks": [...]
    },
    "docker_metrics": {
      "system": {...},
      "summary": {...},
      "containers": [...]
    }
  },
  "additional": {}
}
```

### 🔧 Configuration Changes

#### New Environment Variables
- None (all variables remain the same)

#### New Dependencies
- `python-dotenv>=1.0.0` - For automatic .env file loading

### 🚨 Breaking Changes

⚠️ **This is a major version with breaking changes:**

1. **Payload Structure**
   - APIs consuming the payload must be updated to handle new structure
   - `system_metrics` and `docker_metrics` are now nested inside `stats`
   - `start_time`, `end_time`, and `status` moved inside `stats`

2. **Field Names**
   - Memory: `percent_used` → `usage_percent`
   - Disks: `percent_used` → `usage_percent`, now returns array
   - Services: Field names changed (see above)

3. **Docker Metrics**
   - Individual container counts removed from top-level stats
   - Now grouped under `docker_metrics` with additional details

### 📈 Migration Guide (v1.x → v2.0)

#### Update Your Code

**Old (v1.x):**
```python
stats = response['stats']
system_metrics = response['system_metrics']
containers_running = stats['containers_running']
```

**New (v2.0):**
```python
stats = response['stats']
system_metrics = stats['system_metrics']
containers_running = stats['docker_metrics']['summary']['running_containers']
```

#### Update API Endpoints

If you have API endpoints consuming this payload, update them to:
1. Read `status`, `start_time`, `end_time` from `stats` object
2. Read `system_metrics` from `stats['system_metrics']`
3. Read `docker_metrics` from `stats['docker_metrics']`
4. Handle `disks` as array instead of single object
5. Update field name mappings for memory and services

### 🎯 Upgrade Instructions

1. **Backup your configuration:**
   ```bash
   cp .env .env.backup
   ```

2. **Copy new version:**
   ```bash
   cp -r /tmp/pulse_agent_v2 /path/to/your/location
   cd /path/to/your/location
   ```

3. **Restore configuration:**
   ```bash
   cp .env.backup .env
   ```

4. **Install dependencies:**
   ```bash
   ./install.sh
   ```

5. **Test:**
   ```bash
   ./run.sh
   ```

6. **Update API endpoints** to handle new payload structure

### 📊 Testing

Fully tested with:
- ✅ PostgreSQL 14
- ✅ Ubuntu 22.04
- ✅ Python 3.10
- ✅ Docker 24.0.7
- ✅ End-to-end API integration

### 🔗 Resources

- [README.md](README.md) - Complete documentation
- [QUICKSTART.md](QUICKSTART.md) - Fast setup guide
- [.env.example](.env.example) - Configuration template

---

## [1.0.0] - 2024-02-06

### Initial Release

- Basic database query functionality
- HTTP push to API
- State management
- System and Docker metrics collection
- Configuration via environment variables

---

**Version Format:** [MAJOR.MINOR.PATCH]
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)
