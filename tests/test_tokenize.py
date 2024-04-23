from pyspark.sql import Column, SparkSession, Row
from pyspark.sql.types import DataType, StructType, StructField, LongType, StringType
from pyspark.sql.functions import regexp_replace, substring
from pyspark.testing.utils import assertDataFrameEqual, assertSchemaEqual
from carduus.keys import InMemoryKeyService
from carduus.token import (
    OpprlPii,
    OpprlToken,
    TokenInfo,
    tokenize,
    transcrypt_out,
    transcrypt_in,
)
from carduus.token.pii import PiiTransform


def test_tokenize_and_transcrypt_opprl(
    spark: SparkSession, organization_b_key_service: InMemoryKeyService
):
    tokens = tokenize(
        (
            spark.createDataFrame(
                [
                    Row(
                        id=1,
                        first_name="Louis",
                        last_name="Pasteur",
                        gender="male",
                        birth_date="1822-12-27",
                    ),
                    Row(
                        id=2,
                        first_name="louis",
                        last_name="pasteur",
                        gender="M",
                        birth_date="1822-12-27",
                    ),
                ]
            )
        ),
        pii_transforms={
            "first_name": OpprlPii.first_name,
            "last_name": OpprlPii.last_name,
            "gender": OpprlPii.gender,
            "birth_date": OpprlPii.birth_date,
        },
        tokens=[OpprlToken.token1, OpprlToken.token2],
    )
    assertDataFrameEqual(
        tokens,
        (
            spark.createDataFrame(
                [
                    Row(
                        id=1,
                        opprl_token_1="Ly3w2PppIjtu2LC03FXWTUYrb3WWiiFoETjxnbhrOXb8oCmUrxbs69QfqVdPafqMdRVozMoNt+m7\r\nAvJYG/LLytaArWrW36LOoEINLuNd0mE=",
                        opprl_token_2="wN002PsjouMwmEQTbqOlwxlNrMU9gTjlYoX3kLTokrgNOnwaY9KuHZKnAwnBomGnJd3IaliZF8lE\r\nJwGgzhDScAnK9YlL0bE3vsJTlLseIkY=",
                    ),
                    Row(
                        id=2,
                        opprl_token_1="Ly3w2PppIjtu2LC03FXWTUYrb3WWiiFoETjxnbhrOXb8oCmUrxbs69QfqVdPafqMdRVozMoNt+m7\r\nAvJYG/LLytaArWrW36LOoEINLuNd0mE=",
                        opprl_token_2="wN002PsjouMwmEQTbqOlwxlNrMU9gTjlYoX3kLTokrgNOnwaY9KuHZKnAwnBomGnJd3IaliZF8lE\r\nJwGgzhDScAnK9YlL0bE3vsJTlLseIkY=",
                    ),
                ]
            )
        ),
    )
    sent_tokens = transcrypt_out(
        tokens, token_columns=["opprl_token_1", "opprl_token_2"], destination="OrganizationB"
    )
    assertSchemaEqual(
        sent_tokens.schema,
        StructType(
            [
                StructField("id", LongType()),
                StructField("opprl_token_1", StringType()),
                StructField("opprl_token_2", StringType()),
            ]
        ),
    )
    # When transfering between organizations, tokens from the same PII should _not_ be equal.
    assert sent_tokens.distinct().count() == 2

    assertDataFrameEqual(
        transcrypt_in(
            sent_tokens,
            token_columns=["opprl_token_1", "opprl_token_2"],
            key_service=organization_b_key_service,
        ),
        (
            spark.createDataFrame(
                [
                    Row(
                        id=1,
                        opprl_token_1="/abo0bFAIS934MJQ7TXdKVhj1SuFUbVOt6JbuQNismBm9+btDWVSuAGFcDqVwiJviKxe5WBIJwvj\r\nbyWb1qaE6b1CjbdFmTicpYuyDbkIo+8=",
                        opprl_token_2="UEI5gcYVk1bn4cGHOl6lVOu8N/VTVKyNlL+MwKRuwqGih28RWg4xBMoTPWEpjY4JqEpE5ftLnEAV\r\nG/r0GiRJgrfzbqa8i2ulVo79X5bUqnY=",
                    ),
                    Row(
                        id=2,
                        opprl_token_1="/abo0bFAIS934MJQ7TXdKVhj1SuFUbVOt6JbuQNismBm9+btDWVSuAGFcDqVwiJviKxe5WBIJwvj\r\nbyWb1qaE6b1CjbdFmTicpYuyDbkIo+8=",
                        opprl_token_2="UEI5gcYVk1bn4cGHOl6lVOu8N/VTVKyNlL+MwKRuwqGih28RWg4xBMoTPWEpjY4JqEpE5ftLnEAV\r\nG/r0GiRJgrfzbqa8i2ulVo79X5bUqnY=",
                    ),
                ]
            )
        ),
    )


class ZipcodeTransform(PiiTransform):
    def normalize(self, column: Column, dtype: DataType) -> Column:
        return regexp_replace(column, "[^0-9]", "")

    def enhancments(self, column: Column) -> dict[str, Column]:
        return {"zip3": substring(column, 1, 3)}


def test_custom_pii_and_token(spark: SparkSession):
    assertDataFrameEqual(
        tokenize(
            (
                spark.createDataFrame(
                    [
                        Row(
                            id=1,
                            first_name="Marie",
                            last_name="Curie",
                            gender="f",
                            birth_date="1867-11-07",
                            zipcode="none",
                        ),
                        Row(
                            id=2,
                            first_name="Pierre",
                            last_name="Curie",
                            gender="m",
                            birth_date="1859-05-15",
                            zipcode="none",
                        ),
                        Row(
                            id=3,
                            first_name="Jonas",
                            last_name="Salk",
                            gender="m",
                            birth_date="1914-10-28",
                            zipcode="10016",
                        ),
                    ]
                )
            ),
            pii_transforms={
                "first_name": OpprlPii.first_name,
                "last_name": OpprlPii.last_name,
                "gender": OpprlPii.gender,
                "birth_date": OpprlPii.birth_date,
                "zipcode": ZipcodeTransform(),
            },
            tokens=[
                TokenInfo("custom_token", ("last_name", "zip3")),
                OpprlToken.token1,
            ],
        ),
        (
            spark.createDataFrame(
                [
                    Row(
                        id=1,
                        custom_token="a4l0zaphD0cOzrrRAsQR4++7c91z+wrhZURjlUQszMHS2H82q5dUzYNmsPaVTHRDVtojQKkvKcj0\r\nziGvRBdKxoqp6b3KgkxAoN9EzbPGQJQ=",
                        opprl_token_1="xsznxClPMFc99UQVJNaprl7a54CTltgSQRNm3e2tMyRrJHlx4ig/hyq2PnhzIg16J9fCCFNMy6g9\r\nweng0bdyy/ZFslqMijL5D7gEDzX45zw=",
                    ),
                    Row(
                        id=2,
                        custom_token="a4l0zaphD0cOzrrRAsQR4++7c91z+wrhZURjlUQszMHS2H82q5dUzYNmsPaVTHRDVtojQKkvKcj0\r\nziGvRBdKxoqp6b3KgkxAoN9EzbPGQJQ=",
                        opprl_token_1="LkVV0j3nRIRGox7Od2kDOY2rRZTI9ZqaFnglRyMYwS5i1MyT4GJwVDyT9/KaAeU7LinYuLB2HMjp\r\nN0whbQKhD4Z2Pb4y8uR6yIcB2q/eKKM=",
                    ),
                    Row(
                        id=3,
                        custom_token="mbWIfUp4H/1QVWKF+aNuHfJfpUgnJrifZndPdVquuYcRiKJjG21jQ/71pAnlvDNjTNq3k0mxlKhW\r\nNaypvBc0ghNfmvS1mPfag6sr12dBu1I=",
                        opprl_token_1="d2tUj3yRFPIBSwR/ntUi8v1B/A9H+Q0iNwlz0+OVpO54MER9bRnTgHxOO8Q4IM+gdoxKGJGV9STb\r\n6DH2hxKIb50v6IFa+StqSnKRy7GJG4U=",
                    ),
                ]
            )
        ),
    )
