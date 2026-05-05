#!/usr/bin/env python3
"""
NC-TEST-FR-201 — Health Tool Test Script
Test the NC-SUPER-013-health.py tool directly
"""

import sys
import os
from pathlib import Path

# Add framework to path
framework_dir = Path(__file__).parent / "01_neocortex_framework"
sys.path.insert(0, str(framework_dir))

def test_health_tool():
    """Test the health tool directly"""
    print("TESTING NC-SUPER-013-HEALTH.PY")
    print("=" * 70)
    
    try:
        # Import the health tool module
        from neocortex.mcp.tools.NC_SUPER_013_health import neocortex_health
        
        print("Health tool imported successfully")
        
        # Test each action
        test_cases = [
            ("server.health", "Check server health"),
            ("server.tools_count", "Count available tools"),
            ("ssot.audit", "SSOT compliance audit"),
            ("metrics.live", "Live metrics"),
            ("watchdog.status", "Watchdog status")
        ]
        
        results = []
        
        for action, description in test_cases:
            print(f"\nTesting: {action} - {description}")
            print("-" * 40)
            
            try:
                result = neocortex_health(action)
                success = result.get('success', False)
                
                print(f"  Success: {success}")
                
                if success:
                    if action == "server.health":
                        services = result.get('services', {})
                        print(f"  Services checked: {len(services)}")
                    elif action == "server.tools_count":
                        super_tools = result.get('super_tool_files', 0)
                        total_tools = result.get('total_tool_files', 0)
                        print(f"  Super tools: {super_tools}")
                        print(f"  Total tools: {total_tools}")
                    elif action == "ssot.audit":
                        compliance = result.get('compliance_status', {}).get('R04', {})
                        rate = compliance.get('compliance_rate', 'N/A')
                        status = compliance.get('status', 'N/A')
                        print(f"  Compliance rate: {rate}")
                        print(f"  Status: {status}")
                    elif action == "metrics.live":
                        metrics = result.get('metrics', {})
                        print(f"  Metrics available: {len(metrics)}")
                    elif action == "watchdog.status":
                        running = result.get('running', False)
                        print(f"  Watchdog running: {running}")
                else:
                    error = result.get('error', 'No error message')
                    print(f"  Error: {error}")
                    
                results.append({
                    'action': action,
                    'success': success,
                    'description': description
                })
                
            except Exception as e:
                print(f"  ERROR: {e}")
                results.append({
                    'action': action,
                    'success': False,
                    'error': str(e),
                    'description': description
                })
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY:")
        
        successful = sum(1 for r in results if r.get('success'))
        total = len(results)
        
        print(f"Successful tests: {successful}/{total}")
        
        if successful >= 3:
            print("\nSTATUS: PASS - Health tool is functional")
        else:
            print("\nSTATUS: FAIL - Health tool needs debugging")
            
        return results
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're in the correct directory")
        return []
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    test_health_tool()