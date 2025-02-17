"""
jupyturtle.py release 2024-03
庆祝Think Python第3版。
"""

import math
import sys
import time
from dataclasses import dataclass
from textwrap import dedent
from typing import NamedTuple

from IPython.display import display, HTML, DisplayHandle


# defaults
DRAW_WIDTH = 300
DRAW_HEIGHT = 150
DRAW_BGCOLOR = '#F3F3F7'  # "anti-flash white" (non-standard name)


DRAW_SVG = dedent(
"""
<svg width="{width}" height="{height}">
    <rect width="100%" height="100%" fill="{bgcolor}" />

{contents}

</svg>
"""
).strip()


@dataclass
class Drawing:
    width: int = DRAW_WIDTH
    height: int = DRAW_HEIGHT
    bgcolor: str = DRAW_BGCOLOR
    handle: DisplayHandle | None = None

    def get_SVG(self, contents):
        return DRAW_SVG.format(
            width=self.width,
            height=self.height,
            bgcolor=self.bgcolor,
            contents=contents,
        )


class Point(NamedTuple):
    x: float = 0
    y: float = 0

    def translated(self, dx: float, dy: float):
        return Point(self.x + dx, self.y + dy)


LINE_SVG = dedent(
"""
    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"
        stroke="{color}" stroke-width="{width}" />
"""
).strip()


class Line(NamedTuple):
    p1: Point
    p2: Point
    color: str
    width: int

    def get_SVG(self):
        (x1, y1), (x2, y2) = self.p1, self.p2
        return LINE_SVG.format(
            x1=round(x1, 1),
            y1=round(y1, 1),
            x2=round(x2, 1),
            y2=round(y2, 1),
            color=self.color,
            width=self.width,
        )


# mapping of method names to global aliases
_commands = {}


# decorators to build procedural API with turtle commands
def command(method):
    """在过程API中注册函数为顶级函数。"""
    _commands[method.__name__] = []  # no alias
    return method


def command_alias(*names):
    def decorator(method):
        _commands[method.__name__] = list(names)
        return method

    return decorator


# defaults
TURTLE_HEADING = 0.0  # pointing to screen left, a.k.a. "east"
TURTLE_COLOR = '#63A375'  # "mint" (non-standard name)
TURTLE_DELAY = 0.2  # pause after each visual command, in seconds
PEN_COLOR = '#663399'  # rebeccapurple https://www.w3.org/TR/css-color-4/#valdef-color-rebeccapurple
PEN_WIDTH = 2


TURTLE_SVG = dedent(
"""
    <g transform="rotate({heading},{x},{y}) translate({x}, {y})">
        <circle stroke="{color}" stroke-width="2" fill="transparent" r="5.5" cx="0" cy="0"/>
        <polygon points="0,12 2,9 -2,9" style="fill:{color};stroke:{color};stroke-width:2"/>
    </g>
"""
).rstrip()


class Turtle:
    def __init__(
        self, *, auto_render=True, delay: float | None = None, drawing: Drawing | None = None
    ):
        self.auto_render = auto_render
        self.delay = delay
        self.drawing = drawing if drawing else Drawing()
        self.position = Point(self.drawing.width // 2, self.drawing.height // 2)
        self.heading = TURTLE_HEADING
        self.color = TURTLE_COLOR
        self.visible = True
        self.active_pen = True
        self.pen_color = PEN_COLOR
        self.pen_width = PEN_WIDTH
        self.lines: list[Line] = []
        # TODO: issue warning if `display` did not return a handle
        self.drawing.handle = display(HTML(self.get_SVG()), display_id=True)

    @property
    def x(self) -> float:
        return self.position.x

    @property
    def y(self) -> float:
        return self.position.y

    @property
    def heading(self) -> float:
        return self.__heading

    @heading.setter
    def heading(self, new_heading) -> None:
        self.__heading = new_heading % 360.0

    @property
    def delay(self):
        return self.__delay
    
    @delay.setter
    def delay(self, s):
        if s is None:
            self.__delay = TURTLE_DELAY
            return
        if s == 0:
            self.__delay = 0
            return
        if not self.auto_render:
            print('警告: 当auto_render=False，忽略delay参数', file=sys.stderr)
        self.__delay = s

    def get_SVG(self):
        svg = []
        for line in self.lines:
            svg.append(line.get_SVG())
        if self.visible:
            svg.append(
                TURTLE_SVG.format(
                    id=f'海龟{id(self):x}',
                    x=round(self.x, 1),
                    y=round(self.y, 1),
                    heading=round(self.heading - 90, 1),
                    color=self.color,
                )
            )

        return self.drawing.get_SVG('\n'.join(svg))

    @command
    def render(self):
        # TODO: issue warning if `handle` is None
        if h := self.drawing.handle:
            if self.delay and self.auto_render:
                time.sleep(self.delay)
            h.update(HTML(self.get_SVG()))

    @command
    def hide(self):
        """隐藏海龟。如果钢笔落下，海龟的轨迹依然会保留。"""
        self.visible = False
        # every method that changes the drawing must:
        if self.auto_render:  # check if auto_render is enabled
            self.render()  # if so, update the display

    @command
    def show(self):
        """显示海龟。"""
        self.visible = True
        if self.auto_render:
            self.render()

    @command_alias('fd')
    def forward(self, units: float):
        """将海龟向前移动`units`距离。如果钢笔落下，将保留轨迹。"""
        angle = math.radians(self.heading)
        dx = units * math.cos(angle)
        dy = units * math.sin(angle)
        new_pos = self.position.translated(dx, dy)
        if self.active_pen:
            self.lines.append(
                Line(
                    p1=self.position,
                    p2=new_pos,
                    color=self.pen_color,
                    width=self.pen_width,
                )
            )
        self.position = new_pos
        if self.auto_render:
            self.render()

    @command_alias('bk')
    def back(self, units: float):
        """将海龟向后移动`units`距离。如果钢笔落下，将保留轨迹。"""
        self.forward(-units)

    @command
    def jumpto(self, x: float, y: float):
        """将海龟传送到坐标(x, y)，不进行绘制。"""
        self.position = Point(x, y)
        if self.auto_render:
            self.render()

    @command
    def moveto(self, x: float, y: float):
        """将海龟移动到坐标(x, y)，如果钢笔落下，将保留轨迹。"""
        new_pos = Point(x, y)
        if self.active_pen:
            self.lines.append(
                Line(
                    p1=self.position,
                    p2=new_pos,
                    color=self.pen_color,
                    width=self.pen_width,
                )
            )
        self.position = new_pos
        if self.auto_render:
            self.render()

    @command_alias('lt')
    def left(self, degrees: float):
        """将海龟向左旋转`degrees`度。"""
        self.heading -= degrees
        if self.auto_render:
            self.render()

    @command_alias('rt')
    def right(self, degrees: float):
        """将海龟向右旋转`degrees`度。"""
        self.heading += degrees
        if self.auto_render:
            self.render()

    @command
    def penup(self):
        """抬起钢笔，让海龟停止绘制。"""
        self.active_pen = False

    @command
    def pendown(self):
        """落下钢笔，让海龟开始绘制。"""
        self.active_pen = True

    def __enter__(self):
        self.saved_auto_render = self.auto_render
        self.auto_render = False
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.auto_render = self.saved_auto_render
        if self.auto_render:
            self.render()


################################################## procedural API

# _install_command() will append more names when the module loads
__all__ = ['Turtle', 'make_turtle', 'get_turtle']


def __dir__():
    return sorted(__all__)


_main_turtle = None


def make_turtle(
    *, auto_render=True, delay=None, width=DRAW_WIDTH, height=DRAW_HEIGHT
) -> None:
    """创建新海龟，设置_main_turtle。"""
    global _main_turtle
    drawing = Drawing(width=width, height=height)
    _main_turtle = Turtle(auto_render=auto_render, delay=delay, drawing=drawing)
    return _main_turtle


def get_turtle() -> Turtle:
    """获取现有的_main_turtle; 如有需要，创建一只。"""
    global _main_turtle
    if _main_turtle is None:
        _main_turtle = Turtle()
    return _main_turtle


def _make_command(name):
    method = getattr(Turtle, name)  # get unbound method

    def command(*args):
        turtle = get_turtle()
        method(turtle, *args)

    command.__name__ = name
    command.__doc__ = method.__doc__
    return command


def _install_command(name, function):
    if name in globals():
        raise ValueError(f'重复的海龟命令: {name}')
    globals()[name] = function
    __all__.append(name)


def _install_commands():
    for name, aliases in _commands.items():
        new_command = _make_command(name)
        _install_command(name, new_command)
        for alias in aliases:
            _install_command(alias, new_command)


_install_commands()
