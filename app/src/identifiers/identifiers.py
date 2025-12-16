from pandas import DataFrame
from typing import List


def by_columns(df: DataFrame, expected: List[str]) -> bool:
    actual = df.columns.to_list()

    if len(actual) != len(expected):
        return False

    for i in range(len(expected)):
        if expected[i] != actual[i]:
            return False

    return True
