from llama.trader import Trader


def test_init():
    tony = Trader()
    assert not tony.is_immutable()
