from fastapi import APIRouter, Request, UploadFile, File, status
from starlette.responses import JSONResponse, FileResponse, Response

from cfg import *
from db import DB
from utilities import make_http_error

router = APIRouter()
@router.post("")
async def sign_up_document(request: Request,
                  documents: list[UploadFile] = File(...)):
    dbcon = DB()
    token = str(request.headers.get("Authorization"))
    user = dbcon.get_user_by_token(token)

    if not user:
        return make_http_error(403, "Токен некорректный")

    user_id = user['id']
    if not dbcon.get_user_by_id(user_id):
        return make_http_error(404, "Пользователь не найден.")

    dbcon.add_documents(documents, user_id)
    return JSONResponse(status_code=200, content="документ загружен")

@router.get("/paths")
async def get_doc(request: Request):
    dbcon = DB()
    token = str(request.headers.get("Authorization"))
    user = dbcon.get_user_by_token(token)

    if not user:
        return make_http_error(404, "Пользователь не найден.")

    docs_names = dbcon.get_docs_by_user_id(user['id'])
    return docs_names


@router.get("/{doc}")
async def get_doc(request: Request, response: Response, doc: str):
    token = str(request.headers.get("Authorization"))
    dbcon = DB()
    user = dbcon.get_user_by_token(token)

    if not user:
        return make_http_error(403, "Токен некорректный")

    user_id = user['id']
    if not dbcon.get_user_by_id(user_id):
        return make_http_error(404, "Пользователь не найден.")

    if dbcon.get_user_by_id(user_id)["role"] not in ADMIN_ROLES and doc not in dbcon.get_docs_by_user_id(user_id):
        return make_http_error(403, "Пользователь не имеет доступа к этому документу")

    if not os.path.isfile(f"{UPLOAD_DIR_DOCS}/{doc}"):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Документ не найден."}

    return FileResponse(f"{UPLOAD_DIR_DOCS}/{doc}")

