from enum import Enum


class Period(str, Enum):
    Jan = "Jan"
    Feb = "Feb"
    Mar = "Mar"
    Apr = "Apr"
    May = "May"
    Jun = "Jun"
    Jul = "Jul"
    Aug = "Aug"
    Sep = "Sep"
    Oct = "Oct"
    Nov = "Nov"
    Dec = "Dec"
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"


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
