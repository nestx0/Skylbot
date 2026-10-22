import random

def generarDeck():
    suits = ["♥️","♦️","♣️","♠️"]
    ranks = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    return [{"rank": r, "suit": s} for s in suits for r in ranks]

def shuffleDeck(deck):
    random.shuffle(deck)

def repartirCartasBJ(deck):

    manoJugador = {
        "cartas":[deck.pop(),deck.pop()],
        "puntuacion":0,
        "esBlackJack":False
    }

    manoDealer = {
        "cartas":[deck.pop(),deck.pop()],
        "puntuacion":0,
        "esBlackJack":False
    }

    return manoJugador, manoDealer

def calcularValor(mano):
    suma = 0
    ases = 0

    for carta in mano["cartas"]:
        valor = carta["rank"]
        if valor in ["J","Q","K"]:
            suma += 10
        elif valor == "A":
            suma += 11
            ases += 1
        else:
            suma += int(valor)
    while suma > 21 and ases > 0:
        suma -= 10
        ases -= 1   
    mano["puntuacion"] = suma
    mano["esBlackJack"] = len(mano["cartas"]) == 2 and suma == 21
    
def draw(deck):
    return deck.pop()
