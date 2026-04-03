import httpx


async def fetch_html(url: str) -> str:
    """URL에서 HTML 크롤링"""
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        return response.text
