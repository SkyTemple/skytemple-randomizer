"""Inserts commands into the script coroutine EVENT_DIVIDE to unlock all selected dungeons."""
#  Copyright 2020-2021 Parakoopa and the SkyTemple Contributors
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
from explorerscript.source_map import SourceMap
from explorerscript.ssb_converting.compiler.label_finalizer import LabelFinalizer
from explorerscript.ssb_converting.compiler.label_jump_to_remover import OpsLabelJumpToRemover
from explorerscript.ssb_converting.compiler.utils import strip_last_label, Counter
from explorerscript.ssb_converting.decompiler.label_jump_to_resolver import OpsLabelJumpToResolver
from explorerscript.ssb_converting.ssb_data_types import SsbOpParamConstString
from explorerscript.ssb_converting.ssb_special_ops import SsbLabel, SsbLabelJump
from skytemple_files.common.types.file_types import FileType
from skytemple_files.script.ssb.model import Ssb, SkyTempleSsbOperation
from skytemple_files.script.ssb.script_compiler import ScriptCompiler
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.status import Status


class DungeonUnlocker(AbstractRandomizer):
    def step_count(self) -> int:
        return 1

    def run(self, status: Status):
        status.step('Unlocking dungeons...')

        new_ops = []
        coro_id = self.static_data.script_data.common_routine_info__by_name['EVENT_DIVIDE'].id
        ops = self.static_data.script_data.op_codes__by_name

        # DECOMPILE
        ssb: Ssb = FileType.SSB.deserialize(
            self.rom.getFileByName('SCRIPT/COMMON/unionall.ssb'), static_data=self.static_data
        )
        routine_ops = list(OpsLabelJumpToResolver(ssb.get_filled_routine_ops()))

        # CREATE NEW OPS
        off = Counter()
        off.count = -10000
        for dungeon_id, dungeon in self.config['dungeons']['settings'].items():
            if dungeon['unlock']:
                if len(new_ops) < 1:
                    new_ops.append(SkyTempleSsbOperation(
                        off(), ops['debug_Print'][0], [SsbOpParamConstString('SkyTemple Randomizer: Dungeon Unlock...')]
                    ))
                label_closed = SsbLabel(9000 + dungeon_id, coro_id)
                label_request = SsbLabel(9200 + dungeon_id, coro_id)
                label_else = SsbLabel(9400 + dungeon_id, coro_id)
                new_ops.append(SkyTempleSsbOperation(
                    off(), ops['SwitchDungeonMode'][0], [dungeon_id]
                ))
                new_ops.append(SsbLabelJump(SkyTempleSsbOperation(
                    off(), ops['Case'][0], [0]
                ), label_closed))
                new_ops.append(SsbLabelJump(SkyTempleSsbOperation(
                    off(), ops['Case'][0], [2]
                ), label_request))
                new_ops.append(SsbLabelJump(SkyTempleSsbOperation(
                    off(), ops['Jump'][0], []
                ), label_else))
                new_ops.append(label_closed)
                new_ops.append(SkyTempleSsbOperation(
                    off(), ops['flag_SetDungeonMode'][0], [dungeon_id, 1]
                ))
                new_ops.append(SsbLabelJump(SkyTempleSsbOperation(
                    off(), ops['Jump'][0], []
                ), label_else))
                new_ops.append(label_request)
                new_ops.append(SkyTempleSsbOperation(
                    off(), ops['flag_SetDungeonMode'][0], [dungeon_id, 3]
                ))
                new_ops.append(label_else)

        routine_ops[coro_id] = new_ops + routine_ops[coro_id]
        # COMPILE
        label_finalizer = LabelFinalizer(strip_last_label(routine_ops))
        routine_ops = OpsLabelJumpToRemover(routine_ops, label_finalizer.label_offsets).routines
        new_ssb, _ = ScriptCompiler(self.static_data).compile_structured(
            [b for a, b in ssb.routine_info],
            routine_ops,
            [x.name for x in self.static_data.script_data.common_routine_info__by_id],
            SourceMap.create_empty()
        )

        self.rom.setFileByName('SCRIPT/COMMON/unionall.ssb', FileType.SSB.serialize(
            new_ssb, static_data=self.static_data
        ))

        status.done()
