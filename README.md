# Návody

HTML návody v tomto adresári. `index.html` zobrazuje zoznam automaticky –
nový návod stačí uložiť ako `.html` súbor do adresára (nadpis sa berie z `<h1>`
alebo `<title>`, popis z `<meta name="description">` alebo `<p class="lead">`).

## Spustenie lokálne

```
./spusti_server.sh        # http://localhost:8080/
```

Server je dostupný aj v lokálnej sieti (port treba povoliť vo firewalle).

## Ikona v paneli (Xfce)

```
python3 tray.py           # spustí server, otvorí prehliadač, pridá ikonu do panela
```

Ľavý klik na ikonu otvorí návody, pravý klik ponúkne menu (kopírovať adresu pre sieť,
reštart, zastavenie). Záznam servera: `~/.cache/navody-server.log`.
Odkaz na plochu: `~/Plocha/navody-server.desktop` (spúšťa `tray.py`).

## Domovská stránka (domov.html)

Offline úvodná stránka v jednom súbore – funguje aj bez servera (stačí ju otvoriť
dvojklikom). Vyhľadávanie (bez diakritiky, Enter otvorí prvý výsledok, `/` skočí
do hľadania), filtre podľa skupín, „Často používané“, kontrola dostupnosti
a úpravy priamo na stránke (✎ Upraviť).

- Odkazy sú v súbore **`odkazy.js`** vedľa stránky (`ODKAZY = { … }` – JSON
  s jedným riadkom navyše, aby sa dal načítať aj cez `file://`).
  Súbor je v `.gitignore` a na GitHub nejde. Ak chýba, zobrazí sa ukážka.
- Úpravy sa ukladajú v prehliadači. Natrvalo ich uložíš cez ⚙ → *Stiahnuť
  odkazy.js* a nahradením súboru vedľa stránky.
- Ikony z [dashboardicons.com](https://dashboardicons.com/icons) sa po prvom
  načítaní uložia v prehliadači a potom fungujú aj bez internetu.
