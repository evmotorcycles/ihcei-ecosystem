#!/bin/bash
python -m http.server 8080 > /dev/null 2>&1 &
echo "Server started at http://localhost:8080"
