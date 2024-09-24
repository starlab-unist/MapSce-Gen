
class TestingException(Exception):
    pass


class ExceptionSimulation(TestingException):
    pass


class RunAgain(ExceptionSimulation):
    pass


class TryNextSeed(ExceptionSimulation):
    pass


class Exit(ExceptionSimulation):
    pass


class RoutingFailure(ExceptionSimulation):
    pass
