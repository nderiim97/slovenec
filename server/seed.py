"""Demo content and first-run seeding.

All people, events and quotes in this file are fictional. The portal is a
demonstration and must not be presented as real reporting.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import settings
from .models import AdminUser, Article, Category, Setting
from .security import hash_password

CATEGORIES = [
    ("slovenija", "Slovenija", "#e01b22", "Novice iz vse Slovenije", 1),
    ("svet", "Svet", "#1d4ed8", "Dogajanje v tujini", 2),
    ("gospodarstvo", "Gospodarstvo", "#15803d", "Trg, podjetja in finance", 3),
    ("kronika", "Kronika", "#9f1239", "Črna kronika in varnost", 4),
    ("sport", "Šport", "#ea580c", "Rezultati in zgodbe s terena", 5),
    ("kultura", "Kultura", "#7c3aed", "Umetnost, glasba in film", 6),
    ("mnenja", "Mnenja", "#0f766e", "Kolumne in komentarji", 7),
    ("tehnologija", "Tehnologija", "#4338ca", "Digitalno in znanost", 8),
    ("zabava", "Zabava", "#db2777", "Estrada in mediji", 9),
    ("zdravje", "Zdravje", "#0891b2", "Zdravje in dobro počutje", 10),
]

ARTICLES: list[dict] = [
    {
        "slug": "vlada-potrdila-proracunski-paket-2027",
        "title": "Vlada potrdila proračunski paket za leto 2027",
        "deck": "Predlog predvideva višje izdatke za zdravstvo, šolstvo in železnico. Opozicija opozarja na novo zadolževanje.",
        "category": "slovenija",
        "author": "Maja Kos",
        "cover": 1,
        "tags": ["proračun", "vlada", "finance"],
        "featured": True,
        "views": 4820,
        "minutes": 4,
        "published": "2026-11-12T07:40:00",
        "body": """Vlada je na dopisni seji potrdila predlog proračuna za leto 2027. Dokument predvideva 16,4 milijarde evrov odhodkov, kar je 4,8 odstotka več kot v letošnjem letu. Največji del povečanja je namenjen zdravstvu, šolstvu in posodobitvi železniške infrastrukture.

Po besedah ministra za finance naj bi se primanjkljaj države znižal na 2,3 odstotka bruto domačega proizvoda. »Proračun je razvojno naravnan, a ostaja znotraj fiskalnih pravil,« je povedal na novinarski konferenci. Dodal je, da so rezerve za morebitne krizne ukrepe ohranjene.

Opozicija predlogu očita predvsem novo zadolževanje in premalo konkretnih številk pri reformi zdravstva. »Vidimo le obljube, ne pa tudi načrta, kako bodo bolnišnice dobile dodatne ekipe,« je dejala poslanka opozicije. Razprava v državnem zboru se začne prihodnji teden.

Predlog mora najprej prestati razpravo v matičnih odborih, nato pa še glasovanje v državnem zboru. Če bo sprejet, bo proračun začel veljati 1. januarja 2027.""",
    },
    {
        "slug": "hitri-vlaki-ljubljana-maribor-december",
        "title": "Hitri vlaki med Ljubljano in Mariborom od decembra",
        "deck": "Nov vozni red skrajšuje pot na uro in 45 minut. Na relaciji bo dnevno šest dodatnih povezav.",
        "category": "slovenija",
        "author": "Rok Zupan",
        "cover": 2,
        "tags": ["železnica", "promet", "vlaki"],
        "featured": True,
        "views": 3910,
        "minutes": 3,
        "published": "2026-11-12T06:15:00",
        "body": """S prvim decembrom bo med Ljubljano in Mariborom vozilo šest dodatnih hitrih vlakov na dan. Potovalni čas se bo skrajšal na približno uro in 45 minut, so sporočili iz Slovenskih železnic.

Novi vozni red prinaša tudi več povezav zgodaj zjutraj in pozno zvečer. »Želimo, da je vlak resnična alternativa avtomobilu za dnevne migrante,« je povedal predstavnik prevoznika. Na ključnih postajah bodo posodobili tudi informacijske zaslone.

Potniki pozdravljajo spremembo, a opozarjajo na zanesljivost. »Hitrost je pomembna, še bolj pa, da vlak pride pravočasno,« je dejala potnica z ljubljanske postaje. Železnice napovedujejo dodatna vzdrževalna dela na odsekih, kjer so bila v preteklosti najpogostejša zamude.

Cene vozovnic ostajajo nespremenjene do konca leta. Za dijake in študente bodo še naprej veljale posebne ugodnosti.""",
    },
    {
        "slug": "inflacija-upocasnjena-2-1-odstotka",
        "title": "Inflacija v Sloveniji upočasnjena na 2,1 odstotka",
        "deck": "Cene hrane so prvič po dolgem času padle, energija pa ostaja glavni vir negotovosti.",
        "category": "gospodarstvo",
        "author": "Nina Pavlin",
        "cover": 3,
        "tags": ["inflacija", "cene", "statistika"],
        "featured": True,
        "views": 3210,
        "minutes": 3,
        "published": "2026-11-11T16:20:00",
        "body": """Letna inflacija v Sloveniji se je oktobra upočasnila na 2,1 odstotka, kar je najnižja raven v zadnjih dveh letih. Po podatkih statističnega urada so se cene hrane in brezalkoholnih pijač na mesečni ravni prvič po več mesecih znižale.

Najbolj so se podražile storitve, predvsem zavarovanja in gostinske storitve. Cene energije so ostale približno na enaki ravni kot leto prej, a analitiki opozarjajo, da lahko zima prinese novo negotovost.

»Upočasnitev je dobra novica za gospodinjstva, vendar še ne pomeni, da so pritiski na cene povsem popustili,« je dejala ekonomistka. Po njenem mnenju bo ključno, kako se bodo gibale cene storitev v prvem četrtletju prihodnjega leta.

Vlada je ob objavi podatkov napovedala, da bo še naprej spremljala cene osnovnih življenjskih potrebščin. Trgovci medtem opozarjajo, da so marže v nekaterih segmentih že zelo nizke.""",
    },
    {
        "slug": "vrh-eu-energetska-varnost",
        "title": "Vrh EU o energetski varnosti: dogovor o skupnih rezervah plina",
        "deck": "Voditelji so potrdili načrt za skupno nabavo in solidarnostne rezerve pred zimo.",
        "category": "svet",
        "author": "Tomaž Ferenc",
        "cover": 4,
        "tags": ["EU", "energija", "plin"],
        "featured": False,
        "views": 2870,
        "minutes": 4,
        "published": "2026-11-11T14:05:00",
        "body": """Voditelji držav članic Evropske unije so na izrednem vrhu v Bruslju potrdili okvir za skupno nabavo plina in vzpostavitev solidarnostnih rezerv. Dogovor naj bi državam pomagal pri blaženju cenovnih šokov v zimskih mesecih.

Po besedah predsednice Evropske komisije je cilj, da se zmanjša odvisnost od posameznih dobaviteljev in poveča preglednost pogodb. Nekatere države so zahtevale dodatna jamstva, da skupne rezerve ne bodo nadomestile nacionalnih.

Slovenija je dogovor pozdravila. »Za nas je pomembno, da imamo jasen mehanizem solidarnosti in da so majhne države enako obravnavane,« je dejal vir iz vlade. Podrobnosti izvajanja bodo znane do konca meseca.

Analitiki opozarjajo, da bo učinek odvisen od hitrosti izvedbe. Poleg plina ostaja odprto tudi vprašanje dolgoročnih naložb v obnovljive vire in omrežja.""",
    },
    {
        "slug": "olimpija-derbi-maribor",
        "title": "Olimpija v derbiju premagala Maribor z 2:1",
        "deck": "Odločilni gol je padel v 87. minuti pred polnimi Stožicami. Maribor je končal z igralcem manj.",
        "category": "sport",
        "author": "Luka Bevk",
        "cover": 5,
        "tags": ["nogomet", "Olimpija", "Maribor"],
        "featured": True,
        "views": 6120,
        "minutes": 3,
        "published": "2026-11-11T22:10:00",
        "body": """Nogometaši Olimpije so v 16. krogu državnega prvenstva premagali Maribor z 2:1. Pred 16.000 gledalci v Stožicah je odločilni gol v 87. minuti dosegel rezervist, ki je na igrišče stopil le deset minut prej.

Maribor je povedel v prvem polčasu po hitri protiakciji, a je Olimpija izenačila tik pred odmorom. V drugem delu so bili Ljubljančani bolj konkretni, gostje pa so v 70. minuti ostali z igralcem manj po drugem rumenem kartonu.

»Fantje so verjeli do konca. Zamenjave so prinesle energijo, ki smo jo potrebovali,« je po tekmi dejal trener Olimpije. Njegov kolega na klopi Maribora je bil kritičen do sojenja, a je priznal, da je bila ekipa v zadnjih dvajsetih minutah premalo pogumna.

Olimpija se je z zmago utrdila na vrhu lestvice. Maribor ostaja v boju za evropska mesta, a bo moral v prihodnjih tekmah popraviti predvsem igro v gosteh.""",
    },
    {
        "slug": "janja-garnbret-svetovna-lestvica",
        "title": "Janja Garnbret znova na vrhu svetovne lestvice",
        "deck": "Slovenska plezalka je z zmago v Innsbrucku prevzela vodstvo v skupnem seštevku sezone.",
        "category": "sport",
        "author": "Ana Rožman",
        "cover": 6,
        "tags": ["plezanje", "Garnbret", "svetovni pokal"],
        "featured": False,
        "views": 4100,
        "minutes": 2,
        "published": "2026-11-11T18:30:00",
        "body": """Janja Garnbret je na tekmi svetovnega pokala v Innsbrucku zmagala v težavnosti in se vrnila na prvo mesto skupne lestvice. V finalu je bila edina, ki je priplezala do vrha smeri.

»Vedela sem, da moram biti potrpežljiva. Smer je bila zahtevna, a mi je ustrezala,« je povedala po tekmi. Drugouvrščena tekmovalka je zaostala za več kot deset oprimkov.

Garnbretova je letos že osvojila dve zlati medalji. Pred zadnjo tekmo sezone ima prednost 120 točk, kar ji daje dobre možnosti za skupno zmago.

Sezona se zaključi v začetku decembra. Slovenska ekipa bo nastopila še na tekmi v Kranju, kjer pričakujejo polne tribune.""",
    },
    {
        "slug": "razstava-slovenska-moderna-ljubljana",
        "title": "V Ljubljani odprli razstavo o slovenski moderni",
        "deck": "Pregledna razstava v Narodni galeriji prinaša več kot 120 del iz domačih in tujih zbirk.",
        "category": "kultura",
        "author": "Eva Hribar",
        "cover": 7,
        "tags": ["razstava", "umetnost", "Ljubljana"],
        "featured": False,
        "views": 1450,
        "minutes": 3,
        "published": "2026-11-11T12:00:00",
        "body": """V Narodni galeriji v Ljubljani so odprli razstavo, ki na enem mestu predstavlja razvoj slovenske moderne od začetka 20. stoletja do petdesetih let. Na ogled je več kot 120 slik, grafik in kipov.

Kustosi so dela združili po temah, ne po kronologiji. Obiskovalci tako prehajajo med pokrajino, portretom in abstrakcijo, kar po njihovih besedah omogoča bolj oseben pogled na obdobje.

»Želeli smo pokazati, da moderna ni bila le prelom, ampak tudi nadaljevanje,« je na odprtju dejala kustosinja. Razstavo spremlja katalog z eseji in reprodukcijami.

Razstava bo odprta do konca februarja prihodnje leto. Galerija napoveduje tudi vodstva ob četrtkih in delavnice za šole.""",
    },
    {
        "slug": "pozar-skladisce-celje",
        "title": "Požar v skladišču v Celju, brez poškodovanih",
        "deck": "Gasilci so ogenj pogasili v dobri uri. Vzrok požara še ni znan, škoda je velika.",
        "category": "kronika",
        "author": "Uredništvo",
        "cover": 8,
        "tags": ["požar", "Celje", "gasilci"],
        "featured": False,
        "breaking": True,
        "views": 5320,
        "minutes": 2,
        "published": "2026-11-12T05:25:00",
        "body": """V skladišču podjetja v industrijski coni v Celju je ponoči izbruhnil požar. Gasilci so ga pogasili v dobri uri, poškodovanih ni bilo, so sporočili s celjske policijske uprave.

Ogenj se je razširil po skladiščnem prostoru, kjer so bile shranjene embalaža in papirne pole. Dim je bil sprva viden iz več delov mesta, zato so prebivalce pozvali, naj zaprejo okna.

»Ob prihodu je bila stavba že močno zadimljena. Uspeli smo preprečiti širjenje na sosednje objekte,« je povedal vodja intervencije. Na kraju je bilo približno 40 gasilcev z dvanajstimi vozili.

Policija je začela preiskavo. Po prvih ugotovitvah naj bi požar izbruhnil v skladiščnem delu, kjer so bili nameščeni električni stroji. Lastnik podjetja je ocenil, da bo škoda znašala več sto tisoč evrov.""",
    },
    {
        "slug": "policija-opozarja-kriptovalute-goljufije",
        "title": "Policija opozarja na goljufije s kriptovalutami",
        "deck": "V zadnjem mesecu so zabeležili več primerov, v katerih so oškodovanci izgubili tudi po več deset tisoč evrov.",
        "category": "kronika",
        "author": "Sara Jereb",
        "cover": 9,
        "tags": ["kriptovalute", "goljufije", "policija"],
        "featured": False,
        "views": 2680,
        "minutes": 3,
        "published": "2026-11-10T10:45:00",
        "body": """Policija svari pred goljufijami, povezanimi s kriptovalutami. V zadnjem mesecu so zabeležili več primerov, ko so oškodovanci nakazali denar na tuje platforme v upanju na hitro in visoko donosnost.

Goljufi najpogosteje uporabljajo lažne spletne strani in profile na družbenih omrežjih. Žrtvam obljubljajo zagotovljene donose, nato pa zahtevajo dodatna plačila za »odklepanje« sredstev.

»Če nekdo obljavlja donos brez tveganja, je to že sam po sebi znak za alarm,« je dejal predstavnik policije. Oškodovanci naj vse primere prijavijo, tudi če menijo, da denarja ne bodo dobili nazaj.

Policija svetuje, da se pred vsako naložbo preveri, ali je ponudnik registriran in nadzorovan. Prav tako naj ljudje ne delijo gesel ali dostopov do svojih denarnic.""",
    },
    {
        "slug": "kolumna-stanovanjska-politika",
        "title": "Kolumna: Zakaj potrebujemo novo stanovanjsko politiko",
        "deck": "Cene najema so v Ljubljani presegle raven, ki je za mlade družine vzdržna. Rešitev ni le gradnja.",
        "category": "mnenja",
        "author": "Miha Ravnik",
        "cover": 10,
        "tags": ["stanovanja", "kolumna", "Ljubljana"],
        "featured": False,
        "views": 1890,
        "minutes": 4,
        "published": "2026-11-10T08:00:00",
        "body": """Vsako leto se ob začetku študijskega leta ponovi ista zgodba: študenti iščejo sobe, mlade družine pa stanovanja, ki jih na trgu ni ali pa so predraga. Statistika je jasna, politika pa ostaja razdrobljena.

Gradnja je nujna, a sama po sebi ne zadostuje. Potrebujemo tudi urejen najemni trg, pregledne pogodbe in spodbude za lastnike, da stanovanja oddajajo dolgoročno. Brez tega bo vsaka nova stavba le nov kanal za kratkoročni najem.

Prav tako je treba razmišljati o javnih stanovanjih kot o infrastrukturi, ne kot o socialni pomoči. Ko stanovanje postane dostopno, se ljudje lažje odločajo za otroke, selitve zaradi dela in ostajanje v domačem kraju.

Rešitve ne bodo poceni, a strošek nedelovanja je še višji. Vprašanje ni, ali si lahko privoščimo stanovanjsko politiko, ampak koliko nas stane, ker je nimamo.""",
    },
    {
        "slug": "slovenski-startup-baterija-reciklirani-materiali",
        "title": "Slovenski start-up razvil baterijo iz recikliranih materialov",
        "deck": "Prototip naj bi omogočal hitrejše polnjenje in manjšo odvisnost od redkih kovin.",
        "category": "tehnologija",
        "author": "Jure Oman",
        "cover": 11,
        "tags": ["baterije", "start-up", "recikliranje"],
        "featured": True,
        "views": 3520,
        "minutes": 3,
        "published": "2026-11-11T09:10:00",
        "body": """Slovenski start-up je predstavil prototip litij-ionske baterije, pri kateri so večino materialov pridobili z recikliranjem odsluženih celic. Po navedbah podjetja naj bi baterija omogočala hitrejše polnjenje in manjšo porabo redkih kovin.

Razvoj so podprli z evropskim sredstvi, prve teste pa so opravili v sodelovanju z ljubljansko fakulteto. »Cilj ni le okoljska zgodba, ampak tudi stroškovna prednost,« je dejal soustanovitelj.

Prototip še ni pripravljen za množično proizvodnjo. Podjetje načrtuje pilotno linijo v prihodnjem letu, za katero išče dodatne vlagatelje.

Strokovnjaki so do rezultatov zadržani, a pozitivni. Opozarjajo, da bo treba preveriti življenjsko dobo celic in varnost pri večjih obremenitvah.""",
    },
    {
        "slug": "ai-v-solah-smernice-ministrstva",
        "title": "Umetna inteligenca v šolah: ministrstvo objavilo smernice",
        "deck": "Dokument učiteljem svetuje, kako uporabljati orodja in kako preverjati verodostojnost vsebin.",
        "category": "tehnologija",
        "author": "Jure Oman",
        "cover": 12,
        "tags": ["AI", "šolstvo", "ministrstvo"],
        "featured": False,
        "views": 2210,
        "minutes": 3,
        "published": "2026-11-09T13:40:00",
        "body": """Ministrstvo za vzgojo in izobraževanje je objavilo smernice za uporabo umetne inteligence v šolah. Dokument ni prepoved, ampak okvir, ki učiteljem pomaga pri načrtovanju pouka in ocenjevanju.

Smernice poudarjajo, da morajo učenci razumeti, kako orodja delujejo in kje so njihove omejitve. Učiteljem svetujejo, naj naloge oblikujejo tako, da spodbujajo razmišljanje, ne le prepisovanje odgovorov.

»Umetna inteligenca ne bo nadomestila učitelja, lahko pa mu olajša delo, če jo uporablja premišljeno,« je dejala državna sekretarka. Šole bodo dobile tudi primere dobrih praks.

Nekateri sindikati so opozorili, da bodo potrebna dodatna usposabljanja in oprema. Ministrstvo napoveduje, da bo do pomladi pripravilo še priročnik za ravnatelje.""",
    },
    {
        "slug": "film-preseren-nagrada-portoroz",
        "title": "Film o Prešernu osvojil glavno nagrado v Portorožu",
        "deck": "Žirija je pohvalila igralsko zasedbo in pretanjen pogled na pesnikovo življenje.",
        "category": "zabava",
        "author": "Eva Hribar",
        "cover": 4,
        "tags": ["film", "festival", "Portorož"],
        "featured": False,
        "views": 1760,
        "minutes": 2,
        "published": "2026-11-08T21:30:00",
        "body": """Na festivalu slovenskega filma v Portorožu je glavno nagrado prejel celovečerec o življenju Franceta Prešerna. Žirija je pohvalila igralsko zasedbo, fotografijo in pretanjen pogled na pesnikovo notranje življenje.

Režiser je nagrado posvetil ekipi. »To je film o človeku, ki je živel med idealom in vsakdanjostjo. Vesel sem, da je to prepoznala tudi žirija,« je dejal.

Poleg glavne nagrade je film prejel še nagrado za najboljšo moško vlogo. Občinstvo je izbralo dokumentarec o slovenskih planinah.

Festival je letos obiskalo več kot 20.000 gledalcev. Organizatorji napovedujejo, da bodo prihodnje leto razširili program s sekcijo za mlade avtorje.""",
    },
    {
        "slug": "cepljenje-proti-gripi-kdo-naj-se-cepi",
        "title": "Cepljenje proti gripi: kdo naj se cepi in kdaj",
        "deck": "Epidemiologi priporočajo cepljenje starejšim, kroničnim bolnikom in zdravstvenim delavcem.",
        "category": "zdravje",
        "author": "dr. Petra Vovk",
        "cover": 6,
        "tags": ["cepljenje", "gripa", "zdravje"],
        "featured": False,
        "views": 3120,
        "minutes": 3,
        "published": "2026-11-09T07:20:00",
        "body": """Sezona gripe se običajno začne v decembru, najboljši čas za cepljenje pa je oktober in november. Letošnje cepivo je prilagojeno prevladujočim sevom, ki krožijo v Evropi.

Cepljenje je še posebej priporočljivo za osebe, starejše od 65 let, kronične bolnike, nosečnice in zdravstvene delavce. Za otroke od šestega meseca starosti je smiselno posvetovanje s pediatrom.

»Cepivo ne prepreči vsake okužbe, bistveno pa zmanjša tveganje za hude zaplete,« je povedala epidemiologinja. Poudarila je, da je cepljenje varno tudi v kombinaciji z drugimi cepivi.

Poleg cepljenja je priporočljivo redno umivanje rok, prezračevanje prostorov in ostajanje doma ob simptomih. Bolnišnice so že začele s pripravami na povečan obisk.""",
    },
    {
        "slug": "zakon-o-najemu-stanovanj-javna-razprava",
        "title": "Novi zakon o najemu stanovanj v javni razpravi",
        "deck": "Predlog uvaja register najemnih pogodb in jasnejša pravila za kratkoročno oddajanje.",
        "category": "slovenija",
        "author": "Maja Kos",
        "cover": 8,
        "tags": ["stanovanja", "zakon", "najem"],
        "featured": False,
        "views": 2040,
        "minutes": 3,
        "published": "2026-11-10T15:10:00",
        "body": """Ministrstvo je v javno razpravo poslalo predlog novega zakona o najemu stanovanj. Predlog uvaja register najemnih pogodb, jasnejša pravila za kratkoročno oddajanje in možnost hitrejšega reševanja sporov.

Po besedah ministrstva naj bi register povečal pravno varnost najemnikov in lastnikov. Kratkoročno oddajanje bi bilo omejeno v stavbah, kjer je to že urejeno s soglasjem etažnih lastnikov.

Predlogu so načeloma naklonjene najemniške organizacije, medtem ko del lastnikov opozarja na dodatno birokracijo. »Vsaka evidenca je lahko koristna, če je preprosta in ne podvaja obstoječih postopkov,« je dejal predstavnik lastnikov.

Javna razprava bo odprta do 15. decembra. Predlog naj bi v državni zbor prišel v prvem četrtletju prihodnjega leta.""",
    },
    {
        "slug": "turizem-rekordna-sezona-obala",
        "title": "Turizem: rekordna sezona na slovenski obali",
        "deck": "Število nočitev je preseglo lanski rekord, a ponudniki opozarjajo na kadrovske težave.",
        "category": "gospodarstvo",
        "author": "Nina Pavlin",
        "cover": 10,
        "tags": ["turizem", "obala", "sezona"],
        "featured": False,
        "views": 1980,
        "minutes": 2,
        "published": "2026-11-08T11:00:00",
        "body": """Slovenska obala je letos zabeležila rekordno turistično sezono. Po podatkih občin so nočitve presegle lanski rekord za približno šest odstotkov, največ gostov pa je prišlo iz Avstrije, Nemčije in Italije.

Ponudniki so zadovoljni z obiskom, a opozarjajo na pomanjkanje sezonskih delavcev. »Povpraševanje je, težava je, kako zagotoviti dovolj kakovostnega osebja za celotno sezono,« je dejala lastnica manjšega hotela v Piranu.

Občine načrtujejo dodatne naložbe v javni promet in urejanje plaž. Hkrati razmišljajo o ukrepih za bolj enakomerno porazdelitev obiska izven poletnih mesecev.

Turistični delavci si želijo, da bi država poenostavila postopke za zaposlovanje tujih delavcev. Ministrstvo napoveduje, da bo predlog pripravilo do začetka prihodnje sezone.""",
    },
    {
        "slug": "volitve-nemcija-slovenija",
        "title": "Volitve v Nemčiji: kaj izid pomeni za Slovenijo",
        "deck": "Nemčija ostaja najpomembnejši gospodarski partner Slovenije, zato bo sestava vlade pomembna tudi za Ljubljano.",
        "category": "svet",
        "author": "Tomaž Ferenc",
        "cover": 11,
        "tags": ["Nemčija", "volitve", "gospodarstvo"],
        "featured": False,
        "views": 1620,
        "minutes": 3,
        "published": "2026-11-07T19:40:00",
        "body": """Nemške volitve so prinesle tesno zmago, sestavljanje vlade pa bo verjetno trajalo več tednov. Za Slovenijo je izid pomemben predvsem zaradi gospodarskih odnosov.

Nemčija je največja izvozna partnerica Slovenije. Spremembe v fiskalni politiki in odnosu do industrijske energije bodo vplivale tudi na slovenska podjetja, ki so vpeta v nemške dobavne verige.

Diplomati v Ljubljani pričakujejo nadaljevanje sodelovanja, ne glede na sestavo vlade. »Nemčija je predvidljiv partner, in to je za nas pomembno,« je dejal vir iz ministrstva za zunanje zadeve.

Analitiki opozarjajo, da bo ključno vprašanje, kako bo nova vlada obravnavala evropsko industrijska politiko in širitev EU. Slovenija si želi napredka pri širitvi na Zahodni Balkan.""",
    },
    {
        "slug": "slovenija-kvalifikacije-svetovno-prvenstvo",
        "title": "Slovenija v kvalifikacijah za svetovno prvenstvo",
        "deck": "Reprezentanca je v skupini zbrala sedem točk in ostaja v igri za drugo mesto.",
        "category": "sport",
        "author": "Luka Bevk",
        "cover": 12,
        "tags": ["reprezentanca", "kvalifikacije", "nogomet"],
        "featured": False,
        "views": 2890,
        "minutes": 2,
        "published": "2026-11-09T22:50:00",
        "body": """Slovenska nogometna reprezentanca je po remiju v gosteh zbrala sedem točk v kvalifikacijski skupini. Ekipa ostaja v igri za drugo mesto, ki vodi v dodatne kvalifikacije.

Selektor je po tekmi poudaril, da je ekipa pokazala karakter, a da bo morala izboljšati učinkovitost v napadu. »Imeli smo dovolj priložnosti, da bi zmagali,« je dejal.

Naslednja tekma bo doma v Ljubljani. Pričakuje se poln stadion, saj vstopnice za severno tribuno že skoraj ni več mogoče dobiti.

Do konca kvalifikacij sta še dve tekmi. Slovenska ekipa bo morala zmagati vsaj enkrat in upati na ugoden izid tekmecev.""",
    },
    {
        "slug": "slovenski-film-cannes",
        "title": "Slovenski film v Cannesu? Producenti potrjujejo pogovore",
        "deck": "Novi celovečerec naj bi imel svetovno premiero prihodnje leto, a podrobnosti ostajajo skrivnost.",
        "category": "kultura",
        "author": "Eva Hribar",
        "cover": 5,
        "tags": ["film", "Cannes", "produkcija"],
        "featured": False,
        "views": 1340,
        "minutes": 2,
        "published": "2026-11-07T14:15:00",
        "body": """Slovenski producenti potrjujejo, da potekajo pogovori o uvrstitvi novega celovečernega filma v program festivala v Cannesu. Uradne potrditve še ni, zato podrobnosti ostajajo skrivnost.

Film je nastal v slovensko-francoski koprodukciji. Snemanje je potekalo na več lokacijah v Sloveniji in na Hrvaškem, v glavnih vlogah pa nastopajo slovenski igralci.

»Veseli smo zanimanja, a dokler ni uradne odločitve, ne želimo napovedovati preveč,« je dejal producent. Premiera v Sloveniji je predvidena za jesen prihodnje leto.

Če bo film uvrščen v Cannes, bo to eden največjih mednarodnih uspehov slovenske kinematografije v zadnjih letih.""",
    },
    {
        "slug": "vremensko-opozorilo-veter-primorska",
        "title": "Vremensko opozorilo: močan veter na Primorskem",
        "deck": "Zaradi burje so zaprli del obalne ceste, na Krasu pa pričakujejo sunke do 110 kilometrov na uro.",
        "category": "kronika",
        "author": "Uredništvo",
        "cover": 7,
        "tags": ["vreme", "burja", "Primorska"],
        "featured": False,
        "breaking": True,
        "views": 4210,
        "minutes": 2,
        "published": "2026-11-12T06:50:00",
        "body": """Agencija za okolje je za Primorsko izdala oranžno vremensko opozorilo zaradi močne burje. Na Krasu in v Vipavski dolini pričakujejo sunke do 110 kilometrov na uro.

Zaradi varnosti so zaprli del obalne ceste med Izolo in Piranom. Avtobusni prevozniki opozarjajo na možne zamude, pristaniška uprava pa je omejila delo v koprskem pristanišču.

»Voznikom svetujemo previdnost, predvsem na odprtih odsekih in mostovih,« so sporočili s policije. Dvigala in začasne konstrukcije naj bodo ustrezno zavarovani.

Burja naj bi se umirila v popoldanskih urah. Do takrat velja opozorilo tudi za pohodnike in kolesarje.""",
    },
    {
        "slug": "uredniski-komentar-mediji-zaupanje",
        "title": "Uredniški komentar: Mediji in zaupanje",
        "deck": "Zaupanje v medije ne izhaja iz hitrosti, ampak iz doslednosti in pripravljenosti priznati napako.",
        "category": "mnenja",
        "author": "Uredništvo",
        "cover": 9,
        "tags": ["mediji", "komentar", "zaupanje"],
        "featured": False,
        "views": 1120,
        "minutes": 3,
        "published": "2026-11-06T09:00:00",
        "body": """V času, ko se novice širijo hitreje kot kadarkoli prej, je zaupanje v medije dragocenejše od klikov. Vsaka napaka, ki je ne popravimo, oslabi tudi delo tistih, ki svoje delo opravljajo vestno.

Zaupanje se ne gradi z gesli in kampanjami, ampak z doslednostjo. Bralec mora vedeti, kdo je vir, kako je bila informacija preverjena in kaj ostaja neznano.

Prav zato bomo še naprej objavljali popravke na vidnem mestu in ločevali poročanje od komentarja. Prav tako ne bomo skrivali, ko odgovora ne poznamo.

Mediji niso nad nikomer, tudi nad sabo ne. Edini način, da si zaslužimo zaupanje, je, da ga vsak dan znova pošteno prislužimo.""",
    },
    {
        "slug": "glasbena-nagrada-mlada-pevka",
        "title": "Glasbena nagrada za mlado slovensko pevko",
        "deck": "Njen singel je v enem mesecu presegel milijon predvajanj, kritiki pa hvalijo besedilo.",
        "category": "zabava",
        "author": "Nika Svetlin",
        "cover": 11,
        "tags": ["glasba", "nagrada", "singel"],
        "featured": False,
        "views": 2450,
        "minutes": 2,
        "published": "2026-11-08T17:25:00",
        "body": """Mlada slovenska pevka je na glasbeni podelitvi prejela nagrado za najboljši singel leta. Njena skladba je v enem mesecu presegla milijon predvajanj na spletnih platformah.

Kritiki so pohvalili predvsem besedilo, ki na preprost način govori o odraščanju in izgubi. Pevka je nagrado posvetila svoji ekipi in družini.

»Nisem pričakovala, da bo pesem tako odmevala. To je zgodba, ki sem jo napisala v sobi,« je dejala. Po podelitvi je napovedala novo turnejo po Sloveniji.

Njen album naj bi izšel prihodnjo pomlad. Prvi koncert bo v Ljubljani, sledili pa bodo nastopi v Mariboru, Kopru in Celju.""",
    },
    {
        "slug": "dusevno-zdravje-mladih-centri",
        "title": "Duševno zdravje mladih: novi centri po Sloveniji",
        "deck": "Ministrstvo bo vzpostavilo pet svetovalnih centrov za mlade od 12. do 25. leta.",
        "category": "zdravje",
        "author": "dr. Petra Vovk",
        "cover": 3,
        "tags": ["duševno zdravje", "mladi", "centri"],
        "featured": False,
        "views": 1870,
        "minutes": 3,
        "published": "2026-11-07T08:30:00",
        "body": """Ministrstvo za zdravje bo v prihodnjem letu vzpostavilo pet svetovalnih centrov za duševno zdravje mladih. Centri bodo namenjeni mladim od 12. do 25. leta in bodo nudili brezplačno svetovanje.

Po besedah ministrstva bodo centri delovali v Ljubljani, Mariboru, Celju, Kopru in Novem mestu. V vsakem bodo zaposleni psihologi, socialni delavci in po potrebi psihiatri.

»Želimo skrajšati pot do pomoči in zmanjšati stigma,« je dejala predstavnica ministrstva. Mladi se bodo lahko naročili sami, brez napotnice.

Strokovnjaki pozdravljajo pobudo, a opozarjajo, da bo treba poskrbeti za dovolj usposobljenega kadra. Povprečna čakalna doba za psihoterapijo je v nekaterih regijah še vedno več mesecev.""",
    },
    {
        "slug": "kibernetska-varnost-podjetja-tarca",
        "title": "Kibernetska varnost: slovenska podjetja pogosteje tarča napadov",
        "deck": "Najpogostejši so napadi z izsiljevalsko programsko opremo in lažna e-poštna sporočila.",
        "category": "tehnologija",
        "author": "Jure Oman",
        "cover": 12,
        "tags": ["kibernetska varnost", "podjetja", "napadi"],
        "featured": False,
        "views": 1730,
        "minutes": 3,
        "published": "2026-11-06T12:40:00",
        "body": """Slovenska podjetja so v zadnjem letu zabeležila več kibernetskih napadov kot leto prej. Najpogostejši so napadi z izsiljevalsko programsko opremo, lažna e-poštna sporočila in zlorabe ukradenih gesel.

Po podatkih nacionalnega odzivnega centra so najbolj ranljiva mala in srednja podjetja, ki pogosto nimajo zaposlenega strokovnjaka za varnost. Napadalci izkoriščajo tudi slabo posodobljene sisteme.

»Varnost ni projekt, ampak vsakodnevna praksa,« je dejal strokovnjak. Priporoča večfaktorsko prijavo, redne varnostne kopije in usposabljanje zaposlenih.

Podjetja lahko prijavo napada oddajo nacionalnemu odzivnemu centru, ki nudi pomoč pri omejevanju škode. Letos so obravnavali več kot 300 incidentov.""",
    },
    {
        "slug": "lokalne-volitve-2026-spremljamo",
        "title": "Lokalne volitve 2026: spremljamo dogajanje",
        "deck": "V živo spremljamo volilno nedeljo, odzive kandidatov in prve neuradne izide.",
        "category": "slovenija",
        "author": "Uredništvo",
        "cover": 1,
        "tags": ["volitve", "lokalne volitve", "župani"],
        "featured": False,
        "live": True,
        "views": 8210,
        "minutes": 5,
        "published": "2026-11-12T08:00:00",
        "body": """Dobrodošli v neposrednem prenosu volilne nedelje. Spremljamo dogajanje po vsej Sloveniji, odzive kandidatov in prve neuradne izide.

Volišča so se odprla ob 7. uri. Po podatkih volilne komisije je do 11. ure glasovalo približno 18 odstotkov volivcev, kar je nekoliko več kot na prejšnjih lokalnih volitvah.

V večjih mestih pričakujejo tesno tekmo. V Ljubljani, Mariboru in Kopru so kandidati zadnje dni stavili predvsem na neposredne stike z volivci.

Prve neuradne izide pričakujemo po 19. uri, ko se volišča zaprejo. Sledili bomo odzivom in morebitnemu drugemu krogu.""",
    },
]


def _cover(index: int) -> str:
    return f"/assets/img/covers/cover-{index}.svg"


def _parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def seed_database(db: Session) -> None:
    """Create categories, the admin user and demo articles on first run."""

    if db.scalar(select(func.count()).select_from(Category)) == 0:
        for slug, name, color, description, sort in CATEGORIES:
            db.add(
                Category(
                    slug=slug,
                    name=name,
                    color=color,
                    description=description,
                    sort=sort,
                    in_nav=True,
                )
            )
        db.commit()

    if db.scalar(select(func.count()).select_from(AdminUser)) == 0:
        db.add(
            AdminUser(
                email=settings.admin_email,
                name="Glavni urednik",
                password_hash=hash_password(settings.admin_password),
            )
        )
        db.commit()

    defaults = {
        "site_name": settings.site_name,
        "site_tagline": settings.site_tagline,
        "site_email": settings.site_email,
        "site_city": settings.site_city,
    }
    for key, value in defaults.items():
        if db.get(Setting, key) is None:
            db.add(Setting(key=key, value=value))
    db.commit()

    if db.scalar(select(func.count()).select_from(Article)) > 0:
        return

    for item in ARTICLES:
        body = item["body"].strip()
        words = len(body.split())
        db.add(
            Article(
                slug=item["slug"],
                title=item["title"],
                deck=item["deck"],
                body=body,
                category_slug=item["category"],
                author=item["author"],
                image_url=_cover(item["cover"]),
                image_caption="Ilustracija: Slovenec",
                tags=",".join(item["tags"]),
                status="published",
                is_featured=item.get("featured", False),
                is_breaking=item.get("breaking", False),
                is_live=item.get("live", False),
                views=item.get("views", 0),
                reading_minutes=max(1, round(words / 200)),
                published_at=_parse_date(item["published"]),
                created_at=_parse_date(item["published"]),
                updated_at=_parse_date(item["published"]),
            )
        )
    db.commit()
