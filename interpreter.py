from parser import World, Production, FunctionDefinition


class Interpreter:
    def __init__(self, world: World, script: list[Production]) -> None:
        self._world = world
        self._script = script

    def interpret(self):
        for node in self._script:
            if not isinstance(node, FunctionDefinition):
                # function definitions will be interpreted via function calls
                result = node.interpret(self._world)
        return result
