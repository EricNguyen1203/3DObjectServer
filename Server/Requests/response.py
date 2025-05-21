from fastapi.responses import JSONResponse


class BaseReponse(JSONResponse):
    def __init__(self, result: bool, message: str, data: list, status_code: int):
        content = {
            "result": result,
            "message": message,
            "data": data
        }
        super().__init__(content=content, status_code=status_code)