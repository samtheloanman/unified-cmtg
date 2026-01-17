#!/bin/bash
echo "=== DOCKER PS ===" > debug_status.txt
docker ps --filter "name=ag-companion-test" >> debug_status.txt 2>&1
echo "=== DOCKER LOGS ===" >> debug_status.txt
docker logs ag-companion-test >> debug_status.txt 2>&1
echo "=== CURL TEST 8002 ===" >> debug_status.txt
curl -I --max-time 10 http://localhost:8002/ >> debug_status.txt 2>&1
echo "=== TAILSCALE SERVE STATUS ===" >> debug_status.txt
tailscale serve status >> debug_status.txt 2>&1
echo "=== TAILSCALE IP ===" >> debug_status.txt
tailscale ip -4 >> debug_status.txt 2>&1
