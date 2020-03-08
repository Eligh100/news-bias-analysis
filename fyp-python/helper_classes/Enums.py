from enum import Enum

class PoliticalPartyHelper():
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
    }

class TopicsHelper():
    
    topicIndexToTopic = {
        1: "Labour",
        2: "Conservatives/Government",
        3: "Liberal Democrats",
        4 :"Scotland",
        5: "Ireland",
        6: "Brexit/EU",
        7: "Economy/Business",
        8: "Healthcare/NHS",
        9: "Foreign Affairs",
        10: "Racism",
        11: "Environment/Climate Change",
        12: "Law/Police",
        13: "Education/Schools",
        14: "Immigration",
        15: "Wales"
    }
