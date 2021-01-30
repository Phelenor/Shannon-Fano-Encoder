import sys
import math
from operator import itemgetter

SYMBOL_PROBABILITIES = []   # Matrica vjerojatnosti simbola
ENCODED = []                # Lista kodiranih simbola
REPEAT = False
REPEAT_POSSIBLE = False


# Funkcija za sumiranje vrijednosti u zadanoj listi
def probability_sum(p_list):
    p_sum = 0
    for symbol in p_list:
        p_sum += symbol[1]
    return p_sum


# Funkcija za unos podataka s provjerom ispravnosti
def take_input():
    global SYMBOL_PROBABILITIES
    symbol_num = 0
    eng_alphabet = False
    user_in = 2

    # Unos broja simbola koji ce se kodirati
    while symbol_num <= 1:
        try:
            symbol_num = int(input("Unesite velicinu ulaznog skupa simbola: "))
            eng_alphabet = True if symbol_num <= 26 else False
        except ValueError:
            print("Pogreska. Pokusajte ponovno.")
            continue
        if symbol_num > 1:
            break
        else:
            print("Velicina ulaznog skupa mora biti veca od 1. Pokusajte ponovno.")

    # Ako je simbola manje od 26 prigodno ih prikazujemo znakovima
    # engleske abecede, inače brojkama
    print("-------------------------------------------------------")
    if eng_alphabet:
        print("Simboli ce biti oznaceni znakovima engleske abecede.")
    else:
        print("Simboli ce biti oznaceni prirodnim brojevima.")
    print("Za izlaz iz programa unesite 'x'.")
    print("-------------------------------------------------------")
    print("Unesite vjerojatnosti pojavljivanja simbola: ")

    # Unos vjerojatnosti pojavljivanja simbola
    for i in range(symbol_num):
        # Provjera premasuje li suma dotad unesenih vjerojatnosti 1
        # Ako premasuje zaustavljamo program
        if round(probability_sum(SYMBOL_PROBABILITIES), 2) > 1:
            print("Pogreska. Suma vjerojatnosti mora biti jednaka 1.")
            input("Pritisnite bilo koju tipku za izlaz.")
            sys.exit()
        if round(probability_sum(SYMBOL_PROBABILITIES), 3) == 1:
            print("Pogreska. Suma vjerojatnosti jednaka je 1 prije nego\nsu unesene vjerojatnosti svih simbola.")
            print("Kodirani ce biti simboli cije su vjerojatnosti unesene.")
            break

        # Unos vjerojatnosti simbola uz provjeru ispravnosti
        # Ako uneseno nije decimalni broj manji od jedan, upit
        # za unos se ponavlja dok uvjet ne bude zadovoljen ili
        # dok ne bude upisan znak 'x'
        while user_in > 1:
            try:
                if eng_alphabet:
                    user_in = input(f"P({chr(97 + i)}) = ")
                else:
                    user_in = input(f"P({i + 1}) = ")

                user_in = user_in.split(sep='/')
                if len(user_in) == 1:
                    user_in = user_in[0]
                    user_in = float(user_in)
                elif len(user_in) == 2 and user_in[1] != "0":
                    user_in = float(user_in[0]) / float(user_in[1])
                else:
                    user_in = user_in[0]
                    raise ValueError

                if user_in >= 1 or user_in <= 0:
                    raise ValueError
                if user_in != 0:
                    # Redak matrice simbola opisuje jedan simbol
                    # Sadrzi redni broj simbola (po unosu), vjerojatnost i njegov kod
                    SYMBOL_PROBABILITIES.append([i, user_in, ""])
            except ValueError:
                if user_in == 'x':
                    sys.exit()
                user_in = 2
                print("Vjerojatnosti moraju biti pozitivni brojevi manji od 1.\nPokusajte ponovno.")
                continue
        user_in = 2

    # Provjera je li nakon zavrsenog unosa zeljenog broja simbola
    # zadovoljen uvjet (suma vjerojatnosti = 1)
    if round(probability_sum(SYMBOL_PROBABILITIES), 2) != 1:
        print("Pogreska. Suma vjerojatnosti nije jednaka 1.")
        input("Pritisnite bilo koju tipku za izlaz.")
        sys.exit()


# Funkcija za rekurzivno kodiranje zadanog skupa simbola metodom Shannon-Fano
def shannon_fano(symbols):
    global REPEAT_POSSIBLE
    # Sortiranje matrice simbola po vjerojatnostima, silazno
    symbols = sorted(symbols, key=itemgetter(1), reverse=True)

    # Osnovni slucajevi rekurzije:
    # simbolu vece vjerojatnosti pridruzujemo 0, manjem 1
    # Dodajemo ih matrici kodiranih simbola
    if len(symbols) == 2:
        symbols[0][2] = symbols[0][2] + "0"
        symbols[1][2] = symbols[1][2] + "1"
        ENCODED.extend(symbols)
        return
    # Ako je u podmatrici samo jedan simbol, on je vec kodiran
    elif len(symbols) == 1:
        ENCODED.extend(symbols)
        return
    elif len(symbols) == 0:
        return

    partition_ind = 0  # indeks na kojemu razdvajamo matricu simbola na dva dijela ("poloviste")

    # Pomocne sume vjerojatnosti za odredivanje "polovista", temp1 broji od pocetka, temp2 od kraja
    temp1_p = temp2_p = 0
    half_p = round(probability_sum(symbols) / 2, 4)

    for i in range(len(symbols)):
        temp1_p += symbols[i][1]
        # Ako je suma od pocetka jednaka polovici sume vjerojatnosti, nasli smo "poloviste"
        if round(temp1_p, 4) == half_p:
            partition_ind = i + 1
            break
        # Ako je suma od pocetka veca od polovice, zbrajamo vjerojatnosti od kraja
        elif temp1_p >= half_p:
            for j in range(len(symbols) - 1, -1, -1):
                temp2_p += symbols[j][1]
                # Odredujemo poloviste tako da odaberemo element na kojemu se zaustavio brojac
                # u sumi koja je manja
                if not REPEAT_POSSIBLE and round(temp2_p, 4) == round(temp1_p, 4):
                    REPEAT_POSSIBLE = True
                if temp2_p >= half_p:
                    if not REPEAT:
                        partition_ind = (i + 1) if round(temp2_p, 4) >= round(temp1_p, 4) else j
                    else:
                        partition_ind = (i + 1) if round(temp2_p, 4) > round(temp1_p, 4) else j
                    break
            break

    # Stvaramo dvije podgrupe simbola te kodovima njihovih simbola dodajemo '0' ili '1'
    sub_group1 = symbols[0:partition_ind]
    for sym in sub_group1:
        sym[2] = sym[2] + "0"

    sub_group2 = symbols[partition_ind:]
    for sym in sub_group2:
        sym[2] = sym[2] + "1"

    # Pokrecemo proces kodiranja za obje podgrupe simbola
    shannon_fano(sub_group1)
    shannon_fano(sub_group2)


# Funkcija za ispis kodova simbola
def print_code(codes):
    codes = sorted(codes, key=itemgetter(0))
    if len(SYMBOL_PROBABILITIES) <= 26:
        for i in range(len(codes)):
            print(f"{chr(97 + i)} = {codes[i][2]}")
    else:
        for i in range(len(codes)):
            print(f"{i + 1} = {codes[i][2]}")


# Funkcija koja racuna srednju duljinu kodne rijeci
def avg_code_length(codes):
    avg_len = 0
    # L = sum(p[i] * l[i])
    for code in codes:
        avg_len += code[1] * len(code[2])
    return avg_len


# Funkcija koja računa efikasnost koda, potrebna nam
# je entropija te srednja duljina kodne rijeci
def code_efficiency(codes, length):
    entropy = 0
    # Računamo entropiju H = -sum(log2(p[i]) * p[i])
    for code in codes:
        entropy += -code[1] * math.log(code[1], 2)
    # Vraćamo efikasnost e = H / L
    return entropy / length


# Funkcija koja poziva sve ostale funkcije te
# formatira i ureduje ispis
def encode_display():
    global SYMBOL_PROBABILITIES
    global ENCODED
    ENCODED = []
    for i in range(len(SYMBOL_PROBABILITIES)):
        SYMBOL_PROBABILITIES[i][2] = ""
    print("-------------------------------------------------------")
    print("Kodirani simboli:")
    shannon_fano(SYMBOL_PROBABILITIES)
    print_code(ENCODED)
    avg_len = avg_code_length(ENCODED)
    print(f"Srednja duljina kodne rijeci L = {round(avg_len, 3)} bit/simbol")
    print(f"Efikasnost koda e = {round(code_efficiency(ENCODED, avg_len), 4)}")
    print("-------------------------------------------------------")


# Funkcija koja daje izbor ponavljanja kodiranja jer
# ovisno o razdiobi kojom radimo kodiranje kod moze
# imati drugaciju srednju duljinu kodne rijeci
def repeat():
    global REPEAT
    print("Kodiranje alternativnom razdiobom moze (ali ne mora)\ndati kracu srednju duljinu koda.")
    if input("Za ponavljanje unesite 'p', za izlaz 'x': ") == 'p':
        REPEAT = True
        return True
    else:
        return False


def main():
    take_input()
    encode_display()
    if REPEAT_POSSIBLE:
        if repeat():
            encode_display()


if __name__ == '__main__':
    main()
    input()
