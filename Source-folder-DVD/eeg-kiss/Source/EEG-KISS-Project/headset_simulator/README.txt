De serial_simulator is een opzet voor een python script dat een Imec headset kan imiteren.
Om deze te kunnen gebruiken in de EEG-Kiss software moet een virtuele com-poort aangemaakt worden.
Op Windows kan dit met com0com (pas op, neem de signed versie):
https://code.google.com/p/powersdr-iq/downloads/detail?name=setup_com0com_W7_x64_signed.exe&can=2&q=

com0com maakt twee compoorten aan: koppel de ene aan de simulator (1e regel in '__main__') en open de andere in EEG-Kiss.

Als het goed is stuurt de simulator een gecombineerd sinus-signaal naar alle 8 EEG kanalen en 0 naar de Imp kanalen.
