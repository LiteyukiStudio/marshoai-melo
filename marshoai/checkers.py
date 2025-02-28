from melobot.protocols.onebot.v11.adapter.event import Event, MessageEvent, PokeNotifyEvent
from melobot.protocols.onebot.v11.utils import MsgChecker, LevelRole, MsgCheckerFactory
from melobot.protocols.onebot.v11.adapter.segment import PokeRecvSegment

from melobot.utils.parse import CmdArgs
from melobot.utils.match import StartMatcher
from melobot.utils.check import Checker

from .config import Config
from .extra_segment import TouchSegment
config = Config()

superuser_checker_ft = MsgCheckerFactory(
    owner= config.owner,
    super_users=config.superusers
)
superuser_checker: MsgChecker = superuser_checker_ft.get_base(LevelRole.SU) # 超级用户检查器

class PokeMarshoChecker(Checker):
    """
    戳一戳 Bot 检查器，戳一戳对象为 Bot 自身时检查通过
    """
    def __init__(self) -> None:
        super().__init__()
    async def check(self, event: PokeNotifyEvent) -> bool:
        try:
            if event.target_id == event.self_id:
                return True
            else:
                return False
        except AttributeError:
            return False