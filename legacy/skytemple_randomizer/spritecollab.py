"""Global instance of the SpriteCollab client."""
from typing import Optional, List, Sequence, Dict, Mapping, Tuple

from skytemple_files.common.ppmdu_config.data import Pmd2Sprite
from skytemple_files.common.spritecollab.client import SpriteCollabClient, SpriteCollabSession, MonsterFormDetails
from skytemple_files.common.spritecollab.schema import Credit
from skytemple_files.graphics.chara_wan.model import WanFile
from skytemple_files.graphics.kao import SUBENTRIES
from skytemple_files.graphics.kao.protocol import KaoImageProtocol

_INSTANCE: Optional[SpriteCollabClient] = None
# A dict of credits for all portraits requested (and found) during the randomization
# Key is full form name
_COLLECTED_PORTRAITS: Dict[Tuple[str, str], List[Credit]] = {}
# A list of all sprites requested (and found) during the randomization
# Key is full form name
_COLLECTED_SPRITES: Dict[Tuple[str, str], List[Credit]] = {}


def sprite_collab() -> SpriteCollabClient:
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = SpriteCollabClient(cache_size=5_000)
    return _INSTANCE


async def get_details_and_portraits(
        session: SpriteCollabSession,
        forms_to_try: Sequence[Tuple[int, str]]
) -> Optional[Tuple[MonsterFormDetails, List[Optional[KaoImageProtocol]]]]:
    """
    Fetches portraits and details given the given list of form priorities,
    updates the credits list.

    The portraits are mashed together using the priority list, filling empty slots
    with lower priority forms. However, the returned form details are from the most
    prioritized form available.
    """
    #   - filter by all valid forms
    valid_forms_to_try = await _filter_valid_forms(session, forms_to_try)
    if len(valid_forms_to_try) < 1:
        return None
    #   - Fetch all portraits of all given forms to try
    fetched_portraits = await session.fetch_portraits(valid_forms_to_try)
    final_portraits: List[Optional[KaoImageProtocol]] = [None] * SUBENTRIES
    involved_forms = set()
    #   - Merge them together
    #     - Prioritize early entries, fill with later entries
    for fi, single_set in enumerate(fetched_portraits):
        for i, set_slot in enumerate(single_set):
            if set_slot is not None and final_portraits[i] is None:
                final_portraits[i] = set_slot
                involved_forms.add(valid_forms_to_try[fi])
    if len(involved_forms) < 1:
        return None
    #   - Fetch details of all involved forms
    details = await session.monster_form_details([x for x in valid_forms_to_try if x in involved_forms])
    #   - update credits
    for detail in details:
        _COLLECTED_PORTRAITS[(detail.full_form_name, f'{detail.monster_id:04}')] = list(detail.portrait_credits)
    return details[0], final_portraits


async def get_sprites(
        session: SpriteCollabSession,
        forms_to_try: Sequence[Tuple[int, str]]
) -> Optional[Tuple[WanFile, Pmd2Sprite, int]]:
    """
    Fetches sprites given the given list of form priorities, updates the credits list.

    Sprites are not merged (unlike portraits), all available sprites from the first
    available form that has any sprites are used.
    """
    #   - filter by all valid forms
    valid_forms_to_try = await _filter_valid_forms(session, forms_to_try)
    if len(valid_forms_to_try) < 1:
        return None
    #   - Fetch all sprites of all given forms to try
    for form_path, form in zip(valid_forms_to_try, await session.fetch_sprites(
            valid_forms_to_try,
            [None] * len(valid_forms_to_try),
            copy_to_event_sleep_if_missing=True
    )):
        if form is not None:
            #   - Fetch details of used form
            details = await session.monster_form_details([form_path])
            #   - update credits
            for detail in details:
                _COLLECTED_SPRITES[(detail.full_form_name, f'{detail.monster_id:04}')] = list(detail.sprite_credits)
            return form
    return None


def portrait_credits() -> Mapping[Tuple[str, str], Sequence[Credit]]:
    """Returns all portrait credits, sorted by key. Key is full form name, with monster name."""
    return dict(_COLLECTED_PORTRAITS)


def sprite_credits() -> Mapping[Tuple[str, str], Sequence[Credit]]:
    """Returns all sprite credits, sorted by key. Key is full form name, with monster name."""
    return dict(_COLLECTED_SPRITES)


async def _filter_valid_forms(
        session: SpriteCollabSession,
        forms_to_try: Sequence[Tuple[int, str]]
) -> Sequence[Tuple[int, str]]:
    """Returns all forms in forms_to_try for which a form exists at the server."""
    all_forms = [(x.monster_id, x.form_path) for x in await session.list_monster_forms(False)]
    valid_forms = []

    for monster_id, form_path in forms_to_try:
        if any(x == (monster_id, form_path) for x in all_forms):
            valid_forms.append((monster_id, form_path))
            break

    return valid_forms
