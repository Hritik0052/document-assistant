from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterSchema(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    password_confirm: str = Field(min_length=8, max_length=128)

    @field_validator('username')
    @classmethod
    def username_strip(cls, value: str) -> str:
        cleaned = value.strip()
        if ' ' in cleaned:
            raise ValueError('Username cannot contain spaces.')
        return cleaned

    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, value: str, info) -> str:
        password = info.data.get('password')
        if password and value != password:
            raise ValueError('Passwords do not match.')
        return value


class LoginSchema(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
