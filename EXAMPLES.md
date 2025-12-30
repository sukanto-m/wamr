# WhoAteMyRAM Examples

This document shows various usage scenarios and outputs.

## Example 1: Healthy System

```bash
$ wamr

💾 WhoAteMyRAM - Memory Analysis
==================================================

🟢 HEALTHY - 32.4% used (5.2 GB / 16.0 GB)

📊 Summary: System memory is well-managed. All major memory 
consumers are active development tools with expected usage 
patterns. No action needed.

🟢 SAFE TO IGNORE (5 processes)

• code (1.2 GB) - Active VS Code with 3 workspaces
• chrome (856 MB) - 12 tabs, all actively used
• node (642 MB) - Development server
• slack (428 MB) - Messaging client
• ollama (380 MB) - This analysis tool

💰 Total Reclaimable: ~0 MB
```

---

## Example 2: High Memory Usage

```bash
$ wamr

💾 WhoAteMyRAM - Memory Analysis
==================================================

🔴 CRITICAL - 91.3% used (14.6 GB / 16.0 GB)

📊 Summary: CRITICAL memory pressure detected. System is 
close to OOM (Out Of Memory) condition. Immediate action 
recommended to prevent system instability.

🔴 HIGH PRIORITY (3 issues)

• chrome (PID 4523) - 6.8 GB
  Reason: 89 tabs open across 3 windows, many unused
  Action: Close browser and restart with fewer tabs
  💻 Command: killall chrome (save work first!)

• elasticsearch (PID 8912) - 4.2 GB
  Reason: Development instance with default heap size
  Action: Reduce heap size or stop if not in use
  💻 Command: systemctl stop elasticsearch

• docker (PID 1234) - 2.1 GB
  Reason: 12 stopped containers still in memory
  Action: Remove stopped containers
  💻 Command: docker container prune -f

💰 Total Reclaimable: ~13.1 GB
```

---

## Example 3: Memory Leak Detection

```bash
$ wamr

💾 WhoAteMyRAM - Memory Analysis
==================================================

🟡 WARNING - 68.7% used (11.0 GB / 16.0 GB)

📊 Summary: Potential memory leak detected in Node.js 
process. Memory growth pattern suggests improper cleanup.

🔴 HIGH PRIORITY (1 issue)

• node (PID 15234) - 4.5 GB (growing steadily)
  Reason: Memory increased from 800MB to 4.5GB in 3 hours
           Likely memory leak in application code
  Action: Restart process and investigate code for leaks
  💻 Command: kill 15234 && npm run dev
  💡 Tip: Check for event listeners, closures, or large caches

🟡 MEDIUM PRIORITY (1 issue)

• python (PID 9876) - 2.1 GB
  Reason: Long-running script with growing memory
  Action: Review for memory leaks, consider periodic restarts
```

---

## Example 4: Container Focus

```bash
$ wamr

💾 WhoAteMyRAM - Memory Analysis
==================================================

🟡 WARNING - 71.2% used (11.4 GB / 16.0 GB)

📊 Summary: Multiple Docker containers consuming significant 
memory. Several appear to be from old projects.

🔴 HIGH PRIORITY (2 issues)

• containerd-shim (PID 7234) - 3.2 GB
  Container: old-project_web_1
  Reason: Container hasn't been accessed in 21 days
  Action: Stop and remove unused container
  💻 Command: docker stop old-project_web_1 && docker rm old-project_web_1

• containerd-shim (PID 7891) - 1.8 GB
  Container: test_db_1
  Reason: Test database from 2 weeks ago still running
  Action: Stop test containers
  💻 Command: docker-compose -f test/docker-compose.yml down
```

---

## Example 5: Development Environment

```bash
$ wamr

💾 WhoAteMyRAM - Memory Analysis
==================================================

🟡 WARNING - 73.5% used (11.8 GB / 16.0 GB)

📊 Summary: Typical development environment with multiple 
tools running. Some optimization possible.

🟡 MEDIUM PRIORITY (2 issues)

• java (PID 4321) - 2.1 GB
  Reason: IntelliJ IDEA with large heap
  Action: Reduce heap if not actively using
  💻 Command: Edit idea.vmoptions: -Xmx1024m

• node (PID 8765) - 1.4 GB
  Reason: Multiple webpack dev servers (3 projects)
  Action: Stop unused dev servers
  💻 Command: pkill -f webpack-dev-server

🟢 SAFE TO IGNORE (4 processes)

• code (1.2 GB) - Active editor
• postgres (896 MB) - Local database in use  
• redis (324 MB) - Cache server
• slack (442 MB) - Messaging

💰 Total Reclaimable: ~3.5 GB
```

---

## Example 6: Quick Check (No LLM)

```bash
$ wamr --no-llm

Memory: 7234.5/16000.0 MB (45.2%)

PID      USER         MEMORY       COMMAND
----------------------------------------------------------------------
4523     username     3.2 GB       /usr/bin/chrome
8912     username     1.8 GB       /usr/bin/code
15234    username     1.4 GB       node server.js
9876     username     896.5 MB     /usr/bin/slack
7891     username     642.3 MB     python main.py
```

---

## Example 7: JSON Output (for scripting)

```bash
$ wamr --json | jq '.high_priority[0]'

{
  "process": "chrome",
  "pid": 4523,
  "memory_mb": 3276.8,
  "reason": "Multiple instances with 47 tabs",
  "action": "Close idle tabs",
  "command": "chrome://discards"
}
```

---

## Example 8: Different Models

```bash
# Fast analysis (smaller model)
$ wamr --model llama3.2:1b

# Better quality (larger model)  
$ wamr --model llama3.1:8b

# Alternative model
$ wamr --model qwen2.5:7b
```

---

## Tips

### When to Use `--no-llm`
- Quick health checks
- When Ollama isn't running
- For scripting/automation
- When you just need numbers

### When to Use Full Analysis
- System feels slow
- Investigating high memory
- Not sure what's safe to kill
- Want actionable recommendations

### Automation Example

```bash
#!/bin/bash
# Alert if memory usage is critical

USAGE=$(wamr --no-llm | grep "Memory:" | awk '{print $4}' | tr -d '(%)')

if [ "$USAGE" -gt 90 ]; then
    echo "CRITICAL: Memory at ${USAGE}%"
    wamr --json > /tmp/mem-analysis.json
    # Send alert, take action, etc.
fi
```
