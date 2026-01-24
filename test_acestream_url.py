import aiohttp
import asyncio
import uuid
import sys

async def test_url(base_url):
    pid = str(uuid.uuid4())
    acestream_id = "16598735f228c6dff542125d0e308150b50fc715"
    url = f"{base_url}/ace/getstream?id={acestream_id}&format=json&pid={pid}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {url}")
    print(f"PID: {pid}")
    print(f"{'='*60}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                print(f"Status: {resp.status}")
                text = await resp.text()
                print(f"Response: {text[:500]}")
                return resp.status == 200
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        return False

async def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
        result = await test_url(base_url)
        print(f"\nResult: {'SUCCESS' if result else 'FAILED'}")
    else:
        print("Usage: python test_acestream_url.py <base_url>")
        print("Example: python test_acestream_url.py http://localhost:6878")

if __name__ == "__main__":
    asyncio.run(main())
