[![DOI](https://zenodo.org/badge/679155888.svg)](https://zenodo.org/badge/latestdoi/679155888)

![logot](/images/tosipaikka_logot.png)

# TosiPaikka - GNSS-IMU-UWB Sensor Fusion

Sovellus GNSS-IMU-UWB-sensorifuusioon. Sovellus lukee MQTT-palvelimen kautta GNSS-vastaanottimelta (u-blox C099-F9P), kiihtyvyysanturilta (Xsens MTi-630 AHRS) ja UWB-moduulilta (Decawave DWM1001C) kerättyä anturidataa ja laskee datan perusteella henkilön sijainnin.

![toimintakaavio](/images/toimintakaavio.png)

## Anturidata

Satelliittivastaanottimelta luettu data on käytännössä UBX-NAV-PVT-viesti, joka sisältää muun muassa vastaanottimen sijainnin pituus- ja leveysasteet sekä *gnssFixOK*-parametrin, joka on 1 tai 0 riippuen siitä, onko sijainti validi vai ei.

Kiihtyvyysanturin data sisältää gravitaatiovapaat x-, y- ja z-kiihtyvyydet, Eulerin kulmat ja kvaterniot.

Sisätilapaikannusjärjestelmän data on *les*-komennon vastaus, joka koostuu ankkurien koordinaateista, ankkurien ja tunnisteen välisistä etäisyysmittauksista ja tunnisteen arvioidusta sijainnista. Dataan on jälkikäteen lisätty *uwbFixOK*-parametri, joka 1 tai 0 riippuen siitä, onko tunnisteen sijainti validi vai ei.

## Saumaton tarkkuuspaikannus

Henkilön sijainti lasketaan Kalman suotimen avulla. Sovellus on suunniteltu toimimaan siten, että suodin osaa laskea henkilön sijainnin, vaikka henkilö siirtyy rakennuksen sisältä ulos tai ulkoa rakennuksen sisälle.

Kun henkilö on sisällä (uwbFixOK = 1), suodin hyödyntää laskuissaan sisätilapaikannusjärjestelmän tunnisteen arvioitua sijaintia. Jos taas henkilö on ulkona (gnssFixOK = 1), suodin käyttää sijainnin laskemisessa satelliittivastaanottimen sijaintia. Molemmissa tapauksissa käytetään kiihtyvyysanturilta saatua kiihtyvyysdataa.

On kuitenkin hyvä huomioida, että satelliittivastaanotin ei saa laskettua välittömästi omaa sijaintiaan, kun henkilö siirtyy sisältä ulos, sillä validin sijainnin saaminen voi kestää jopa useita kymmeniä sekunteja. Tässä tilanteessa suodin käyttää hyväksi sijaintia, jonka suodin itse laski edellisellä kerralla.

Sovellus laskee lopuksi sijainnin WGS84-järjestelmässä ja lähettä sijainnin MQTT-palvelimelle, jotta henkilön sijainti voidaan visualisoida erillisessä karttasovelluksessa.

## Ohjelmistoriippuvuudet

Vaadittavat Python-paketit voidaan asentaan komennolla
```
pip3 install -r requirements.txt
```

Sovellus on tarkoitettu käytettäväksi yhdessä sensoridatan lukijasovelluksen kanssa:

[https://github.com/SeAMKedu/tosipaikka-gnss-imu-uwb-sensor-reader](https://github.com/SeAMKedu/tosipaikka-gnss-imu-uwb-sensor-reader)

## Sovelluksen ajaminen

Sovellus käynnistetään komentokehotteessa suorittamalla komento
```
python3 app.py
```

Sovelluksen ajon voi lopettaa painamalla Ctrl+c.

## Tekijätiedot

Hannu Hakalahti, Asiantuntija TKI, Seinäjoen ammattikorkeakoulu

## Hanketiedot

* Hankkeen nimi: Tosiaikaisen paikkadatan hyödyntäminen teollisuudessa (TosiPaikka)
* Rahoittaja: Etelä-Pohjanmaan liitto
* Aikataulu: 01.12.2021 - 31.08.2023
* Hankkeen kotisivut: [https://projektit.seamk.fi/alykkaat-teknologiat/tosipaikka/](https://projektit.seamk.fi/alykkaat-teknologiat/tosipaikka/)
