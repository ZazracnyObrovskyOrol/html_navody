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
