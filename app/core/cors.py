from dataclasses import dataclass, field


@dataclass
class CORSSettings:
    allow_methods: list[str]
    allow_headers: list[str]
    allow_origins: list[str] = field(default_factory=list)
    allow_credentials: bool = True


default_cors = CORSSettings(
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Accept-Language",
        "Origin",
        "User-Agent",
        "X-Requested-With",
        "X-Auth-Token",
        "X-CSRF-Token",
        "Accept-Language",
    ],
)
