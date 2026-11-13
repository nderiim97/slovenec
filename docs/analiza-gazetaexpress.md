# Analiza e gazetaexpress.com — bazë për portalin "Slovenec"

Kjo analizë është bërë lokalisht (local reverse) mbi faqen publike
<https://www.gazetaexpress.com/> më 12. 11. 2026. Nuk është kopjuar kod, CSS,
logo apo përmbajtje; janë nxjerrë vetëm modelet e strukturës dhe të dizajnit.

## 1. Platforma

| Të dhënë | Vlera |
| --- | --- |
| CMS | WordPress 6.4.2 |
| Temë | `express6` |
| CSS bazë | Bootstrap 4 + `mainStyle.css` e temës |
| Fontet | Raleway (Black / ExtraBold / SemiBold) + system-ui |
| Ngarkimi | jQuery, Owl Carousel, Slick (Top Stories) |
| Reklamat | `mandeta-ad` blloqe (leaderboard, katror, in-page) |

## 2. Struktura e faqes kryesore

```
header.header                     → shirit i kuq me logo dhe menu
main.main
  .block.topstories              → hero / karusel "Top Stories"
  .block.oped                    → 3 kolona opinion
  .block.t7videos                → video / TV
  .block.morenews                → "Më të fundit" + tab "Më të lexuarat"
  .block (rubrika)               → 4 kolona lajmesh për çdo rubrikë
footer.footer                     → i zi, kolona me lidhje
```

Përsëritjet kryesore:

- **Hero**: imazh i madh, titull i bardhë UPPERCASE i mbivendosur (`box__title-background`)
- **Kartela**: imazh lart, titull i zi `box__title`, rubrika e kuqe sipër
- **Blloqe rubrikash**: titull i kuq `block__title` + vijë, pastaj grid
- **Top Stories / LIVE / Më të lexuarat** si seksione të veçanta
- **Reklama** të pozicionuara midis blloqeve

## 3. Dizajn-tokens të nxjerra

| Token | Vlera |
| --- | --- |
| Ngjyra primare | `#ED1D24` (header, tituj rubrikash, linja) |
| Teksti | `#000000` / `#212529` |
| Sfond | `#FFFFFF` |
| Footer | `#000000` |
| Font titujsh | Raleway, 700–900 |
| Font teksti | system-ui / Segoe UI |
| Titull rubrike | 22 px, i kuq, uppercase, bold |
| Titull kartele | 14 px, 600, hapësirë shkronjash -0.2 px |
| Hero titull | 22 px, i bardhë, uppercase, ExtraBold |

## 4. Navigimi (i përshtatur për tregun slovene)

| Gazeta Express | Slovenec |
| --- | --- |
| Lajme | Slovenija |
| Shqiperi | Svet |
| Maqedoni | Gospodarstvo |
| Op/Ed | Mnenja |
| Sport | Šport |
| Roze | Zabava |
| Arte | Kultura |
| AutoTech | Tehnologija |
| Fun / Shneta | Zdravje |
| — | Kronika |

## 5. Çka u riprodhua në "Slovenec"

- Header i kuq me masthead, datë, mot dhe nav sticky
- Hero me titull të bardhë mbi imazh + lajme dytësore anash
- Blloqe rubrikash me titull të kuq uppercase dhe grid 4-kolonaš
- "Najnovejše" (më të fundit), "Najbolj brano" (më të lexuara), "LIVE"
- Kartela me rubrikë, titull, kohë leximi dhe datë
- Footer i zi me kolona
- Reklama: pozicione të gatshme (`ad-slot`) pa tracking të jashtëm

## 6. Çka u shtua (jo në original)

- CMS real: FastAPI + SQLAlchemy + SQLite/Postgres
- Admin panel me login, CRUD artikujsh, kategorive dhe cilësimeve
- SEO: meta tags server-side, sitemap.xml, robots.txt, Open Graph
- Kërkim i brendshëm, faqe rubrike me paginim, artikull me të ngjashme
- Pa varësi nga jashtë: pa Google Fonts, pa jQuery, pa tracker

## 7. Kufizime

- Të gjithë artikujt, autorët dhe ngjarjet në demo janë **fiction**.
- Imazhet janë SVG abstrakte të gjeneruara lokalisht, pa të drejta të treta.
- Marka "Slovenec" është emër pune; ndryshohet në admin → Nastavitve
  (parazgjedhja është në `server/config.py`).
