"""An analyzer for the syntax tree"""

from parser import World, Production


class Analyzer:
    def __init__(self, world: World, script: list[Production]) -> None:
        self._world = world
        self._script = script

    def analyze(self):
        for node in self._script:
            node.analyze(self._world)
