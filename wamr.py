#!/usr/bin/env python3
"""
WhoAteMyRAM - LLM-powered memory analysis tool
"""

import sys
import subprocess
import json
import time
import os
import platform
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path

@dataclass
class ProcessInfo:
    pid: int
    name: str
    user: str
    rss_mb: float
    cmd: str
    
    def __repr__(self):
        return f"ProcessInfo(pid={self.pid}, name={self.name}, rss_mb={self.rss_mb:.1f}MB)"


class MemoryAnalyzer:
    def __init__(self):
        self.processes: List[ProcessInfo] = []
        self.total_mem_mb = 0
        self.used_mem_mb = 0
        self.free_mem_mb = 0
        
    def get_system_memory(self) -> Dict[str, float]:
        """Get system memory info from /proc/meminfo (Linux) or vm_stat (macOS)"""
        
        # macOS support
        if platform.system() == 'Darwin':
            try:
                # Get vm_stat output
                result = subprocess.run(['vm_stat'], capture_output=True, text=True, check=True)
                lines = result.stdout.strip().split('\n')
                
                page_size = 4096
                stats = {}
                
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip().rstrip('.')
                        # Handle values with spaces (like "4096 bytes")
                        value_num = ''.join(c for c in value if c.isdigit())
                        if value_num:
                            stats[key] = int(value_num)
                
                # Get page size from first line
                if 'page size of' in lines[0].lower():
                    page_size = int(''.join(c for c in lines[0] if c.isdigit()))
                
                # Calculate memory
                pages_free = stats.get('Pages free', 0)
                pages_active = stats.get('Pages active', 0)
                pages_inactive = stats.get('Pages inactive', 0)
                pages_speculative = stats.get('Pages speculative', 0)
                pages_wired = stats.get('Pages wired down', 0)
                
                free_mb = (pages_free + pages_speculative) * page_size / (1024 * 1024)
                active_mb = pages_active * page_size / (1024 * 1024)
                inactive_mb = pages_inactive * page_size / (1024 * 1024)
                wired_mb = pages_wired * page_size / (1024 * 1024)
                
                # Get total memory
                result = subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True, check=True)
                total_bytes = int(result.stdout.strip())
                total_mb = total_bytes / (1024 * 1024)
                
                used_mb = active_mb + wired_mb
                
                self.total_mem_mb = total_mb
                self.used_mem_mb = used_mb
                self.free_mem_mb = free_mb + inactive_mb
                
                return {
                    'total_mb': total_mb,
                    'used_mb': used_mb,
                    'free_mb': free_mb + inactive_mb,
                    'used_percent': (used_mb / total_mb * 100) if total_mb > 0 else 0
                }
            except Exception as e:
                print(f"⚠️  Error reading macOS memory: {e}", file=sys.stderr)
                # Fall through to demo data
        
        # Linux support
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
            
            mem_info = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':')
                    # Extract number (remove kB and whitespace)
                    value_kb = int(value.strip().split()[0])
                    mem_info[key.strip()] = value_kb / 1024  # Convert to MB
            
            self.total_mem_mb = mem_info.get('MemTotal', 0)
            mem_free = mem_info.get('MemFree', 0)
            mem_available = mem_info.get('MemAvailable', 0)
            buffers = mem_info.get('Buffers', 0)
            cached = mem_info.get('Cached', 0)
            
            self.used_mem_mb = self.total_mem_mb - mem_available
            self.free_mem_mb = mem_available
            
            return {
                'total_mb': self.total_mem_mb,
                'used_mb': self.used_mem_mb,
                'free_mb': self.free_mem_mb,
                'used_percent': (self.used_mem_mb / self.total_mem_mb * 100) if self.total_mem_mb > 0 else 0
            }
        except FileNotFoundError:
            # Running in container or restricted environment - use mock data
            print("⚠️  Running in restricted environment - using demo data", file=sys.stderr)
            self.total_mem_mb = 16384.0  # 16 GB
            self.used_mem_mb = 12000.0   # 12 GB used
            self.free_mem_mb = 4384.0
            return {
                'total_mb': self.total_mem_mb,
                'used_mb': self.used_mem_mb,
                'free_mb': self.free_mem_mb,
                'used_percent': 73.2
            }
        except Exception as e:
            print(f"Error reading memory info: {e}", file=sys.stderr)
            return {}
    
    def get_processes(self, top_n: int = 20) -> List[ProcessInfo]:
        """Get top memory-consuming processes"""
        
        # macOS support
        if platform.system() == 'Darwin':
            try:
                # macOS ps uses different flags
                cmd = ['ps', '-ax', '-m', '-o', 'pid,user,rss,command']
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                processes = []
                
                for line in lines[:top_n * 2]:  # Get extra to filter
                    parts = line.split(None, 3)
                    if len(parts) >= 4:
                        try:
                            pid = int(parts[0])
                            user = parts[1]
                            rss_kb = float(parts[2])
                            rss_mb = rss_kb / 1024
                            cmd_str = parts[3]
                            
                            # Skip kernel threads
                            if rss_mb < 1:
                                continue
                            
                            # Get process name
                            name = Path(cmd_str.split()[0]).name if cmd_str else 'unknown'
                            
                            processes.append(ProcessInfo(
                                pid=pid,
                                name=name,
                                user=user,
                                rss_mb=rss_mb,
                                cmd=cmd_str[:100]
                            ))
                        except (ValueError, IndexError):
                            continue
                
                # Sort by memory and take top_n
                processes.sort(key=lambda p: p.rss_mb, reverse=True)
                self.processes = processes[:top_n]
                return self.processes
                
            except Exception as e:
                print(f"⚠️  Error reading macOS processes: {e}", file=sys.stderr)
                # Fall through to demo data
        
        # Linux support
        try:
            # Use ps to get process info
            cmd = ['ps', 'aux', '--sort=-rss']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            processes = []
            
            for line in lines[:top_n]:
                parts = line.split(None, 10)  # Split on whitespace, max 11 parts
                if len(parts) >= 11:
                    user = parts[0]
                    pid = int(parts[1])
                    # RSS is in KB on most systems
                    rss_kb = float(parts[5])
                    rss_mb = rss_kb / 1024
                    cmd_parts = parts[10]
                    
                    # Get process name from command
                    name = Path(cmd_parts.split()[0]).name if cmd_parts else 'unknown'
                    
                    processes.append(ProcessInfo(
                        pid=pid,
                        name=name,
                        user=user,
                        rss_mb=rss_mb,
                        cmd=cmd_parts[:100]  # Truncate long commands
                    ))
            
            self.processes = processes
            return processes
            
        except Exception as e:
            # If ps fails, provide mock data for demo
            print(f"⚠️  Could not read processes - using demo data", file=sys.stderr)
            mock_processes = [
                ProcessInfo(12091, "chrome", "username", 3276.8, "/usr/bin/chrome --type=renderer"),
                ProcessInfo(8432, "docker-compose", "username", 2150.4, "docker-compose up"),
                ProcessInfo(15678, "code", "username", 1024.5, "/usr/share/code/code"),
                ProcessInfo(14233, "node", "username", 1482.3, "node server.js"),
                ProcessInfo(9876, "ollama", "username", 1150.0, "ollama serve"),
                ProcessInfo(7654, "slack", "username", 856.2, "/usr/bin/slack"),
                ProcessInfo(3421, "postgres", "username", 642.8, "postgres: main"),
                ProcessInfo(5234, "redis-server", "username", 324.5, "redis-server *:6379"),
            ]
            self.processes = mock_processes
            return mock_processes
    
    def analyze_with_llm(self, model: str = "llama3.2:3b") -> Optional[Dict]:
        """Send data to Ollama for analysis"""
        
        # Prepare data for LLM
        mem_data = self.get_system_memory()
        processes = self.get_processes()
        
        # Build prompt
        prompt = f"""You are a system administrator analyzing memory usage on a Linux system.

SYSTEM MEMORY:
- Total: {mem_data['total_mb']:.1f} MB
- Used: {mem_data['used_mb']:.1f} MB ({mem_data['used_percent']:.1f}%)
- Free: {mem_data['free_mb']:.1f} MB

TOP MEMORY CONSUMERS:
"""
        
        for i, proc in enumerate(processes[:10], 1):
            prompt += f"{i}. {proc.name} (PID {proc.pid}) - {proc.rss_mb:.1f} MB - User: {proc.user}\n"
            prompt += f"   Command: {proc.cmd}\n"
        
        prompt += """
Analyze this memory usage and provide:
1. Identify which processes are suspicious or unusual
2. Suggest which processes can be safely reduced/killed
3. Detect any potential memory leaks
4. Provide actionable recommendations

Respond in JSON format with this structure:
{
  "summary": "brief overall assessment",
  "high_priority": [
    {
      "process": "name",
      "pid": 1234,
      "memory_mb": 100.0,
      "reason": "why this is concerning",
      "action": "what to do",
      "command": "actual shell command to fix it (optional)"
    }
  ],
  "medium_priority": [...same structure...],
  "safe_to_ignore": [...same structure...],
  "total_reclaimable_mb": 1234.5
}

Only return valid JSON, no other text.
"""
        
        try:
            # Call Ollama API
            import requests
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False,
                    'format': 'json'
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result.get('response', '{}')
                
                # Parse JSON from response
                try:
                    analysis = json.loads(analysis_text)
                    return analysis
                except json.JSONDecodeError as e:
                    print(f"Error parsing LLM response as JSON: {e}", file=sys.stderr)
                    print(f"Raw response: {analysis_text[:500]}", file=sys.stderr)
                    return None
            else:
                print(f"Ollama API error: {response.status_code}", file=sys.stderr)
                return None
                
        except ImportError:
            print("Error: 'requests' library not installed. Install with: pip install requests", file=sys.stderr)
            return None
        except requests.exceptions.ConnectionError:
            print("Error: Cannot connect to Ollama. Make sure Ollama is running (ollama serve)", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error calling Ollama: {e}", file=sys.stderr)
            return None


def format_bytes(bytes_val: float) -> str:
    """Format bytes into human-readable format"""
    if bytes_val < 1024:
        return f"{bytes_val:.1f} MB"
    else:
        return f"{bytes_val/1024:.1f} GB"


def print_analysis(analysis: Dict, mem_data: Dict):
    """Pretty print the analysis results"""
    
    # Header
    print("\n" + "="*70)
    print("💾 WhoAteMyRAM - Memory Analysis")
    print("="*70)
    
    # System overview
    used_percent = mem_data['used_percent']
    if used_percent >= 80:
        status = "🔴 CRITICAL"
    elif used_percent >= 60:
        status = "🟡 WARNING"
    else:
        status = "🟢 HEALTHY"
    
    print(f"\n{status} - {used_percent:.1f}% used ({format_bytes(mem_data['used_mb'])} / {format_bytes(mem_data['total_mb'])})")
    
    # Summary
    summary = analysis.get('summary', 'No summary available')
    print(f"\n📊 Summary: {summary}")
    
    # High priority issues
    high_priority = analysis.get('high_priority', [])
    if high_priority:
        print(f"\n🔴 HIGH PRIORITY ({len(high_priority)} issues)")
        print("-" * 70)
        for item in high_priority:
            print(f"\n• {item.get('process', 'Unknown')} ({format_bytes(item.get('memory_mb', 0))})")
            print(f"  Reason: {item.get('reason', 'N/A')}")
            print(f"  Action: {item.get('action', 'N/A')}")
            if item.get('command'):
                print(f"  💻 Command: {item['command']}")
    
    # Medium priority
    medium_priority = analysis.get('medium_priority', [])
    if medium_priority:
        print(f"\n🟡 MEDIUM PRIORITY ({len(medium_priority)} issues)")
        print("-" * 70)
        for item in medium_priority:
            print(f"\n• {item.get('process', 'Unknown')} ({format_bytes(item.get('memory_mb', 0))})")
            print(f"  Reason: {item.get('reason', 'N/A')}")
            print(f"  Action: {item.get('action', 'N/A')}")
            if item.get('command'):
                print(f"  💻 Command: {item['command']}")
    
    # Safe to ignore
    safe = analysis.get('safe_to_ignore', [])
    if safe:
        print(f"\n🟢 SAFE TO IGNORE ({len(safe)} processes)")
        print("-" * 70)
        for item in safe:
            print(f"• {item.get('process', 'Unknown')} ({format_bytes(item.get('memory_mb', 0))}) - {item.get('reason', 'N/A')}")
    
    # Total reclaimable
    reclaimable = analysis.get('total_reclaimable_mb', 0)
    if reclaimable > 0:
        print(f"\n💰 Total Reclaimable: ~{format_bytes(reclaimable)}")
    
    print("\n" + "="*70 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='WhoAteMyRAM - LLM-powered memory analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--model',
        default='llama3.2:3b',
        help='Ollama model to use (default: llama3.2:3b)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output raw JSON instead of formatted text'
    )
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Skip LLM analysis, just show process list'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode with mock data (no system access required)'
    )
    
    args = parser.parse_args()
    
    # Demo mode - just run the demo script logic
    if args.demo:
        print("🎬 Running in DEMO mode (using mock data)\n")
        import importlib.util
        demo_path = Path(__file__).parent / "demo.py"
        if demo_path.exists():
            spec = importlib.util.spec_from_file_location("demo", demo_path)
            demo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(demo)
            demo.print_demo()
        else:
            print("Demo file not found. Install wamr properly to use demo mode.", file=sys.stderr)
        return
    
    analyzer = MemoryAnalyzer()
    
    # Get system info (will use mock data if /proc unavailable)
    mem_data = analyzer.get_system_memory()
    
    if not mem_data:
        print("Error: Could not read system memory information", file=sys.stderr)
        print("\nTry running with --demo flag to see example output:", file=sys.stderr)
        print("  wamr --demo", file=sys.stderr)
        sys.exit(1)
    
    # Get processes (will use mock data if ps unavailable)
    processes = analyzer.get_processes()
    
    if not processes:
        print("Error: Could not read process information", file=sys.stderr)
        print("\nTry running with --demo flag to see example output:", file=sys.stderr)
        print("  wamr --demo", file=sys.stderr)
        sys.exit(1)
    
    # No LLM mode - just show top processes
    if args.no_llm:
        print(f"\nMemory: {mem_data['used_mb']:.1f}/{mem_data['total_mb']:.1f} MB ({mem_data['used_percent']:.1f}%)\n")
        print(f"{'PID':<8} {'USER':<12} {'MEMORY':<12} {'COMMAND'}")
        print("-" * 70)
        for proc in processes[:15]:
            print(f"{proc.pid:<8} {proc.user:<12} {format_bytes(proc.rss_mb):<12} {proc.cmd[:40]}")
        print()
        return
    
    # Analyze with LLM
    print("🤖 Analyzing memory usage with LLM...", end='', flush=True)
    analysis = analyzer.analyze_with_llm(model=args.model)
    print(" Done!\n")
    
    if not analysis:
        print("Error: LLM analysis failed. Try --no-llm flag to see raw data.", file=sys.stderr)
        print("\nMake sure Ollama is running:", file=sys.stderr)
        print("  ollama serve", file=sys.stderr)
        print("\nOr use --demo mode to see example output:", file=sys.stderr)
        print("  wamr --demo", file=sys.stderr)
        sys.exit(1)
    
    # Output
    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print_analysis(analysis, mem_data)


if __name__ == '__main__':
    main()
