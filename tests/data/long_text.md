## E-mail

Pekný piatok všetkým,

na úvod vás chcem všetkých privítať na kurze Kvantitativní metody. V pondelok nás čaká naše prvé spoločné cvičenie. Jedným z prvkov, ktoré chcem v rámci výuky tento semester vyskúšať budú krátke e-maily "na zamyslenie". V týchto e-mailoch vám v krátkosti dobredu predstavím nejaký problém súvisiaci s témou nasledujúceho cvičenia. Od vás budem chcieť, aby ste sa nad týmto problémom skúsili na 10-15 minút zamyslieť. Nejde nutne o to, aby ste našli správne riešnie, ale aby ste sa sami pokúsili vymyslieť postup, ako by sa daná úloha dala riešiť.

Tento prístup je inšpirovaný konceptom produktívneho zlyhania (angl. productive failure). Jeho základnou myšlienkou je, že "trápenie sa" nad určitým problémom vám pomôže ho pochopiť lepšie, než keby vám len niekto priamo ukázal postup, ako ho vyriešiť. Ak sa nebojíte angličtiny, tak pekné zhrnutie nájdete napríklad tu: https://fs.blog/2012/04/the-learning-paradox/

Tak a teraz už k samotnému problému:

Predstavte si, že máme pekáreň, ktorá pečie a následne predáva 3 druhy výrobkov: chleba, rohlíky a housky. K výrobe tohto pečiva potrebuje múku a vajíčka (a ďalšie suroviny, ktoré ale budeme nateraz ignorovať). Na jeden deň má táto pekáreň k dispozícii 100kg múky a 100 vajec. Okrem surovín je potrebná aj pracovná sila. Pekáreň má k dispozícii 4 pekárov. Každý z nich pracuje 7.5 hodiny denne. O spotrebe surovín ďalej vieme, že na jeden chleba potrebujeme 0.5kg múky a 5 minút práce (vajíčka nepotrebujeme). Na jeden rohlík potrebujeme v priemere 30g múky, a pol minúty práce. Na housku zase 50g múky, 0.2 vajíčka (z jedného vajíčka upečieme 5 housek) a 1 minutu práce. Chceme zistiť koľko máme čoho upiecť, aby sme mali čo najvyššie tržby. Vieme pritom, že 1 chleba predáme za veľkoobchodnú cenu 10Kč, 1 rohlík za 0.80Kč a jednu housku 1.5Kč. Pre jednoduchosť uvažujme, že poptávka je neobmedzená a sme schopní predať všetko, čo upečieme.

Chcel by som, aby ste sa v kontexte tohto problému skúsili zamyslieť predovšetkým nad tým, ako popísať tento problém pomocou matematiky. Presné riešenie zatiaľ hľadať nemusíte. Následne sa tomuto problému budeme venovať na cvičení.

Želám všetkým pekný víkend a vidíme sa v pondelok,

Miloš.

## Cvičenie

### Uvod (5 minut)

- Kto som, kde ma najdu
- Cvicenia sa budu nahravat, ak vsetci suhlasia. Bude ale naviazane na ucast. Aspon polka ludi.
- Vratit sa k posielaniu mailov
- Na cviceni budem ocakavat aktivitu (budem vyvolavat)
- Na SII robime vyskum aj v oblasti linearneho programovania, ci obecnejsie rozhodovania. Venujeme sa pritom hlavne situaciam za rizika alebo neurcitosti

### Moj pohlad na matematicke programovanie (20 minut)

- Matematicke programovanie je nastroj, ktory by nam mal pomahat v rozhodovani
- Riesi ale specificky druh rozhodovacich problemov
- Klasicky rozhodovaci problem - mam si vybrat jednu z konecneho poctu alternativ. Ked kupujem notebook, tak ci vyberam jeden z tych, co napriklad nejaky e-shop ponuka. Toto sa da riesit metodami viackriterialneho rozhodovania
- MP naproti tomu riesi problemy, kde hladame najlepsiu kombinaciu roznych prvkov, pricom kazdy prvok moze byt zastupeny v inom mnozstve. Pri vybere kombinacii sme este typicky limitovani roznymi obmezeniami
- Zakladny ekonomicky problem, kedy mame rozdelit obmedzene mnozstvo zdrojov do roznych aktivit tak, aby sme maximalizovali celkovy uzitok, splna vsetky tieto charakteristiky.
- Konkretnejsi priklad - ako vlada mame rozpocet a ten musime rozdelit medzi aktivity ako zdravotnictvo, zemedelstvi, vzdelavanie, bezpecnost a pod.
- Keby sme to riesili ako vyber notebooku, tak cely nas rozpocet by sme dali do jednej aktivity.
- To je ale blbost
- Nas rozpocet chceme nejakym sposobom rozdelit medzi viacere aktivity - otazka je teda, "kolko coho"
- Otazka na studenta: keby sme uvazovali len dve aktivity napr. Vzdelavanie a zdravotnictvo a mame nejaky fixny rozpocet napr. 10 miliard korun, kolko roznych sposobov ako tieto peniaze rozdelit existuje?
- Prvy dolezity prvok: rozhodovacie premenne. Hladame odpoved na otazku kolko coho. Nateraz je pre nas tento udaj neznamy, takze ho nahradime premennou x - podobne ako pri rieseni rovnic na strednej. Mame x, ktoreho hodnotu sa snazime najst. Akurat teraz uz k tomu vyuzijeme pocitac. Dolezite je uvedomit si jednotky.
- Spominali sme obmedzenia - ekonomicke zdroje su obmedzene, rozpocet je obmezeny a pod. Tie predstavuju druhy vyznamny prvok - PVO.
- PVO maju podobu nerovnic a obcas rovnic, ktore musia platit, tvoria nam tzv. Mnozinu pripustnych rieseni.
- Otazka na studenta - ako by sme zachytili, ze nas rozpocet nesmie prekrocit 10 miliard Kc.
- Typicky k modelu pridavame este podmienky nezapornosti.
- Aj ked mame PVO, stale mozeme vyberat z nekonecneho mnozstva kombinacii. My chceme najst tu nejlepsiu, teda optimalnu kombinaciu. K tomu potrebujeme ucelovu funkciu. Na nu sa da jednoducho divat tak, ze je to vzorec do ktoreho vlozime nejaku konkretnu kombinaciu (hodnoty rozhodovacich premennych) a tento vzorec nam vyhodi cislo, ktore nam povie ako kvalitne to riesenie je.
- A my chceme but co najvyssie cislo (maximalizovat) alebo co najnizsie cislo (minimalizovat).
- Tento vzorec nam casto zaroven spocita nejaky konkretny ekonomicky udaj (celkove naklady, ktore chceme minimalizovat, celkove trzby, co chceme maximalizovat a pod)
- Cim sa lisi Linearne programovanie od matematickeho - mame iba linearne funkcie.

### Priklad pekara (15 minut)

- *Otazka na studenta - ake mame rozhodovacie premenne (kolko ich bude a co budu vyjadrovat). Co sa snazime najst?*
- *Otazka na studenta - Ako by sme mohli porovnat vyhodnost jednotlivych kombinacii? Je nejaka jednoduchy ekonomicky ukazatel, co by nam v tom pomohol? Ako ho spocitame?*
- *Otazka na studenta - cim sme obmedzeni? Je nieco, co nemozeme prekrocit?*
- *Otazka na studenta - kolko muky realne spotrebujeme?*
- *Otazka na studenta - kolko vajicok realne spotrebujeme?*
- *Otazka na studenta - kolko pracovneho casu realne spotrebujeme?*
- *Otazka na studenta - ma zmysel, aby nejake x bolo zaporne?*

### Pauza (5 minút)

- budem sa snažiť počas cvičení krátke pauzy, počas ktorých sa budem snažiť dávať tipy na lepšie učenie
- Tip 1: Spánok
    - Dospelý človek potrebuje 7.5 až 9 hodín spánku
    - Výskum naznačuje, že spánok má veľmi dôležitú úlohu pri dlhodobom ukladaní informácií. Vypadá to tak, že mozog počas spánku spracúva informácie, ktoré cez deň získal. Ráno múdrejšie večera.
    - Spánok nám tiež umožňuje prečistiť mozog od nepotrebných informácii a pripraviť ho tak na ďalšie učenie
    - Čo potenciálne môže pomôcť je, ak si tesne pred spánkom zopakujete tie najpodstatnejšie informácie, čo si chcete zapamätať.
    - Štúdie tiež naznažujú, že krátke 20 až 30 minútové zdriemnutie počas dňa zlepšuje našu schopnosť učiť sa
    - Nedostatok spánku má negatívny vplyv na sústredenie sa, učenie a pamäť. Nie je dobrý nápad sa pred skúškou nevyspať.

### Excel (20 minut)

- *Student pri PC: Nazov vyrobku, nazov premennej, pociatocne hodnoty premennej*
- *Student pri PC: Zapis ucelovej funkcie*
- *Student pri PC: Zapis prvej podmienky*
- *Student pri PC: Zapis druhej podmienky*
- *Student pri PC: Pouzitie riesitela*

### Druhy priklad - Zostavenie PC (20 minut)

- Mame firmu, ktora sa zaobera zostavovanim hotovych pocitacov z jednotlivych komponentov. Specializuje sa pritom na 2 typy pocitacovych zostav. Vo vyrobe ju obmedzuje niekolko faktorov. Prvy z nich je pracovny cas. Zostavenie prveho typu zostavy trva 3 hodiny, zostavenie druheho typu 5 hodin. Na planovane obdobie mame na skladanie PC k dispozicii celkom 150 hodin casu nasich zamestnancov. Druhym obmedzenim je mnozstvo potrebneho skladovacieho priestoru. Prvy typ PC potrebuje 8dm^2, druhy typ 5 dm^2. K dispozici mame priestor 300dm^2. Kvoli nedostupnosti niektorych komponentov mozeme vyrobit max 20ks prveho typu PC. Kolko kusov jednotlivych druhov PC mame vyrobit, ak chceme maximalizovat nas cisty zisk a vieme, ze za 1 ks prveho PC mame zisk 300Kc a za druhy typ PC 240Kc.
- *Otazka na studenta: rozhodovacie premenne*
- *Otazka na studenta: ucelova funkcia*
- *Otazka na studenta: Podmienka pracovny cas*
- *Otazka na studenta: Podmienka na sklad*
- *Otazka na studenta: Podmienka prve PC iba 20 Ks*

# E-mail

Pekný deň všetkým,

ako som sľúbil, posielam znova krátky e-mail na zamyslenie. Jednou z tém nasledujúceho cvičenia (a zrejme aj prednášky) budú rôzne praktické aplikácie Lineárneho programovania. Jednou z tých zaujímavejších je tvorba investičného portfólia (napr. z akcií firiem alebo podielových fondov). Tu je pár otázok, nad ktorými by ste sa znovu mohli zamyslieť ešte predtým, než pôjdete na prednášku a cvičenie:

1. Aké rozhodovacie premenné by mohol obsahovať model na tvorbu investičného portfólia? Ako zistíme ich počet. Čo budú reprezentovať? V akých jednotkách budú?
2. Ako môžeme merať kvalitu nášho portfólia, čo budeme chcieť mať v rámci investičného portfólia čo najnižšie alebo čo najvyššie?
3. Napadajú vám nejaké podmienky vlastných obmedzení, ktoré by v modeli pre tvorbu investičného portfólia mohli byť?

Snažil som sa tiež informovať ohľadom pripojenia vlastného notebooku k projektoru, aby sa mohlo nahrávať, no zatiaľ som bohužiaľ bez odpovede. Snáď sa mi to ešte do pondelka podarí vyriešiť.

Prajem vám všetkým pekný víkend a vidíme sa v pondelok.

Miloš.

## Úvod (3 minúty)

- Nech si študenti zapnú PC
- Na dnešnom a zrejme aj budúcom cviku si postupne prejdeme niekoľko typov úloh a praktických aplikácií Lineárneho programovania. A začneme tým, čo som spomínal v maili - teda tvorba investičného portfólia

## Investičná úloha - zadanie (5 minút)

- Chceme vytvořit investiční portfolio z následujících podílových fondů:

[Untitled Database](https://www.notion.so/50932074468f4c6da9d73d7944c4bbd7?pvs=21)

- Od našeho portfolia chceme očekávaný roční výnos minimálně 6%.
- *Otázka na studenty: Co chceme optimalizovat (jak budeme vyhodnovat kvalitu různých portfolií)?*

## Vytvorenie modelu (15 minut)

- Otázka na studenta: kolik máme rozhodovacích proměnných, co reprezentují a v jakých jednotkách budou?
- Otázka na studenta: Jakou podmínkou bychom mohli popsat zabezpečení minimálního výnosu?
- Otázka na studenta: Momentálně hodnoty rozhodovacích proměnných můžou růst donekonečna. Jak bychom je mohli omezit? Čím jsme v realitě při investovaní omezeni?
- Otázka na studenta: Jak bychom mohli vzorcem vyjádřit celkové riziko portfolia.

## Model v MS Excel (15 minut)

- Student 1: Zápis promenných a UF
- Student 2: Zápis podmínek
- Student 3: Řešitel

## Pár postřehů k investičním úlohám (5 minut)

- V realitě se používají nelineární modely
- Hlavním problémem je vyjádrění rizika
- V našem případě ignorujeme jeden důležitý aspekt - vzájemnou závislost různých aktiv.
- Výnosy aktiv jsou v mnohých případech korelované, t.j. například pokud roste cena jednoho aktiva, tak roste cena i aktiva druhého
- Jsou rizikové míry, které si s tím umí poradit - vedou ale právě k nelineárním modelům.
- Tímto modelům se s některými z vás možná budeme věnovat v rámci magisterského předmětu Optimalizační metody
- Dalším problémem je, že neřešíme poplatky
- Taky je otázné jak dobře historie popisuje budoucí vývoj
- Poslední otázku řeším v rámci moji dizertace - skouším použít sentiement ze sociálních sítí k zlepšení predikce jak výnosů, tak i různých rizikových měr a použít tyto predikce pro optimalizaci portfolia.

## Pauza (5 minút)

**Používanie viacerých zmyslov pri učení**

- možno ste sa stretli s teóriou, že každý človek má nejaký dominantný štýl učenia vzhľadom k našim zmyslom (vizuálny, zvukový, pohybový a pod.)
- nie je však úplne jednoznačné, že to tak aj v realite funguje
- miesto používania jedného zmyslu je vhodnejšie pri učení zapojiť zmyslov čo najviac
  - zrak - čítanie ale predovšetkým obrázky
  - zvuk - nahrávky ale aj hovorenie nahlas, či pred spolužiakom
  - čuch - je veľmi zaujímavý - môže pomáhať pri tvorbe spomienok a spomínaní si na ne. Z biologického pohľadu to súvisí s tým, že časť mozgu zodpovedná za spracovanie čuchovej informácie je blízko časti zodpovednej za pamäť a emócie. Skúste experimentovať s vytvorením asociácie medzi niečim, čo sa učíte a nejakou konkrétnou vôňou.
  - V experimente z roku 1969 porovnávali, ako dobre sa darilo študentom v troch skupinách na teste z určitého učiva: Prvá skupina si materiál len prečítala, druhá skupina si vypočula rovnaké informácie od prednášajúceho. Tretia skupina sa zúčastnila prednášky, ktorá ale bola doplnená o obrazový materiál. Študenti v prvej skupine si boli schopni na teste správne spomenúť na cca 10% informácií a v druhej skupine na 20% informácií. V tretej skupine to ale bolo až 50%.
  - jedno z teoretických vysvetlení z pohľadu neurológie je, že nám pomáha si k tej istej informácii vytvoriť viacero ciest.

## Poměrová podmínka (15 minut)

- Dejme tomu, že chceme zabezpečit, v Evropských akciích byla alespoň polovina z toho, co máme akcích amerických.
- Otázka na studenta: jak bychom tento požadavek mohli vyjádřit? Ignorujme nateď požadavky linearity
- Otázka na studenta: jak z tohoto zápisu udelat lineární
- Student pri PC: přidání podmínky a řešitel

## Příklad k procvičení (5 minut)

Mame firmu, ktora sa zaobera zostavovanim hotovych pocitacov z jednotlivych komponentov. Specializuje sa pritom na 2 typy pocitacovych zostav. Vo vyrobe ju obmedzuje niekolko faktorov. Prvy z nich je pracovny cas. Zostavenie prveho typu zostavy trva 3 hodiny, zostavenie druheho typu 5 hodin. Na planovane obdobie mame na skladanie PC k dispozicii celkom 150 hodin casu nasich zamestnancov. Druhym obmedzenim je mnozstvo potrebneho skladovacieho priestoru. Prvy typ PC potrebuje 8dm2, druhy typ 5 dm2. K dispozici mame priestor 300dm2. Kvoli nedostupnosti niektorych komponentov mozeme vyrobit max 20ks prveho typu PC. Kolko kusov jednotlivych druhov PC mame vyrobit, ak chceme maximalizovat nas cisty zisk a vieme, ze za 1 ks prveho PC mame zisk 300Kc a za druhy typ PC 240Kc.

## Sestavení modelu (15 minut)

- *Otázka na studenta: Kolik máme proměnných a co nám budou reprezentovat*
- *Otázka na studenta: Jak budeme porovnávat různe kombinace vyrobených PC (účelová funkce)*
- *Otázka na studenta : jaké máme omezení*

# E-mail

Pekný deň všetkým,

ako som spomínal v pondelok, na ďalšom cvičení budeme pokračovať s ďalšími aplikáciami lineárneho programovania. Okrem iného sa bližšie pozrieme na spätnú väzbu. Dnešný príklad na zamyslenie súvisí práve s ňou:

Máme firmu, ktorá sa zaoberá výrobou počítačových čipov a zároveň vyrába mobilné telefóny (v podobnej situácii je napríklad firma Samsung). Čipy sa typicky produkujú vo forme "platní" známych ako wafery. (https://en.wikipedia.org/wiki/Wafer_(electronics)) Množstvo vyrobených čipov teda môžeme počítať na plochu vyrobených waferov v cm2. Vyrobené čipy firma buď predá alebo ich použije ako komponent do svojich telefónov. Kapacita firmy, čo sa týka výroby waferov, je obmedzená dostupnosťou surovín a technickým vybavením na 50m2 mesačne. Na výrobu jedného kusu mobilného telefónu firma potrebuje 5cm2 čipov. Zároveň je k výrobe potrebný aj plast, ktorého má firma na mesiac k dispozícii 6 ton, a hliník, ktorého sú k dispozícii 2 tony. Na jeden telefón pritom je pritom potrebných 150g plastu a 25g hliníku. Ako ma firma naplánovať množstvo vyrobených čipov a telefónov tak, aby dosiahla čo najvyšší zisk? Zisk z predaja 1cm2čipov je pritom 75Kč a zisk z predaja jedného telefónu je 2000Kč.

V rámci tejto úlohy sa skúste zamyslieť predovšetkým nad tým, kde sa v tomto probléme nachádza spätná väzba a ako by sme ju mohli popísať matematicky.

Nakoniec by som vás chcel ešte informovať, že do LMS, zložky Cvičenia -> Miloš Švaňa som pridal súbor "odkazy.pdf", kde okrem iného nájdete odkaz, kde budem postupne pridávať nahrávky cvičení a tiež odkazy na moje poznámky, ktoré si ku cvičeniam robím (okrem iného v nich nájdete aj zadania príkladov z cvičení). Dajte mi prosím vedieť, ak by niektorý z odkazov prípadne nefungoval.

Želám vám pekný víkend a vidíme sa v pondelok,

Miloš.

# Cvičenie

## Úvod (3 min)

Záznamy a odkazy na poznámky v LMS

Účasť

## Riešenie príkladu z e-mailu (25 min)

## Ukázať druhý spôsob riešenia (10 min)

## Pauza (5 min)

Písanie poznámok:

- Na internete nájdete veľa rôznych rád týkajúcich sa písania poznámok
- Mnohí napríklad riešia, či písať poznámky rukou na papier, na tablet, alebo do notebooku na klávesnici
- Médium je však menej dôležité ako samotný obsah poznámok
- Pri pochopení danej témy pomáha, ak nepíšete poznámky od slova do slova podľa toho, čo rozpráva prednášajúci alebo ako je daný text napísaný v knihe, ale prevádzate ich na vlastné slová
- Znovu to má neurologické vysvetlenie - tým že používate vlastné slová, napájate nový materiál na už existujúce nervové spojenia v mozgu
- Jedna z možností - prečítať si (pod)kapitolu, zatvoriť knihu a skúsiť do jedného krátkeho odstavca stručne zhrnúť o čom bola. Výhodou je, že spomínananím si sa zároveň učíme.
- Rôzne štýly poznámok:
  - Outline - odrážky
  - Cornell - delenie papiera na 3 časti - kľúčové pojmy naľavo, poznámky napravo a dolu stručné zhrnutie
  - Mind/concept map
  - Otázky a odpovede


![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/8dc11b4c-2984-4e1f-8c55-987977fc13e3/Untitled.png)

## Tvorba zmesí - Zadanie (5 minút)

Chceme zostaviť porciu jedálnička v závodnej jedálni. Máme pritom k dispozícii 3 suroviny - hovězí maso, brambory a rajčata. Táto musí spĺňať určité podmienky týkajúce sa výživových hodnôt. Mala by obsahovať aspoň 600mg vitamínu C, no nie viac ako 900mg. Ďalej by ala obsahovať aspoň 35g proteínu a mala by disponovať energetickou hodnotou aspoň 800kJ. Ako bude zloženie tejto porcie vypadať, ak chceme, aby bola pre nás čo najlacnejšia?

Nasledujúca tabuľka udáva informácie o cene a výživových hodnotách jednotlivých surovín:

[Untitled Database](https://www.notion.so/9b4f62b947a94d26ad30a10c4c9db664?pvs=21)

## Tvorba zmesí - tvorba modelu (15 minút)

## Tvorba zmesí - riešenie modelu v Exceli (10 minút)

## Tvorba zmesí - pridanie pomerovej podmienky (10 minút)

Ako by sme zabezpečili, aby rajčata tvorili aspoň 20% hmotnosti celej porcie?

## Príklad na precvičenie, ak budeme stíhať

Petrochemická výrobní firma vyrábí PET lahve. Vyrábí 3 druhy lahví: L1 – 0,5 litru, L2 – 1 litr a L3 – 1,5 litru a vyrábí je postupem z peletkových granulí, které potřebuje vždy v určitém množství na konkrétní druh PET lahve. Peletkové granule nemá k dispozici hotové, ale vyrábí si je jako polotovar z drtě, kdy spotřeba činí 800 g drtě na 1 ks peletkové dávky. Drtě má k dispozici na 1 měsíc produkce 10 tun. Výrobním postupem je dáno, že na 1 ks láhve L1 je zapotřebí 1 dávka, na 1 ks láhve L2 je zapotřebí 1,5 dávky a na 1 ks láhve L3 jsou zapotřebí 2 dávky. Zjistěte, jak by měla firma nastavit výrobní program, aby maximalizovala vyráběné množství PET lahví, musí-li odběrateli dodat minimální množství jednotlivých druhů lahví, a to 500 ks L1, 800 ks L2 a 1000 ks L3.