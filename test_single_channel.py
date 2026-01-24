#!/usr/bin/env python3
import requests
import json

# Test DAZN 1 específico
content_id = "7ba1f321f4d0791b7ebd42f41a07c1cd1479e784"

url = f"http://localhost:6878/server/api"
params = {
    'method': 'get_media_files',
    'api_version': '3',
    'content_id': content_id
}

print(f"Testing: {content_id}")
print(f"URL: {url}")
print(f"Params: {params}")
print("-" * 80)

try:
    response = requests.get(url, params=params, timeout=15)
    print(f"Status: {response.status_code}")
    print(f"Response:")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    # Check logic
    print("-" * 80)
    print("Logic check:")
    
    if 'error' in data:
        print(f"  'error' in data: True")
        print(f"  data['error']: {data['error']}")
        print(f"  data['error'] is not None: {data['error'] is not None}")
        print(f"  bool(data['error']): {bool(data['error'])}")
    
    if 'result' in data:
        print(f"  'result' in data: True")
        if 'files' in data['result']:
            print(f"  'files' in data['result']: True")
            files = data['result']['files']
            print(f"  len(files): {len(files)}")
            print(f"  files: {files}")
            
            if files and len(files) > 0:
                print(f"\n✅ SHOULD BE ONLINE")
            else:
                print(f"\n❌ SHOULD BE OFFLINE (empty files)")
        else:
            print(f"  'files' in data['result']: False")
            print(f"\n❌ SHOULD BE OFFLINE (no files key)")
    else:
        print(f"  'result' in data: False")
        print(f"\n❌ SHOULD BE OFFLINE (no result)")
        
except Exception as e:
    print(f"❌ Exception: {e}")
