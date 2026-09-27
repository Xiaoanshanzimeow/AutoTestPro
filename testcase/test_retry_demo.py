"""演示用例：展示 pytest-rerunfailures 的失败重试机制。

刻意让用例第一次执行失败（counter 从 0 增到 1，不满足 >1），
依赖 pytest.ini 里的 --reruns 2 重试后，第二次（counter=2）才通过。

这不是业务用例，仅用于说明「失败自动重试」的配置效果，
故在模块级标记 skip，不参与正常回归统计。
"""
import pytest

pytestmark = pytest.mark.skip(reason="演示用例：仅展示 --reruns 失败重试机制，非业务测试")

counter = {"n": 0}


def test_flaky_demo():
    counter["n"] += 1
    assert counter["n"] > 1
