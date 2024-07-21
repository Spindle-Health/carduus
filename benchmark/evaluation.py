from dataclasses import dataclass
from functools import reduce
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, struct


@dataclass
class Metrics:
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int

    @property
    def precision(self):
        return self.true_positives / (self.true_positives + self.false_positives)

    @property
    def recall(self):
        return self.true_positives / (self.true_positives + self.false_negatives)

    @property
    def f_score(self):
        return (2.0 * self.precision * self.recall) / (self.precision + self.recall)

    @property
    def false_discovery_rate(self):
        return self.false_positives / (self.true_positives + self.false_positives)

    @property
    def accuracy(self):
        return (self.true_positives + self.true_negatives) / (
            self.true_positives
            + self.true_negatives
            + self.false_positives
            + self.false_negatives
        )


def evaluate(
    data: DataFrame,
    ground_truth_key: list[str],
    tokens: list[str],
) -> Metrics:
    data = data.select(
        struct(*[col(c) for c in ground_truth_key]).alias("key"),
        struct(*[col(c) for c in tokens]).alias("tokens"),
    )
    matches = (
        data.withColumnRenamed("key", "l_key")
        .alias("l")
        .join(data.withColumnRenamed("key", "r_key").alias("r"), ["tokens"])
        .groupBy((col("l_key") == col("r_key")).alias("tp"))
        .count()
        .orderBy(col("tp"))
        .collect()
    )
    false_positives = matches[0]["count"]
    true_positives = matches[1]["count"]
    false_negatives = (
        data.withColumnRenamed("key", "l_key")
        .alias("l")
        .join(
            data.withColumnRenamed("key", "r_key").alias("r"),
            (col("l_key") == col("r_key"))
            & reduce(
                lambda acc, token: acc | (col("l.tokens." + token) != col("r.tokens." + token)),
                tokens,
                lit(False),
            ),
        )
        .count()
    )
    true_negatives = (data.count() ** 2) - (false_negatives + true_positives + false_positives)
    return Metrics(true_positives, false_positives, true_negatives, false_negatives)
