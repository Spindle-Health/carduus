from typing import Any, Callable, Iterable
import jellyfish as j

from pyspark.sql import Column
from pyspark.sql.functions import (
    lit,
    when,
    length,
    substring,
    upper,
    regexp_replace,
    trim,
    udf,
)
from pyspark.sql.types import StringType


def remap(mapping: dict[Any, Any], col: Column, default: Any | None = None) -> Column:
    result = None
    for k, v in mapping.items():
        if result is None:
            result = when(col == lit(k), lit(v))
        else:
            result = result.when(col == lit(k), lit(v))
    if default is not None and result is not None:
        result = result.otherwise(default)
    return col if result is None else result


def null_if(pred: Callable[[Column], Column], col: Column) -> Column:
    return when(~pred(col), col).otherwise(lit(None))


def first_char(col: Column) -> Column:
    return substring(col, 1, 1)


def _metaphone_udf_impl(s: str | None) -> str | None:
    return j.metaphone(s) if s else None


metaphone = udf(_metaphone_udf_impl, returnType=StringType(), useArrow=False)


def normalize_text(raw: Column) -> Column:
    return null_if(lambda c: length(c) == 0, trim(regexp_replace(upper(raw), "\\s+", " ")))
