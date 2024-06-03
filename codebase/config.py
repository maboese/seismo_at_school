# -*- coding: utf-8 -*-
""" 
Configuration file for the codebase package 
"""
from obspy.taup import TauPyModel

# Seismic wave velocities:
vp = 5.8 # km/s P-Welle
vs = 3.4 # km/s S-Welle

# Model for predicting phase arrivals
model = TauPyModel(model="iasp91")

# Parameters per region scale
regions = {
    "worldwide": {'distance': 9000, 
                  'magnitudes': ['6.0','6.5','7.0'],
                  'filt-freq-range': (0.1, 0.8),
                  'filt-time-range': (0, 80*60)
                  },
    "europe": {'distance': 6000, 
                'magnitudes': ['4.0','5.0','6.0'],
               'filt-freq-range': (0.7, 2.0),
               'filt-time-range': (0, 10*60)
               },
    "switzerland": {'distance': 200, 
                    'magnitudes': ['2.0','2.5','3.5','4.0'],
                    'filt-freq-range': (2.0, 20.0),
                    'filt-time-range': (0, 1.5*60)
                    }
}

# RaspberryShake station list
rs_sta_list =[
["GBIEL","S8C09", "CHASS","GBIEL, Gymnasium Biel-Seeland Biel"],
["GLSTL","RDFB5", "MUTEZ","GLSTL, Gymnasium Liestal"],
["GOBWL","RDFB5","","GOBWL, Gymnasium Oberwil"],
["GOBZL","R19BB", "BALST","GOBZL, Gymnasium Oberaargau"],
["GUSTZ","R4335", "ZUR","GUSTZ, Gymnasium Unterstrass"],
["KSCHR","RB22F", "PLONS","KSCHR, Bündner KS Chur"],
["KSENZ","RD3C4","","KSENZ, KS Enge Zürich"],
["KSHOZ","RE5E7", "ZUR","KSHOZ, KS Hottingen Zürich"],
["KSKNZ","RC23B", "ZUR","KSKNZ, KS Küsnacht"],
["KSROM","R58D2", "WALHA","KSROM, KS Romanshorn"],
["KSRYC","RF726", "WILA","KSRYC, KS Rychenberg Winterthur"],
["KSSO","RFE6B", "MOUTI","KSSO, KS Solothurn"],
["KSURI","R8F49", "MUO","KSURI, KS Uri"],
["KSWAT","R4AF0", "","KSWAT, KS Wattwil"],
["KSZOW","RF726", "WILA","KSZOW, KS Zürcher Oberland, Wetzikon"],
["KSZUG","R3BE0", "ZUR", "KSZUG, KS Zug"],
["MNGRZ","R7DBB", "ZUR","MNGRZ, MNG Rämibühl"],
["COAVI","RA652", "VANNI", "COAVI, CO d'Anniviers"],
["COAYT","RB15C", "SENIN", "COAYT, CO Ayent"],
["CLREN","R3BDC", "", "CLREN, OFFLINE Collège du Léman"],
["COHEU","RB289", "DIX", "COHEU, CO Hérens"],
["COLEY","RA7C7", "GRYON", "COLEY, CO Leytron"],
["COLSL","RE4EF", "VANNI", "COLSL, CO des Liddes"],
["COORS","S3900", "MFERR", "COORS, CO Orsières"],
["COPCM","RA83F", "ILLEZ", "COPCM, CO des Perraires"],
["COSAV","R2D50", "SENIN", "COSAV, CO Savièse"],
["COSTG","R7694", "SENIN", "COSTG, CO St-Guérin"],
["CPPSS","R05D6", "SENIN", "CPPSS, partner institution (SION CPPS HES-SO)"],
["EAMCX","S7A06", "SALAN", "EAMCX, Ecole de l'Arpille"],
["EDILA","RC676", "GOURZ", "EDILA, partner institution (EDI LAUSANNE)"],
["EPSBE","R65E9", "VINZL", "EPSBE, EPS de Begnins – L'Esplanade"],
["EPSEC","R8710", "GOURZ", "EPSEC, EPS Ecublens"],
["EPSGD","R3B57", "CHAMB", "EPSGD, EPS Grandson"],
["EPSLB","R0CD2", "", "EPSLB, OFFLINE EPS Bergières"],
["EPSLE","R5BF0", "GOURZ", "EPSLE, Collège/EPS de l'Elysée"],
["EPSVP","RF727", "GOURZ", "EPSVP, EPSCL Collège du Verney"],
["ESLAS","R8E4D", "LASAR", "ESLAS, ES de La Sarraz et environs"],
["ESNYM","R5D35", "", "ESNYM, OFFLINE ES Nyon-Marens"],
["ESPEC","R46E5", "", "ESPEC, OFFLINE ES du Pays-d'Enhaut"],
["ESTSE","R52F7", "", "ESTSE, OFFLINE ES des Trois-Sapins"],
["ESSTI","R1F5E", "CHASS", "ESSTI, ES St-Imier"]
]