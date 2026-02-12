#!/usr/bin/env python3
"""
Test script to verify Pulse Agent v2 setup
"""

import sys
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all imports work"""
    print("Testing imports...")
    try:
        from pulse_agent_complete.config import Config
        from pulse_agent_complete.db_client import DatabaseClient, QueryLoader
        from pulse_agent_complete.aggregator import DataAggregator
        from pulse_agent_complete.http_client import HttpClient
        from pulse_agent_complete.state_manager import StateManager
        from pulse_agent_complete.docker_client import DockerClient
        from pulse_agent_complete.system_client import SystemClient
        print("  ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from pulse_agent_complete.config import Config

        print(f"  Database: {Config.DB_TYPE}://{Config.DB_USER}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
        print(f"  Push URL: {Config.PUSH_URL}")
        print(f"  Client ID: {Config.CLIENT_ID}")
        print(f"  Site ID: {Config.SITE_ID}")
        print(f"  Data Dir: {Config.get_data_dir()}")
        print("  ✓ Configuration loaded")
        return True
    except Exception as e:
        print(f"  ✗ Configuration failed: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from pulse_agent_complete.config import Config
        from pulse_agent_complete.db_client import DatabaseClient

        db = DatabaseClient(
            db_type=Config.DB_TYPE,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            ssl_mode=Config.DB_SSL_MODE
        )

        db.connect()
        if db.is_connected():
            print("  ✓ Database connection successful")
            db.disconnect()
            return True
        else:
            print("  ✗ Database connection failed")
            return False
    except Exception as e:
        print(f"  ✗ Database connection failed: {e}")
        return False

def test_queries():
    """Test query loading"""
    print("\nTesting query loading...")
    try:
        from pulse_agent_complete.config import Config
        from pulse_agent_complete.db_client import QueryLoader

        queries_file = Config.get_queries_filepath()
        loader = QueryLoader(queries_file)

        print(f"  Queries file: {queries_file}")
        print(f"  Loaded {len(loader.queries)} queries")
        print("  ✓ Queries loaded successfully")
        return True
    except Exception as e:
        print(f"  ✗ Query loading failed: {e}")
        return False

def test_docker():
    """Test Docker connection"""
    print("\nTesting Docker connection...")
    try:
        from pulse_agent_complete.docker_client import DockerClient

        client = DockerClient()
        if client.is_connected():
            metrics = client.get_detailed_metrics()
            print(f"  Docker version: {metrics['system']['version']}")
            print(f"  Containers: {metrics['summary']['total_containers']}")
            print("  ✓ Docker connection successful")
            return True
        else:
            print("  ⚠ Docker not available (this is OK)")
            return True
    except Exception as e:
        print(f"  ⚠ Docker test failed: {e} (this is OK)")
        return True

def test_system():
    """Test system metrics"""
    print("\nTesting system metrics...")
    try:
        from pulse_agent_complete.system_client import SystemClient

        client = SystemClient()
        if client.is_available():
            metrics = client.get_all_metrics()
            print(f"  Hostname: {metrics['system']['hostname']}")
            print(f"  CPU Count: {metrics['system']['cpu_count']}")
            print(f"  Memory: {metrics['memory']['usage_percent']}% used")
            print(f"  Disks: {len(metrics['disks'])} mounted")
            print("  ✓ System metrics collected")
            return True
        else:
            print("  ✗ psutil not available")
            return False
    except Exception as e:
        print(f"  ✗ System metrics failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("  Pulse Agent v2 - Setup Verification")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Queries", test_queries),
        ("Docker", test_docker),
        ("System Metrics", test_system)
    ]

    results = {}
    for name, test_func in tests:
        results[name] = test_func()

    print("\n" + "=" * 60)
    print("  Test Results")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name:20} {status}")

    print("\n" + "=" * 60)
    print(f"  {passed}/{total} tests passed")

    if passed == total:
        print("  ✅ Setup is complete and ready to use!")
    elif passed >= total - 1:
        print("  ⚠️  Setup is mostly complete (minor issues)")
    else:
        print("  ❌ Setup incomplete - please fix the errors above")

    print("=" * 60)

    return 0 if passed >= total - 1 else 1

if __name__ == "__main__":
    sys.exit(main())
