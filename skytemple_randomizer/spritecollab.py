"""Global instance of the SpriteCollab client."""
from typing import Optional

from skytemple_files.common.spritecollab.client import SpriteCollabClient


_INSTANCE: Optional[SpriteCollabClient] = None


def sprite_collab() -> SpriteCollabClient:
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = SpriteCollabClient()
    return _INSTANCE
