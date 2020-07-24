from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from omi_async_http_client._model import RequestModel
from test.mock.mock_async_http_client import APIClient

app = FastAPI()


# ==============================Demo for AsyncHTTPClient=================================

class Resource(BaseModel):
    name: str = None
    description: str = None


class ResourceID(Resource):
    id: str = None


@RequestModel(api_name="/resources", api_prefix="/database", api_suffix="")
class APIResource(BaseModel):
    name: str = None
    description: str = None


@RequestModel(api_name="/resources/{id}", api_prefix="/database", api_suffix="")
class APIResourceID(Resource):
    id: str = None


resources = [
    {"id": "1", "name": "alpha", "description": "alpha is A"},
    {"id": "2", "name": "bravo", "description": "bravo is B"},
    {"id": "3", "name": "charlie", "description": "charlie is C"},
    {"id": "4", "name": "delta", "description": "delta is D"},
    {"id": "5", "name": "echo", "description": "echo is E"}
]


@app.get("/mock/resources/all")
def resources_get_all():
    return JSONResponse(
        status_code=200,
        content={
            "code": 100,
            "message": "success",
            "detail": resources
        })


@app.get("/mock/resources")
def resources_get(name: Optional[str]):
    resp = []
    for item in resources:
        if item["name"].find(name) > -1:
            resp.append(item)
    if len(resp) > 0:
        return JSONResponse(
            status_code=200,
            content={
                "code": 100,
                "message": "success",
                "detail": resp
            })
    else:
        return JSONResponse(
            status_code=404,
            content={
                "code": 101,
                "message": "not found",
                "detail": {}
            })


@app.get("/mock/resources/{id}")
def resources_get_by_id(id: str):
    for item in resources:
        if item["id"] == id:
            return JSONResponse(
                status_code=200,
                content=item
            )
            # return JSONResponse({
            #     "code":200,
            #     "message":"success",
            #     "detail":item
            # })
    return JSONResponse(
        status_code=404,
        content={
            "code": 101,
            "message": "not found",
            "detail": {}
        })


@app.put("/mock/resources/{id}")
def resources_put(id: str, resource: Resource):
    for item in resources:
        if item["id"] == id:
            item["name"] = resource.name
            item["description"] = resource.description
            return JSONResponse(
                status_code=200,
                content={
                    "code": 100,
                    "message": "success",
                    "detail": item
                })
    return JSONResponse(
        status_code=404,
        content={
            "code": 101,
            "message": "not found",
            "detail": {}
        })


@app.post("/mock/resources")
def resources_post(resource: ResourceID):
    resources.append(resource.dict())
    return JSONResponse(
        status_code=201,
        content={
            "code": 100,
            "message": "created",
            "detail": {}
        })


@app.delete("/mock/resources/{id}")
def resources_delete(id: str):
    for item in resources:
        if item["id"] == id:
            resources.remove(item)
            return JSONResponse(
                status_code=200,
                content={
                    "code": 100,
                    "message": "success",
                    "detail": {}
                })
    return JSONResponse(
        status_code=404,
        content={
            "code": 102,
            "message": "not found",
            "detail": {}
        })


# ===============================================================

# =============================for integration test==================================

@app.get("/mock/rpc/resources/{id}")
async def resources_get_form_rpc(id: str):
    client = APIClient(APIResourceID)
    resp = await client.retrieve(
        opt_id={"id": id}
    )
    return JSONResponse(
        status_code=404,
        content={
            "code": 102,
            "message": "not found",
            "detail": resp.dict()
        })


@app.get("/mock/database/resources/{id}")
def resources_database(id: str):
    for item in resources:
        if item["id"] == id:
            return JSONResponse(
                status_code=200,
                content=item
            )
            # return JSONResponse({
            #     "code":200,
            #     "message":"success",
            #     "detail":item
            # })
    return JSONResponse(
        status_code=404,
        content={
            "code": 101,
            "message": "not found",
            "detail": {}
        })


# ===============================================================

@app.on_event("startup")
async def startup_event():
    pass


@app.on_event("shutdown")
async def shutdown_event():
    pass


if __name__ == '__main__':
    uvicorn.run(app='mock_fastapi:app', host="0.0.0.0",
                port=8003, reload=True, debug=True)
