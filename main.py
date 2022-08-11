import os
from urllib.parse import urljoin

import httpx
import uvicorn
from fastapi import Depends, FastAPI, Request, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic()

base_url = 'https://cloud.mongodb.com/api/atlas/v1.0/'
allowed_http_methods = ['DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT']


@app.api_route('/{uri:path}', methods=allowed_http_methods)
async def proxy(uri: str, request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    digest_auth = httpx.DigestAuth(credentials.username, credentials.password)
    # NOTE: uri = request.path_params['uri']; but need param for swagger page
    url = urljoin(base_url, uri)
    response = await async_httpx(method=request.method, url=url, auth=digest_auth, params=request.query_params)
    return Response(
        status_code=response.status_code,
        content=response.text,
        headers={key: val for key, val in response.headers.items() if key in ['content-type']}
    )


async def async_httpx(*args, **kwargs):
    async with httpx.AsyncClient() as client:
        return await client.request(*args, **kwargs)


if __name__ == '__main__':
    service_port = int(os.environ.get('SERVICE_PORT', '8000'))
    uvicorn.run('main:app', host='0.0.0.0', port=service_port, reload=True)
