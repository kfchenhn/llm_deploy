#!/bin/bash

response=$（curl -s -X 'POST' \
  'http://10.254.25.12:8777/api/local_doc_qa/list_knowledge_base \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
        "user_id": "zzp" }'
  )

echo $response | python -c 'import sys, json; import pprint; pprint.pprint(json.load(sys.stdin))'