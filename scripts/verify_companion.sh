#!/bin/bash
echo "Verifying Port 9090..." > verify_output.txt
curl -v --max-time 5 http://localhost:9090/api/inbox >> verify_output.txt 2>&1
echo "\n\nDocker PS:" >> verify_output.txt
docker ps -a >> verify_output.txt 2>&1
