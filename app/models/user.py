# Helper for ObjectId
from bson import ObjectId
from pydantic import BaseModel
from pydantic import EmailStr, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        # This replaces __modify_schema__ in Pydantic v2
        return {"type": "string"}


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    hashed_password: str
    is_active: bool = True

    class Config:
        validate_assignment = True
        json_encoders = {ObjectId: str, "datetime": lambda dt: dt.isoformat()}
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "hashed_password": "hashedpassword123",
                "is_active": True
            }
        }
