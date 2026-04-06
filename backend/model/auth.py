from pydantic import BaseModel


class TokenData(BaseModel):
    user_name: str
    user_id: str

    @classmethod
    def from_user(cls, username: str, user_id) -> "TokenData":
        return cls(user_name=username, user_id=str(user_id))
