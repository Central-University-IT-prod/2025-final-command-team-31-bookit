from fastapi import APIRouter

from fastapi.responses import HTMLResponse

from utilities import make_http_error

router = APIRouter()

@router.get("/{p:path}", status_code=200, response_class=HTMLResponse)
async def index(p: str):
    try:
        with open("dist/index.html", "r") as f:
            return f.read()
    except:
        return make_http_error(404, "не найдено")