from typing import List, Optional

from ..models import Role


async def role_check(
    role: Role,
    available_roles: List[Role],
    message: Optional[str] = "you don't have access",
) -> Optional[str]:
    if role not in available_roles:
        return message
