from pandas import DataFrame, Series
from typing import List


def validate_columns(df: DataFrame, expected: List[str]) -> bool:
    actual = df.columns.to_list()

    if len(actual) != len(expected):
        return False

    for i in range(len(expected)):
        if expected[i] != actual[i]:
            return False
    
    return True


def column_is_constant(column: Series) -> bool:
    """
    Ensure that the values in a column are all the same. 
    """
    c = column.to_numpy()
    return (c[0] == c).all()


def column_is_integer(column: Series) -> bool:
    return (column % 1 == 0).all()


def column_has_at_most_two_decimal_places(column: Series) -> bool:
    return column.apply(lambda x: round(x, 2) == x).all()