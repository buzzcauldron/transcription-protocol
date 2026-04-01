# Benchmark images (not committed)

## BM-MED-001

Download a folio image from the Walters Art Museum open-access collection for [MS W.25](https://art.thewalters.org/detail/37603) (or the current catalogue URL for W.25). Save as:

`benchmark/images/BM-MED-001/folio.jpg`

The stress runner skips `BM-MED-001` if this file is missing unless you pass `--include-optional`.

## BM-001

Images are fetched automatically from Library of Congress IIIF URLs listed in `benchmark/manifest.yaml`.

## BM-CROP

Optional benchmark for **binding-edge / scan crop** behavior (`[crop]` token). Add a suitable page image at:

`benchmark/images/BM-CROP/page.jpg`

The stress runner skips `BM-CROP` if the file is missing unless you pass `--include-optional`. See `benchmark/test-results/BM-CROP.md` for the adoption gate note.
