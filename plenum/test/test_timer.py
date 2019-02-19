import pytest

from plenum.common.timer import Timer
from plenum.test.helper import MockTimestamp


class Callback:
    def __init__(self):
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        self.call_count += 1


def test_timer_can_schedule_callback():
    ts = MockTimestamp(0)
    timer = Timer(ts)
    cb = Callback()

    timer.schedule(5, cb)
    assert cb.call_count == 0

    timer.service()
    assert cb.call_count == 0

    ts.value += 3
    timer.service()
    assert cb.call_count == 0

    ts.value += 3
    timer.service()
    assert cb.call_count == 1

    timer.service()
    assert cb.call_count == 1

    ts.value += 6
    timer.service()
    assert cb.call_count == 1


def test_timer_can_schedule_callback_after_first_call():
    ts = MockTimestamp(0)
    timer = Timer(ts)
    cb = Callback()

    timer.schedule(5, cb)
    ts.value += 6
    timer.service()
    assert cb.call_count == 1

    timer.schedule(5, cb)
    ts.value += 6
    timer.service()
    assert cb.call_count == 2


def test_timer_can_schedule_callback_twice():
    ts = MockTimestamp(0)
    timer = Timer(ts)
    cb = Callback()

    timer.schedule(3, cb)
    timer.schedule(5, cb)

    ts.value += 4
    timer.service()
    assert cb.call_count == 1

    ts.value += 4
    timer.service()
    assert cb.call_count == 2


def test_timer_can_schedule_and_process_callback_twice():
    ts = MockTimestamp(0)
    timer = Timer(ts)
    cb = Callback()

    timer.schedule(3, cb)
    timer.schedule(5, cb)

    ts.value += 6
    timer.service()
    assert cb.call_count == 2


def test_timer_can_schedule_same_callback_on_same_time_twice():
    ts = MockTimestamp(0)
    timer = Timer(ts)
    cb = Callback()

    timer.schedule(5, cb)
    timer.schedule(5, cb)

    ts.value += 6
    timer.service()
    assert cb.call_count == 2


def test_timer_can_schedule_different_callbacks_on_same_time_twice():
    ts = MockTimestamp(0)
    timer = Timer(ts)
    cb1 = Callback()
    cb2 = Callback()

    timer.schedule(5, cb1)
    timer.schedule(5, cb2)

    ts.value += 6
    timer.service()
    assert cb1.call_count == 1
    assert cb2.call_count == 1


def test_timer_can_schedule_different_callbacks():
    ts = MockTimestamp(0)
    timer = Timer(ts)
    cb1 = Callback()
    cb2 = Callback()

    timer.schedule(5, cb1)
    timer.schedule(3, cb2)

    ts.value += 4
    timer.service()
    assert cb1.call_count == 0
    assert cb2.call_count == 1

    ts.value += 4
    timer.service()
    assert cb1.call_count == 1
    assert cb2.call_count == 1


def test_timer_can_schedule_and_simultaneously_process_different_callbacks():
    ts = MockTimestamp(0)
    timer = Timer(ts)
    cb1 = Callback()
    cb2 = Callback()

    timer.schedule(5, cb1)
    timer.schedule(3, cb2)

    ts.value += 6
    timer.service()
    assert cb1.call_count == 1
    assert cb2.call_count == 1


@pytest.mark.parametrize('cancel_all', [False, True])
def test_timer_can_cancel_callback(cancel_all):
    ts = MockTimestamp(0)
    timer = Timer(ts)
    cb = Callback()

    timer.schedule(5, cb)

    ts.value += 3
    timer.service()
    assert cb.call_count == 0

    timer.cancel(cb, cancel_all=cancel_all)

    ts.value += 3
    timer.service()
    assert cb.call_count == 0


@pytest.mark.parametrize('cancel_all', [False, True])
def test_timer_cancel_callback_doesnt_crash_for_nonexistant_callback(cancel_all):
    ts = MockTimestamp(0)
    timer = Timer(ts)
    cb = Callback()

    # This shouldn't crash
    timer.cancel(cb, cancel_all=cancel_all)

    # Make sure that callback which was scheduled later is still called
    timer.schedule(5, cb)
    ts.value += 6
    timer.service()
    assert cb.call_count == 1

    # And this still shouldn't crash
    timer.cancel(cb, cancel_all=cancel_all)


@pytest.mark.parametrize('cancel_all', [False, True])
def test_timer_can_cancel_callback_without_touching_other_callbacks(cancel_all):
    ts = MockTimestamp(0)
    timer = Timer(ts)
    cb1 = Callback()
    cb2 = Callback()
    cb3 = Callback()

    timer.schedule(5, cb1)
    timer.schedule(3, cb2)
    timer.schedule(4, cb3)
    timer.cancel(cb2, cancel_all=cancel_all)

    ts.value += 6
    timer.service()
    assert cb1.call_count == 1
    assert cb2.call_count == 0
    assert cb3.call_count == 1


def test_timer_cancels_only_one_instance_of_callback():
    ts = MockTimestamp(0)
    timer = Timer(ts)
    cb = Callback()

    timer.schedule(5, cb)
    timer.schedule(3, cb)
    timer.cancel(cb)

    ts.value += 6
    timer.service()
    assert cb.call_count == 1


def test_timer_can_cancel_all_instances_of_callback():
    ts = MockTimestamp(0)
    timer = Timer(ts)
    cb = Callback()

    timer.schedule(5, cb)
    timer.schedule(3, cb)
    timer.cancel(cb, cancel_all=True)

    ts.value += 6
    timer.service()
    assert cb.call_count == 0
