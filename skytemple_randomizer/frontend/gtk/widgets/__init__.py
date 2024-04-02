#  Copyright 2020-2024 Capypara and the SkyTemple Contributors
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.
from __future__ import annotations

# Make sure the imports are ordered in a way that they don't cause circular imports.
from skytemple_randomizer.frontend.gtk.widgets._util import (
    RandomizationSettingsWidget,
    RandomizationSettingsWindow,
)
from skytemple_randomizer.frontend.gtk.widgets.popover_help import (
    HelpPopover,
)
from skytemple_randomizer.frontend.gtk.widgets.banner_update_info import (
    UpdateInfoBanner,
)
from skytemple_randomizer.frontend.gtk.widgets.grid_links import LinksGrid
from skytemple_randomizer.frontend.gtk.widgets.base_dialog_settings import (
    BaseSettingsDialog,
    SubpageStackEntry,
)
from skytemple_randomizer.frontend.gtk.widgets.page_items import ItemsPage
from skytemple_randomizer.frontend.gtk.widgets.page_items_categories import (
    ItemsCategoriesPage,
)
from skytemple_randomizer.frontend.gtk.widgets.page_personality_quiz import (
    PersonalityQuizPage,
)
from skytemple_randomizer.frontend.gtk.widgets.page_text_pool import (
    TextPool,
    TextPoolPage,
)
from skytemple_randomizer.frontend.gtk.widgets.page_dungeons_chances import (
    DungeonsChancesPage,
)
from skytemple_randomizer.frontend.gtk.widgets.page_dungeons_settings import (
    DungeonsSettingsPage,
)
from skytemple_randomizer.frontend.gtk.widgets.page_explorer_rank import (
    ExplorerRankPage,
)
from skytemple_randomizer.frontend.gtk.widgets.page_monsters_abilities import (
    MonstersAbilitiesPage,
)
from skytemple_randomizer.frontend.gtk.widgets.page_monsters_pool import (
    MonstersPoolPage,
    MonstersPoolType,
)
from skytemple_randomizer.frontend.gtk.widgets.page_dungeons_individual_settings import (
    DungeonsIndividualSettingsPage,
)
from skytemple_randomizer.frontend.gtk.widgets.page_personality_quiz_questions import (
    PersonalityQuizQuestionsPage,
)
from skytemple_randomizer.frontend.gtk.widgets.page_movesets import MovesetsPage
from skytemple_randomizer.frontend.gtk.widgets.page_music import MusicPage
from skytemple_randomizer.frontend.gtk.widgets.page_patches import PatchesPage
from skytemple_randomizer.frontend.gtk.widgets.page_tactics_iq import TacticsIqPage
from skytemple_randomizer.frontend.gtk.widgets.page_text import TextPage
from skytemple_randomizer.frontend.gtk.widgets.page_tweaks import TweaksPage
from skytemple_randomizer.frontend.gtk.widgets.page_welcome import WelcomePage
from skytemple_randomizer.frontend.gtk.widgets.page_settings import SettingsPage
from skytemple_randomizer.frontend.gtk.widgets.dialog_randomize import RandomizeDialog
from skytemple_randomizer.frontend.gtk.widgets.page_dungeons import DungeonsPage
from skytemple_randomizer.frontend.gtk.widgets.page_monsters import MonstersPage
from skytemple_randomizer.frontend.gtk.widgets.stack_main import MainStack
from skytemple_randomizer.frontend.gtk.widgets.stack_start import StartStack
from skytemple_randomizer.frontend.gtk.widgets.window_app import AppWindow


__all__ = [
    "HelpPopover",
    "RandomizationSettingsWidget",
    "RandomizationSettingsWindow",
    "RandomizeDialog",
    "SettingsPage",
    "DungeonsPage",
    "MonstersPage",
    "TextPage",
    "TweaksPage",
    "WelcomePage",
    "AppWindow",
    "MainStack",
    "StartStack",
    "BaseSettingsDialog",
    "SubpageStackEntry",
    "DungeonsIndividualSettingsPage",
    "DungeonsChancesPage",
    "DungeonsSettingsPage",
    "MovesetsPage",
    "TacticsIqPage",
    "MonstersAbilitiesPage",
    "MonstersPoolPage",
    "MonstersPoolType",
    "PersonalityQuizPage",
    "PersonalityQuizQuestionsPage",
    "TextPool",
    "ItemsPage",
    "ItemsCategoriesPage",
    "ExplorerRankPage",
    "MusicPage",
    "PatchesPage",
    "TextPoolPage",
    "UpdateInfoBanner",
    "LinksGrid",
]
