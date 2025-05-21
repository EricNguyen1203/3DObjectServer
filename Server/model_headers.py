from packages.pydantic import BaseModel


class ModelHeaders(BaseModel):
    param_query_type: int # 0-id 1-name