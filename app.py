from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_tajny_klucz_foodgo'
DATABASE = 'foodgo.db'

def pobierz_baze():
    polaczenie = sqlite3.connect(DATABASE)
    polaczenie.row_factory = sqlite3.Row
    return polaczenie

def zainicjalizuj_baze():
    with pobierz_baze() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS uzytkownicy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT NOT NULL UNIQUE,
                haslo TEXT NOT NULL,
                rola TEXT NOT NULL
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS dania (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nazwa TEXT NOT NULL,
                opis TEXT,
                cena REAL NOT NULL,
                dostawca TEXT NOT NULL
            )
        ''')
        db.commit()

        liczba_dan = db.execute('SELECT COUNT(*) FROM dania').fetchone()[0]
        
        if liczba_dan == 0:
            wspolne_haslo_hasz = generate_password_hash('restauracja123')
            restauracje = ['Pizzeria Bella', 'Burgerownia Max', 'Sushi Master', 'Pierogarnia Babci', 'Zielony Talerz']
            
            for nazwa_restauracji in restauracje:
                try:
                    db.execute('INSERT INTO uzytkownicy (login, haslo, rola) VALUES (?, ?, ?)', 
                               (nazwa_restauracji, wspolne_haslo_hasz, 'Restauracja'))
                except sqlite3.IntegrityError:
                    pass

            dania_testowe = [
                ('Pizza Margherita', 'Sos pomidorowy, ser mozzarella, swieza bazylia', 24.99, 'Pizzeria Bella'),
                ('Pizza Capricciosa', 'Sos pomidorowy, ser, szynka, pieczarki', 29.50, 'Pizzeria Bella'),
                ('Pizza Pepperoni', 'Sos pomidorowy, mozzarella, pikantne salami', 31.00, 'Pizzeria Bella'),
                
                ('Klasyczny Burger', 'Wolowina 200g, salata, pomidor, cebula, sos', 28.00, 'Burgerownia Max'),
                ('Burger Serowy', 'Wolowina 200g, podwojny ser cheddar, pikle', 32.00, 'Burgerownia Max'),
                ('Burger Ostry', 'Wolowina 200g, papryczki jalapeno, ostry sos', 33.50, 'Burgerownia Max'),
                
                ('Zestaw Futomaki', 'Rolki z lososiem, awokado, ogorkiem (6 szt.)', 26.00, 'Sushi Master'),
                ('Zestaw California', 'Rolki z paluszkiem krabowym i sezamem (8 szt.)', 29.00, 'Sushi Master'),
                ('Zestaw Box Premium', 'Miks rolek: Nigiri, Hosomaki oraz Futomaki', 55.00, 'Sushi Master'),
                
                ('Pierogi Ruskie', 'Tradycyjne pierogi z twarogiem i ziemniakami', 19.90, 'Pierogarnia Babci'),
                ('Pierogi z Miesem', 'Domowe pierogi z farszem z miesa wieprzowego', 22.50, 'Pierogarnia Babci'),
                ('Pierogi z Jagodami', 'Slodkie pierogi z lesnymi jagodami i smietana', 21.00, 'Pierogarnia Babci'),
                
                ('Salatka Cezar', 'Chrupia ca salata rzymska, kurczak, sos cezar', 24.00, 'Zielony Talerz'),
                ('Krem z Pomidorow', 'Aromatyczny, gesty krem ze swiezych pomidorow', 16.50, 'Zielony Talerz'),
                ('Bowl Wege', 'Komosa ryzowa, pieczone bataty, awokado, hummus', 29.90, 'Zielony Talerz')
            ]
            
            db.executemany('INSERT INTO dania (nazwa, opis, cena, dostawca) VALUES (?, ?, ?, ?)', dania_testowe)
            db.commit()

@app.route('/')
def index():
    if 'zalogowany_uzytkownik' in session:
        return redirect(url_for('menu'))
    return redirect(url_for('logowanie'))

@app.route('/logowanie', methods=['GET', 'POST'])
def logowanie():
    komunikat = ""
    if request.method == 'POST':
        akcja = request.form.get('akcja')
        login = request.form.get('login').strip()
        haslo = request.form.get('haslo').strip()
        rola = request.form.get('rola')

        if not login or not haslo:
            komunikat = "Pola nie moga byc puste!"
            return render_template('logowanie.html', komunikat=komunikat)

        db = pobierz_baze()

        if akcja == 'zarejestruj':
            haslo_hasz = generate_password_hash(haslo)
            try:
                db.execute('INSERT INTO uzytkownicy (login, haslo, rola) VALUES (?, ?, ?)', (login, haslo_hasz, rola))
                db.commit()
                komunikat = "Konto utworzone! Zaloguj sie."
            except sqlite3.IntegrityError:
                komunikat = "Taki login juz istnieje!"
                
        elif akcja == 'zaloguj':
            uzytkownik = db.execute('SELECT * FROM uzytkownicy WHERE login = ?', (login,)).fetchone()
            if uzytkownik and check_password_hash(uzytkownik['haslo'], haslo):
                session['zalogowany_uzytkownik'] = uzytkownik['login']
                session['rola_uzytkownika'] = uzytkownik['rola']
                session['koszyk'] = []
                return redirect(url_for('menu'))
            else:
                komunikat = "Bledny login lub haslo!"

    return render_template('logowanie.html', komunikat=komunikat)

@app.route('/menu')
def menu():
    if 'zalogowany_uzytkownik' not in session:
        return redirect(url_for('logowanie'))
        
    db = pobierz_baze()
    
    if session['rola_uzytkownika'] == 'Restauracja':
        wszystkie_dania = db.execute('SELECT * FROM dania WHERE dostawca = ?', (session['zalogowany_uzytkownik'],)).fetchall()
    else:
        wszystkie_dania = db.execute('SELECT * FROM dania').fetchall()
        
    return render_template('menu.html', dania=wszystkie_dania, uzytkownik=session['zalogowany_uzytkownik'], rola=session['rola_uzytkownika'])

@app.route('/dodaj', methods=['GET', 'POST'])
def dodaj():
    if 'zalogowany_uzytkownik' not in session or session['rola_uzytkownika'] != 'Restauracja':
        return redirect(url_for('menu'))

    if request.method == 'POST':
        nazwa = request.form.get('nazwa')
        opis = request.form.get('opis')
        cena = request.form.get('cena')
        dostawca = session['zalogowany_uzytkownik']

        if nazwa and cena:
            db = pobierz_baze()
            db.execute('INSERT INTO dania (nazwa, opis, cena, dostawca) VALUES (?, ?, ?, ?)', 
                       (nazwa, opis, float(cena), dostawca))
            db.commit()
            return redirect(url_for('menu'))

    return render_template('dodaj.html', rola=session['rola_uzytkownika'])

@app.route('/usun/<int:id>')
def usun(id):
    if 'zalogowany_uzytkownik' in session and session['rola_uzytkownika'] == 'Restauracja':
        db = pobierz_baze()
        db.execute('DELETE FROM dania WHERE id = ? AND dostawca = ?', (id, session['zalogowany_uzytkownik']))
        db.commit()
    return redirect(url_for('menu'))

@app.route('/dodaj_do_koszyka/<int:id>')
def dodaj_do_koszyka(id):
    if 'zalogowany_uzytkownik' not in session:
        return redirect(url_for('logowanie'))
    
    db = pobierz_baze()
    danie = db.execute('SELECT * FROM dania WHERE id = ?', (id,)).fetchone()
    
    if danie:
        koszyk = session.get('koszyk', [])
        koszyk.append({
            'id': danie['id'],
            'nazwa': danie['nazwa'],
            'cena': danie['cena'],
            'dostawca': danie['dostawca']
        })
        session['koszyk'] = koszyk
        session.modified = True
        
    return redirect(url_for('menu'))

@app.route('/koszyk')
def wyswietl_koszyk():
    if 'zalogowany_uzytkownik' not in session:
        return redirect(url_for('logowanie'))
        
    koszyk = session.get('koszyk', [])
    suma = 0.0
    for produkt in koszyk:
        suma += produkt['cena']
    suma = round(suma, 2)
        
    return render_template('koszyk.html', koszyk=koszyk, suma=suma, rola=session['rola_uzytkownika'])

@app.route('/usun_z_koszyka/<int:indeks>')
def usun_z_koszyka(indeks):
    if 'zalogowany_uzytkownik' in session:
        koszyk = session.get('koszyk', [])
        if 0 <= indeks < len(koszyk):
            koszyk.pop(indeks)
            session['koszyk'] = koszyk
            session.modified = True
    return redirect(url_for('wyswietl_koszyk'))

@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if 'zalogowany_uzytkownik' not in session:
        return redirect(url_for('logowanie'))
        
    komunikat = ""
    typ_komunikatu = ""
    
    if request.method == 'POST':
        nowy_login = request.form.get('nowy_login').strip()
        nowe_haslo = request.form.get('nowe_haslo').strip()
        stary_login = session['zalogowany_uzytkownik']
        
        if not nowy_login:
            komunikat = "Nazwa użytkownika nie może być pusta!"
            typ_komunikatu = "error"
        else:
            db = pobierz_baze()
            try:
                if nowe_haslo:
                    nowe_haslo_hasz = generate_password_hash(nowe_haslo)
                    db.execute('UPDATE uzytkownicy SET login = ?, haslo = ? WHERE login = ?', 
                               (nowy_login, nowe_haslo_hasz, stary_login))
                else:
                    db.execute('UPDATE uzytkownicy SET login = ? WHERE login = ?', (nowy_login, stary_login))
                
                if session['rola_uzytkownika'] == 'Restauracja':
                    db.execute('UPDATE dania SET dostawca = ? WHERE dostawca = ?', (nowy_login, stary_login))
                
                db.commit()
                
                session['zalogowany_uzytkownik'] = nowy_login
                komunikat = "Dane profilu zostały pomyślnie zaktualizowane!"
                typ_komunikatu = "success"
            except sqlite3.IntegrityError:
                komunikat = "Ta nazwa użytkownika jest już zajęta!"
                typ_komunikatu = "error"
                
    return render_template('profil.html', uzytkownik=session['zalogowany_uzytkownik'], rola=session['rola_uzytkownika'], komunikat=komunikat, typ_komunikatu=typ_komunikatu)

@app.route('/wyloguj')
def wyloguj():
    session.clear()
    return redirect(url_for('logowanie'))

if __name__ == '__main__':
    zainicjalizuj_baze()
    app.run(debug=True)