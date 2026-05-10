import asyncio
import httpx

# Real CDN URL from last scrape
test_url = "https://scontent-atl3-2.xx.fbcdn.net/v/t39.30808-6/690827428_1442307277943465_5584583160714562708_n.jpg?_nc_cat=102&ccb=1-7&_nc_sid=7b2446&_nc_ohc=o3dBkCvQIe4Q7kNvwH44N9h&_nc_oc=Adqlnj8L6FMymU3RMQ_8-C_pylTNUO6KLxXwFGnL-6tYrai8Umh24HVmmlORB4ttcHE&_nc_zt=23&_nc_ht=scontent-atl3-2.xx&_nc_gid=shnh4u3Dld8Fy-tHk0xOKA&_nc_ss=72289&oh=00_Af7yLg3RIWGRcBDS3e068Tv8qi4pOVUDUsWqsRE_z-FSDQ&oe=6A05C985"

async def test_download():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    }
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        print(f"Fetching: {test_url[:80]}...")
        r = await client.get(test_url, headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('content-type')}")
        print(f"Content-Length: {len(r.content)} bytes")
        print(f"First 20 bytes: {r.content[:20]}")

asyncio.run(test_download())
