from enum import Enum


class Country(str, Enum):
    MX = "MX"
    DE = "DE"
    FR = "FR"
    CA = "CA"
    GB = "GB"
    NZ = "NZ"
    JP = "JP"
    US = "US"
    CH = "CH"
    ZA = "ZA"
    EU = "EU"
    AU = "AU"
    TR = "TR"
    ES = "ES"
    IT = "IT"


class Currency(str, Enum):
    CAD = "CAD"
    GBP = "GBP"
    MXN = "MXN"
    NZD = "NZD"
    ZAR = "ZAR"
    EUR = "EUR"
    TRY = "TRY"
    CHF = "CHF"
    AUD = "AUD"
    USD = "USD"
    JPY = "JPY"
