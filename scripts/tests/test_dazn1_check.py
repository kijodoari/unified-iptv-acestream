"""
Test directo de check_stream_availability para DAZN 1
"""
import asyncio
import aiohttp

async def test_dazn1():
    acestream_id = "7ba1f321f4d0791b7ebd42f41a07c1cd1479e784"
    base_url = "http://localhost:6878"
    
    url = f"{base_url}/server/api"
    params = {
        'method': 'get_media_files',
        'api_version': '3',
        'content_id': acestream_id
    }
    
    timeout = aiohttp.ClientTimeout(total=15)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=timeout) as response:
            print(f"Status: {response.status}")
            
            data = await response.json()
            print(f"Response: {data}")
            
            # Check if there's an error (must be non-null and non-empty)
            if 'error' in data and data['error'] is not None and data['error']:
                print(f"ERROR DETECTED: {data['error']}")
                return False
            
            # Check if we got valid result
            if 'result' in data and 'files' in data['result']:
                files = data['result']['files']
                print(f"Files found: {len(files)}")
                if files and len(files) > 0:
                    print(f"Stream is AVAILABLE")
                    return True
            
            print(f"Stream has NO FILES")
            return False

if __name__ == "__main__":
    result = asyncio.run(test_dazn1())
    print(f"\nFinal result: {result}")
