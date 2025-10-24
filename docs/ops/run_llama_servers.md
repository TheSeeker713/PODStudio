# Running llama.cpp Servers for PODStudio

**Version**: 1.0.0  
**STEP**: 7 — Offline GGUF Agent Layer  
**Platform**: Windows 10/11  
**Last Updated**: October 23, 2025

---

## Overview

PODStudio uses **4 concurrent llama-server instances** to provide offline LLM capabilities:

| Agent | Purpose | Model | Port | Context |
|-------|---------|-------|------|---------|
| Vision | Image analysis, captions | gemma-3-12b (Q4_K_M) | 9091 | 32K |
| Dialog | Fluency, polish | discopop-zephyr-7b (Q4_K_M) | 9092 | 8K |
| Logic | Planning, reasoning | gemma-3n-e4b (Q4_K_M) | 9093 | 16K |
| Fast | Quick tasks, fallback | lfm2-1.2b (Q8_0) | 9094 | 4K |

**Total RAM usage**: ~8-12 GB with all agents running  
**CPU usage**: 50-80% during inference (Ryzen 6800H)

---

## Prerequisites

1. **llama.cpp installed**: See [external_tools.md](external_tools.md)
2. **Models downloaded**: Verify `.gguf` files exist at `J:\Models\LLM-Models-2025\models\`
3. **Free ports**: Ensure 9091-9094 are available

---

## Manual Launch (Individual Agents)

### Agent 1: Vision/Reader (Port 9091)

```powershell
llama-server.exe `
  --model "J:\Models\LLM-Models-2025\models\gemma\gemma-3-12b-q4_k_m.gguf" `
  --mmproj "J:\Models\LLM-Models-2025\models\gemma\mmproj-gemma-3-12b-f16.gguf" `
  --host 127.0.0.1 `
  --port 9091 `
  --ctx-size 32768 `
  --n-gpu-layers 0 `
  --threads 14 `
  --n-batch 512 `
  --timeout 300 `
  --log-disable
```

**Health check:**
```powershell
curl http://127.0.0.1:9091/health
```

---

### Agent 2: Dialog/Fluency (Port 9092)

```powershell
llama-server.exe `
  --model "J:\Models\LLM-Models-2025\models\zephyr\discopop-zephyr-7b-gemma-q4_k_m.gguf" `
  --host 127.0.0.1 `
  --port 9092 `
  --ctx-size 8192 `
  --n-gpu-layers 0 `
  --threads 14 `
  --n-batch 512 `
  --timeout 300 `
  --log-disable
```

**Health check:**
```powershell
curl http://127.0.0.1:9092/health
```

---

### Agent 3: Logic/Planner (Port 9093)

```powershell
llama-server.exe `
  --model "J:\Models\LLM-Models-2025\models\gemma\gemma-3n-e4b-q4_k_m.gguf" `
  --host 127.0.0.1 `
  --port 9093 `
  --ctx-size 16384 `
  --n-gpu-layers 0 `
  --threads 14 `
  --n-batch 512 `
  --timeout 300 `
  --log-disable
```

**Health check:**
```powershell
curl http://127.0.0.1:9093/health
```

---

### Agent 4: Fast/Fallback (Port 9094)

```powershell
llama-server.exe `
  --model "J:\Models\LLM-Models-2025\models\liquid\lfm2-1.2b-q8_0.gguf" `
  --host 127.0.0.1 `
  --port 9094 `
  --ctx-size 4096 `
  --n-gpu-layers 0 `
  --threads 8 `
  --n-batch 256 `
  --timeout 300 `
  --log-disable
```

**Health check:**
```powershell
curl http://127.0.0.1:9094/health
```

---

## Batch Launch (All Agents)

### PowerShell Script: `start_llama_agents.ps1`

Create this file in the PODStudio root directory:

```powershell
# PODStudio — Start all 4 llama.cpp agents
# Save as: start_llama_agents.ps1

$LLAMA_BIN = "C:\llama.cpp\llama-server.exe"  # Adjust path
$MODEL_ROOT = "J:\Models\LLM-Models-2025\models"

# Start Agent 1: Vision (Port 9091)
Start-Process -FilePath $LLAMA_BIN -ArgumentList @(
    "--model", "$MODEL_ROOT\gemma\gemma-3-12b-q4_k_m.gguf",
    "--mmproj", "$MODEL_ROOT\gemma\mmproj-gemma-3-12b-f16.gguf",
    "--host", "127.0.0.1",
    "--port", "9091",
    "--ctx-size", "32768",
    "--n-gpu-layers", "0",
    "--threads", "14",
    "--n-batch", "512",
    "--timeout", "300",
    "--log-disable"
) -WindowStyle Minimized

Write-Host "✓ Agent 1 (Vision) starting on port 9091..."
Start-Sleep -Seconds 2

# Start Agent 2: Dialog (Port 9092)
Start-Process -FilePath $LLAMA_BIN -ArgumentList @(
    "--model", "$MODEL_ROOT\zephyr\discopop-zephyr-7b-gemma-q4_k_m.gguf",
    "--host", "127.0.0.1",
    "--port", "9092",
    "--ctx-size", "8192",
    "--n-gpu-layers", "0",
    "--threads", "14",
    "--n-batch", "512",
    "--timeout", "300",
    "--log-disable"
) -WindowStyle Minimized

Write-Host "✓ Agent 2 (Dialog) starting on port 9092..."
Start-Sleep -Seconds 2

# Start Agent 3: Logic (Port 9093)
Start-Process -FilePath $LLAMA_BIN -ArgumentList @(
    "--model", "$MODEL_ROOT\gemma\gemma-3n-e4b-q4_k_m.gguf",
    "--host", "127.0.0.1",
    "--port", "9093",
    "--ctx-size", "16384",
    "--n-gpu-layers", "0",
    "--threads", "14",
    "--n-batch", "512",
    "--timeout", "300",
    "--log-disable"
) -WindowStyle Minimized

Write-Host "✓ Agent 3 (Logic) starting on port 9093..."
Start-Sleep -Seconds 2

# Start Agent 4: Fast (Port 9094)
Start-Process -FilePath $LLAMA_BIN -ArgumentList @(
    "--model", "$MODEL_ROOT\liquid\lfm2-1.2b-q8_0.gguf",
    "--host", "127.0.0.1",
    "--port", "9094",
    "--ctx-size", "4096",
    "--n-gpu-layers", "0",
    "--threads", "8",
    "--n-batch", "256",
    "--timeout", "300",
    "--log-disable"
) -WindowStyle Minimized

Write-Host "✓ Agent 4 (Fast) starting on port 9094..."
Start-Sleep -Seconds 3

Write-Host "`n✅ All 4 LLM agents launched!"
Write-Host "   Vision:  http://127.0.0.1:9091"
Write-Host "   Dialog:  http://127.0.0.1:9092"
Write-Host "   Logic:   http://127.0.0.1:9093"
Write-Host "   Fast:    http://127.0.0.1:9094"
Write-Host "`nRun 'curl http://127.0.0.1:9091/health' to verify."
```

**Run:**
```powershell
.\start_llama_agents.ps1
```

---

## Stop All Agents

### PowerShell Script: `stop_llama_agents.ps1`

```powershell
# PODStudio — Stop all llama-server processes
# Save as: stop_llama_agents.ps1

Get-Process -Name "llama-server" -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "✅ All llama-server processes stopped."
```

**Run:**
```powershell
.\stop_llama_agents.ps1
```

---

## Verify All Agents

### PowerShell Health Check

```powershell
# Check all 4 agent health endpoints

$ports = @(9091, 9092, 9093, 9094)
$agents = @("Vision", "Dialog", "Logic", "Fast")

for ($i = 0; $i -lt $ports.Length; $i++) {
    $port = $ports[$i]
    $agent = $agents[$i]
    
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$port/health" -TimeoutSec 5
        Write-Host "✓ $agent (port $port): OK" -ForegroundColor Green
    } catch {
        Write-Host "✗ $agent (port $port): FAILED" -ForegroundColor Red
    }
}
```

---

## Troubleshooting

### Port Already in Use

```powershell
# Find process using port 9091
netstat -ano | findstr :9091

# Kill process by PID
taskkill /PID <PID> /F
```

### Model File Not Found

Verify paths in registry match actual file locations:
```powershell
Test-Path "J:\Models\LLM-Models-2025\models\gemma\gemma-3-12b-q4_k_m.gguf"
```

### High CPU Usage

- Reduce `--threads` value (try 10 instead of 14)
- Reduce `--ctx-size` to lower memory usage
- Close other CPU-intensive applications

### Slow Response Times

- Check `--threads` matches CPU cores
- Ensure models are Q4 or Q8 quantized (not F16/F32)
- Increase `--n-batch` for better throughput

### Server Won't Start

- Check Windows Firewall isn't blocking localhost
- Verify llama-server.exe version is compatible (use latest)
- Check for antivirus interference

---

## Integration with PODStudio

Once all agents are running, PODStudio's backend can access them:

- **Health API**: `/api/llm/health` — Shows 4/4 agents online
- **Prompt generation**: Routes to appropriate agent based on task
- **Fallback**: Uses `agent_fast` if primary agent fails

**Next**: See [prompt_templates_spec.md](../specs/prompt_templates_spec.md) for agent routing logic.

---

## Performance Expectations

| Agent | Cold Start | Inference (100 tokens) | RAM Usage |
|-------|------------|------------------------|-----------|
| Vision | 5-8s | 3-5s | 3-4 GB |
| Dialog | 3-5s | 2-4s | 2-3 GB |
| Logic | 4-6s | 2-4s | 2.5-3.5 GB |
| Fast | 1-2s | 0.5-1s | 800 MB - 1.5 GB |

**Total system impact**: 8-12 GB RAM, 50-80% CPU during active inference.

---

**End of run_llama_servers.md**
