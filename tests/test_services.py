import pytest

from src.dataworkers.services import convert_value


@pytest.mark.asyncio
async def test_convert_value_correct():
    value1 = '4'
    value2 = 'Fail'
    res1 = convert_value(value1)
    res2 = convert_value(value2)
    assert res1 == 4.0
    assert res2 == 'Fail'
