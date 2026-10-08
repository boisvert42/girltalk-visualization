# Girltalk Visualization

An interactive timeline visualization of samples used in Girl Talk's mashup albums, specifically *All Day* and *Feed the Animals*.

Originally created by Matthew Adereth to generate [All Day by Girl Talk, Annotated](http://adereth.github.io/oneoff/girltalk-v2/).

---

## How It Works

1. **Tracklist Parsing (`src/girltalk/tracklist.clj`):**
   * Uses [Instaparse](https://github.com/Engelberg/instaparse) to parse sample breakdown markdown files (`data/AllDay.md`, `data/FeedTheAnimals.md`).
   * Computes cumulative running timestamps across continuous mix tracks and collapses samples that bridge track boundaries.

2. **Dataset Generation (`src/girltalk/vizdata.clj`):**
   * Computes active sample sets for each point in time across the album.
   * Assigns visual display slots (0–7) so sample cards don't collide.
   * Outputs JSON datasets (e.g., `resources/AllDaySamplesWithSets.json`).

3. **Interactive Frontend (`resources/index.html`):**
   * Uses D3.js (v3) to draw a 2D timeline plotting sample year against playback time.
   * Interactively seeks and highlights active samples as audio plays.
   * Uses native HTML5 `<audio>` for playback and scrubber tracking.

---

## Running the Web Visualization

Because modern browsers block loading local JSON files over `file://` (due to CORS security policies), you must serve the files with a local HTTP server:

```bash
# From the repository root:
python3 -m http.server 8000
```

Then open your browser to:
[http://localhost:8000/resources/](http://localhost:8000/resources/)

*(Alternatively, you can `cd resources && python3 -m http.server 8000` and visit `http://localhost:8000/`)*.

### Deploying to GitHub Pages
An automated GitHub Actions workflow (`.github/workflows/deploy.yml`) is set up to publish the visualization automatically on every push:

1. In your repository on GitHub, go to **Settings** > **Pages**.
2. Under **Build and deployment > Source**, select **GitHub Actions**.
3. Push your commits to `master` (or `main`):
   ```bash
   git add .
   git commit -m "Deploy to GitHub Pages"
   git push origin master
   ```
4. The workflow will automatically publish the contents of `resources/` directly to the root of your GitHub Pages site (`https://<username>.github.io/<repository>/`), fully supporting audio seeking and byte-range requests.

---

## Audio Support

The visualization uses the HTML5 `<audio>` element with native seeking and time synchronization. It looks for the continuous, seamless album audio in the `resources/` directory:

* `resources/allday.ogg` (recommended: ~47 MB, fits comfortably within GitHub file limits)
* `resources/allday.mp3` (fallback)

---

## License

### Code
Copyright © 2014 Matthew Adereth  
All code is distributed under the [Eclipse Public License v1.0](http://www.eclipse.org/legal/epl-v10.html) or (at your option) any later version.

### Data
All data files (`*.md`, `*.edn`, `*.json`) are licensed under the [Creative Commons Attribution-ShareAlike 3.0 Unported License (CC BY-SA 3.0)](https://creativecommons.org/licenses/by-sa/3.0/).  
* The `AllDay.md` and `FeedTheAnimals.md` tracklists were sourced from `http://www.illegal-tracklist.net/`.

### Audio
*All Day* by [Girl Talk](http://en.wikipedia.org/wiki/Girl_Talk_(musician)) was released in 2010 on [Illegal Art](http://illegal-art.net/allday/) and is distributed under the [Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported License (CC BY-NC-ND 3.0)](https://creativecommons.org/licenses/by-nc-nd/3.0/).
