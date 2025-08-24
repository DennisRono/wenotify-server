from fastapi import APIRouter

test_router = APIRouter()


@test_router.get("/")
def get_test_endp():
    return {"message": "Test Endpoint is working!"}
