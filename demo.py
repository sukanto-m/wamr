#!/usr/bin/env python3
"""
Demo script for WhoAteMyRAM with mock LLM responses
(for testing without Ollama running)
"""

import json

# Mock analysis response
mock_analysis = {
    "summary": "System is experiencing high memory usage at 73% with multiple browser instances and development tools. Several optimization opportunities identified.",
    "high_priority": [
        {
            "process": "chrome",
            "pid": 12091,
            "memory_mb": 3276.8,
            "reason": "Multiple instances with 47 total tabs, 28 idle for >2 hours consuming excessive memory",
            "action": "Close idle tabs or restart Chrome to reclaim memory",
            "command": "chrome://discards (visit in browser to see discardable tabs)"
        },
        {
            "process": "docker-compose",
            "pid": 8432,
            "memory_mb": 2150.4,
            "reason": "Containers from 'old-project' haven't been accessed in 14 days",
            "action": "Stop unused containers to free memory",
            "command": "docker ps -a | grep old-project && docker-compose down"
        }
    ],
    "medium_priority": [
        {
            "process": "code",
            "pid": 15678,
            "memory_mb": 1024.5,
            "reason": "VS Code with 8 workspace folders loaded simultaneously",
            "action": "Close unused workspaces to reduce memory footprint",
            "command": "Close workspace folders in VS Code: File > Close Folder"
        }
    ],
    "safe_to_ignore": [
        {
            "process": "node",
            "pid": 14233,
            "memory_mb": 1482.3,
            "reason": "Active webpack dev server for current project - legitimate development usage",
            "action": "This is expected memory usage for active development"
        },
        {
            "process": "ollama",
            "pid": 9876,
            "memory_mb": 1150.0,
            "reason": "Currently running this memory analysis",
            "action": "Will be freed after analysis completes"
        },
        {
            "process": "slack",
            "pid": 7654,
            "memory_mb": 856.2,
            "reason": "Active messaging client with normal memory usage for Electron app",
            "action": "Restart if memory grows significantly higher"
        }
    ],
    "total_reclaimable_mb": 3900.0
}

# Simulated memory data
mock_memory = {
    'total_mb': 16384.0,
    'used_mb': 12000.0,
    'free_mb': 4384.0,
    'used_percent': 73.2
}

def print_demo():
    """Print a demo analysis"""
    print("\n" + "="*70)
    print("💾 WhoAteMyRAM - Memory Analysis [DEMO MODE]")
    print("="*70)
    
    # System overview
    used_percent = mock_memory['used_percent']
    status = "🟡 WARNING"
    
    def format_bytes(bytes_val: float) -> str:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} MB"
        else:
            return f"{bytes_val/1024:.1f} GB"
    
    print(f"\n{status} - {used_percent:.1f}% used ({format_bytes(mock_memory['used_mb'])} / {format_bytes(mock_memory['total_mb'])})")
    
    # Summary
    summary = mock_analysis.get('summary', '')
    print(f"\n📊 Summary: {summary}")
    
    # High priority
    high_priority = mock_analysis.get('high_priority', [])
    if high_priority:
        print(f"\n🔴 HIGH PRIORITY ({len(high_priority)} issues)")
        print("-" * 70)
        for item in high_priority:
            print(f"\n• {item.get('process', 'Unknown')} (PID {item.get('pid')}) - {format_bytes(item.get('memory_mb', 0))}")
            print(f"  Reason: {item.get('reason', 'N/A')}")
            print(f"  Action: {item.get('action', 'N/A')}")
            if item.get('command'):
                print(f"  💻 Command: {item['command']}")
    
    # Medium priority
    medium_priority = mock_analysis.get('medium_priority', [])
    if medium_priority:
        print(f"\n🟡 MEDIUM PRIORITY ({len(medium_priority)} issues)")
        print("-" * 70)
        for item in medium_priority:
            print(f"\n• {item.get('process', 'Unknown')} (PID {item.get('pid')}) - {format_bytes(item.get('memory_mb', 0))}")
            print(f"  Reason: {item.get('reason', 'N/A')}")
            print(f"  Action: {item.get('action', 'N/A')}")
            if item.get('command'):
                print(f"  💻 Command: {item['command']}")
    
    # Safe to ignore
    safe = mock_analysis.get('safe_to_ignore', [])
    if safe:
        print(f"\n🟢 SAFE TO IGNORE ({len(safe)} processes)")
        print("-" * 70)
        for item in safe:
            print(f"• {item.get('process', 'Unknown')} (PID {item.get('pid')}) - {format_bytes(item.get('memory_mb', 0))}")
            print(f"  {item.get('reason', 'N/A')}")
    
    # Total reclaimable
    reclaimable = mock_analysis.get('total_reclaimable_mb', 0)
    if reclaimable > 0:
        print(f"\n💰 Total Reclaimable: ~{format_bytes(reclaimable)}")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    print_demo()
