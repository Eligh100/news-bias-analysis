from enum import Enum

class PoliticalPartyHelper():
    """Allows encoding and decoding between numerical, string, and enum representations of political parties"""

    class PoliticalParty(Enum):
        brexitParty = 1
        conservative = 2
        green = 3
        labour = 4
        libDem = 5
        plaidCymru = 6
        SNP = 7
        UKIP = 8


    enumToPoliticalPartyString = {
        PoliticalParty.brexitParty: "Brexit Party",
        PoliticalParty.conservative: "Conservatives",
        PoliticalParty.green: "Green",
        PoliticalParty.labour: "Labour",
        PoliticalParty.libDem: "Liberal Democrats",
        PoliticalParty.plaidCymru: "Plaid Cymru",
        PoliticalParty.SNP: "SNP",
        PoliticalParty.UKIP: "UKIP",
        "NO PARTY": "No clear party"
    }

    partyNumToEnum = {
        1: PoliticalParty.labour,
        2: PoliticalParty.conservative,
        3: PoliticalParty.libDem,
        4: PoliticalParty.SNP,
        5: PoliticalParty.green,
        6: PoliticalParty.brexitParty,
        7: PoliticalParty.plaidCymru,
        8: PoliticalParty.UKIP,
        9: "NO PARTY"
    }

class TopicsHelper():
    """Allows encoding and decoding between numerical, string, and enum representations of topics"""

    topicIndexToTopic = {
        1: "Scotland",
        2: "Ireland",
        3: "Wales",
        4: "Brexit/EU",
        5: "Economy/Business",
        6: "Healthcare/NHS",
        7: "Foreign Affairs",
        8: "Racism",
        9: "Environment/Climate Change",
        10: "Law/Police",
        11: "Education/Schools",
        12: "Immigration",
    }
