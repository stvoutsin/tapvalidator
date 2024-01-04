import dramatiq
from dramatiq.results import Results
from dramatiq.results.backends import StubBackend


def test_actors_can_be_defined(stub_broker):
    # Test that actors can be created
    @dramatiq.actor
    def add(x, y):
        return x + y

    assert isinstance(add, dramatiq.Actor)


def test_messages_can_get_results_from_inferred_backend(
    stub_broker, stub_worker, result_backend
):
    # Given a result backend
    # And a broker with the results middleware
    stub_broker.add_middleware(Results(backend=StubBackend()))

    # And an actor that stores a result
    @dramatiq.actor(store_results=True)
    def do_work():
        return 42

    # When I send that actor a message
    message = do_work.send()

    # And wait for a result
    # Then I should get that result back
    assert message.get_result(block=True) == 42
