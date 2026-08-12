from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator, model_validator


# ── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── User ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role_id: int = 2  # default to USER role

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("username cannot be blank")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role_id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Role ─────────────────────────────────────────────────────────────────────

class RoleResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


# ── Task ─────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assigned_to: int | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title cannot be blank")
        return v


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    assigned_to: int | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "TaskUpdate":
        if all(v is None for v in self.model_dump().values()):
            raise ValueError("at least one field must be provided")
        return self


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    assigned_to: int | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


# ── Document ──────────────────────────────────────────────────────────────────

class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int | None
    uploaded_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Search ────────────────────────────────────────────────────────────────────

class SearchResult(BaseModel):
    document_id: int
    original_filename: str
    score: float
    chunk_text: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
