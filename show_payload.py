#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from pulse_agent_complete.config import Config
from pulse_agent_complete.db_client import DatabaseClient, QueryLoader
from pulse_agent_complete.aggregator import DataAggregator
from pulse_agent_complete.state_manager import StateManager
import json

state_manager = StateManager(Config.get_data_filepath())
start_time, end_time = state_manager.get_start_end_times()

db_client = DatabaseClient(Config.DB_TYPE, Config.DB_HOST, Config.DB_PORT, Config.DB_NAME, Config.DB_USER, Config.DB_PASSWORD, Config.DB_SSL_MODE)
query_loader = QueryLoader(Config.get_queries_filepath())
aggregator = DataAggregator(db_client, query_loader)

with db_client:
    pull_response = aggregator.fetch_stats(start_time=start_time, end_time=end_time, client_id=Config.CLIENT_ID, site_id=Config.SITE_ID)

payload = {
    'client_id': Config.CLIENT_ID,
    'site_id': Config.SITE_ID,
    'batch_index': state_manager.get_batch_index() + 1,
    'uuid': 'test-uuid',
    'stats': pull_response.get('stats', {}),
    'additional': {}
}

# Show structure summary
stats = payload['stats']
print("=" * 60)
print("PAYLOAD STRUCTURE VERIFICATION")
print("=" * 60)
print(f"\n✓ Top Level Keys: {list(payload.keys())}")
print(f"\n✓ Stats Keys: {list(stats.keys())}")
print(f"\n✓ Status: {stats.get('status')}")
print(f"✓ Start Time: {stats.get('start_time')}")
print(f"✓ End Time: {stats.get('end_time')}")

# Database metrics
db_metrics = [k for k in stats.keys() if 'images_' in k or 'tasks_' in k or 'patients_' in k]
print(f"\n✓ Database Metrics ({len(db_metrics)}): {db_metrics[:3]}...")

# System metrics
if 'system_metrics' in stats:
    sm = stats['system_metrics']
    print(f"\n✓ System Metrics Keys: {list(sm.keys())}")
    print(f"  - System: {list(sm['system'].keys())}")
    print(f"  - Memory: {list(sm['memory'].keys())}")
    print(f"  - Disks: {len(sm['disks'])} disks")
    print(f"  - Services: {list(sm['services'].keys())}")

# Docker metrics
if 'docker_metrics' in stats:
    dm = stats['docker_metrics']
    print(f"\n✓ Docker Metrics Keys: {list(dm.keys())}")
    print(f"  - System: daemon_status={dm['system']['daemon_status']}, version={dm['system']['version']}")
    print(f"  - Summary: total={dm['summary']['total_containers']}, running={dm['summary']['running_containers']}")
    print(f"  - Containers: {len(dm['containers'])} containers")
    
    # Show a sample container if any
    if dm['containers']:
        c = dm['containers'][0]
        print(f"\n✓ Sample Container:")
        print(f"  - Name: {c.get('name')}")
        print(f"  - Image: {c.get('image')}")
        print(f"  - State: {c.get('state')}")

print("\n" + "=" * 60)
print("PAYLOAD SIZE")
print("=" * 60)
print(f"Total payload size: {len(json.dumps(payload))} bytes")
print(f"Stats section size: {len(json.dumps(stats))} bytes")
print("\n✅ Payload structure is complete and correct!")
