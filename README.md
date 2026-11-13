# Slovenec — slovenski novičarski portal

Demo novičarski portal, narejen po vzoru velikih regionalnih portalov
(analiza: [`docs/analiza-gazetaexpress.md`](docs/analiza-gazetaexpress.md)).
Vsebuje javni portal in uredniški sistem (CMS) z bazo, prijavo in urejanjem
člankov. Vsi članki, avtorji in dogodki v demo podatkih so **izmišljeni**.

## Hitri začetek

```powershell
cd slovenec
pip install -r server/requirements.txt
copy .env.example .env
python -m uvicorn server.main:app --reload --port 8000
```

Odprite <http://127.0.0.1:8000>. Uredniški sistem je na
<http://127.0.0.1:8000/admin>.

Privzeti dostop (spremenite v `.env`):

| | |
| --- | --- |
| E-pošta | `admin@slovenec.local` |
| Geslo | `slovenec123` |

Ob prvem zagonu se ustvari baza `server/slovenec.db`, uvozi 10 kategorij in
25 demo člankov ter ustvari skrbniški račun.

## Kaj je vključeno

**Javni del**

- domača stran: hero, najnovejše, rubrike, najbolj brano, mnenja, LIVE
- rubrike z paginacijo (`/rubrika/{slug}`)
- članek z avtorjem, berljivostjo, deljenjem, sorodnimi članki in navigacijo
- iskanje po naslovu, povzetku, vsebini in ključnih besedah
- stran “V živo”
- odziven dizajn (mobile-first), brez zunanjih pisav in sledenja
- SEO: meta oznake strežniško, Open Graph, JSON-LD `NewsArticle`,
  `sitemap.xml`, `robots.txt`

**Uredniški sistem**

- prijava z e-pošto in geslom (scrypt + podpisana piškotna seja)
- nadzorna plošča s statistiko in hitro objavo: izberi rubriko, odpri
  urejevalnik in objavi ali shrani osnutek
- CRUD člankov: naslov, slug, povzetek, besedilo, kategorija, avtor,
  slika, ključne besede, status (objavljeno/osnutek), izpostavljeno,
  “zadnje”, “v živo”, datum objave
- upravljanje kategorij (ime, slug, barva, opis, vrstni red)
- nastavitve portala (ime, slogan, e-pošta, mesto); sprememba imena takoj
  posodobi glavo, nogo in uredniški sistem

## Struktura

```text
slovenec/
├── index.html, category.html, article.html,
│   search.html, live.html, 404.html      javne strani (strežniško polnjen SEO)
├── admin.html                            uredniški sistem
├── assets/
│   ├── css/style.css                     celoten dizajn sistem
│   ├── js/app.js                         skupne funkcije + chrome
│   ├── js/pages.js                       render javnih strani
│   ├── js/admin.js                       CMS logika
│   └── img/covers/*.svg                  lokalne ilustracije
├── server/
│   ├── main.py                           FastAPI: strani + API
│   ├── models.py                         Article, Category, AdminUser, Setting
│   ├── security.py                       gesla, seja, throttling
│   ├── seed.py                           demo vsebina
│   └── config.py                         okolje in nastavitve
├── tools/
│   ├── build_pages.py                    generira HTML iz skupne predloge
│   └── make_covers.py                    generira SVG naslovnice
└── docs/analiza-gazetaexpress.md         reverse-engineering analiza
```

## API (izbor)

| Metoda | Pot | Namen |
| --- | --- | --- |
| GET | `/api/site` | ime portala, kategorije, števci |
| GET | `/api/home` | hero, najnovejše, rubrike, najbolj brano |
| GET | `/api/articles?category=&q=&limit=&offset=` | seznam člankov |
| GET | `/api/articles/{slug}` | članek + sorodni + prejšnji/naslednji |
| POST | `/api/articles/{slug}/view` | števec branj |
| GET | `/api/live` | članki v živo |
| POST | `/api/admin/login` | prijava |
| GET/POST/PUT/DELETE | `/api/admin/articles` | CRUD člankov |
| GET/POST/PUT/DELETE | `/api/admin/categories` | CRUD kategorij |
| GET/PUT | `/api/admin/settings` | nastavitve |

Interaktivna dokumentacija: <http://127.0.0.1:8000/docs>.

## Produkcija

1. Nastavite `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` in `DATABASE_URL`
   (Postgres: `postgresql+psycopg://…`).
2. `APP_ENV=production` vklopi `secure` piškotke.
3. Zaženite za obratnim proxyjem:

```powershell
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --workers 2
```

Primer `Procfile` za Render/Heroku:

```text
web: uvicorn server.main:app --host 0.0.0.0 --port $PORT
```

## Razvoj

```powershell
# znova zgradi HTML strani iz predloge
python tools/build_pages.py

# znova ustvari SVG naslovnice
python tools/make_covers.py

# preveri sintakso
python -m compileall -q server tools
```

## Opombe

- Demo ne pošilja e-pošte in ne uporablja zunanjih analitik.
- Ilustracije so generirane lokalno (SVG), brez tujih avtorskih pravic.
- Pred javno objavo zamenjajte demo vsebino, nastavite pravo geslo in
  preverite pravne strani (impresum, zasebnost, piškotki).
