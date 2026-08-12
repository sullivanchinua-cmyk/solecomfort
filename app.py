"""
SoleComfort - Live Search Shoe Store
Type any keyword → pinscrape fetches real images → products appear automatically
"""

from flask import Flask, render_template_string, request, jsonify
from pinscrape import Pinterest
import os
import time
import random
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Store scraped results in memory (simple cache)
search_cache = {}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>SoleComfort — Live Search</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #1a1a1a;
      --accent: #c9a87c;
      --bg: #faf8f5;
      --card: #ffffff;
      --text: #333;
      --muted: #777;
      --radius: 16px;
      --shadow: 0 10px 30px rgba(0,0,0,0.08);
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      min-height: 100vh;
    }

    header {
      background: var(--primary);
      color: white;
      padding: 1rem 5%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 2px 20px rgba(0,0,0,0.15);
    }
    .logo {
      font-family: 'Playfair Display', serif;
      font-size: 1.6rem;
      font-weight: 700;
    }
    .logo span { color: var(--accent); }

    .search-box {
      display: flex;
      gap: 0.5rem;
      flex: 1;
      max-width: 520px;
      margin: 0 1.5rem;
    }
    .search-box input {
      flex: 1;
      padding: 0.7rem 1.2rem;
      border: none;
      border-radius: 50px;
      font-size: 1rem;
      outline: none;
    }
    .search-box button {
      background: var(--accent);
      color: #1a1a1a;
      border: none;
      padding: 0.7rem 1.4rem;
      border-radius: 50px;
      font-weight: 600;
      cursor: pointer;
      transition: 0.2s;
    }
    .search-box button:hover { background: #b8956a; }
    .search-box button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .cart-btn {
      background: var(--accent);
      color: #1a1a1a;
      border: none;
      padding: 0.55rem 1.1rem;
      border-radius: 50px;
      font-weight: 600;
      cursor: pointer;
    }

    /* Hero / Status */
    .status-area {
      text-align: center;
      padding: 2.5rem 5% 1rem;
    }
    .status-area h1 {
      font-family: 'Playfair Display', serif;
      font-size: 2.2rem;
      margin-bottom: 0.5rem;
    }
    .status-area p { color: var(--muted); }
    .loading {
      display: none;
      margin-top: 1.5rem;
      font-weight: 500;
      color: var(--accent);
    }
    .loading.show { display: block; }
    .spinner {
      display: inline-block;
      width: 22px;
      height: 22px;
      border: 3px solid #eee;
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      vertical-align: middle;
      margin-right: 8px;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* Products */
    .section { padding: 1.5rem 5% 4rem; }
    .products-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 1.8rem;
    }
    .product-card {
      background: var(--card);
      border-radius: var(--radius);
      overflow: hidden;
      box-shadow: var(--shadow);
      transition: transform 0.3s, box-shadow 0.3s;
      animation: fadeIn 0.5s ease;
    }
    .product-card:hover {
      transform: translateY(-8px);
      box-shadow: 0 20px 40px rgba(0,0,0,0.12);
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(15px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .product-img {
      width: 100%;
      height: 240px;
      object-fit: cover;
      background: #f0ece6;
    }
    .product-info { padding: 1.2rem 1.3rem 1.4rem; }
    .product-info h3 {
      font-size: 1.1rem;
      font-weight: 600;
      margin-bottom: 0.25rem;
    }
    .category {
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 0.7rem;
    }
    .price-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .price {
      font-size: 1.2rem;
      font-weight: 700;
    }
    .price s {
      font-size: 0.85rem;
      color: #aaa;
      font-weight: 400;
      margin-left: 0.35rem;
    }
    .add-btn {
      background: var(--primary);
      color: white;
      border: none;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      font-size: 1.2rem;
      cursor: pointer;
      transition: 0.2s;
    }
    .add-btn:hover { background: var(--accent); color: #1a1a1a; }

    .empty-state {
      text-align: center;
      padding: 4rem 1rem;
      color: var(--muted);
    }
    .empty-state h3 { margin-bottom: 0.5rem; color: #555; }

    footer {
      background: var(--primary);
      color: #aaa;
      text-align: center;
      padding: 1.8rem 5%;
      font-size: 0.9rem;
    }
    footer a { color: var(--accent); }

    @media (max-width: 700px) {
      header { flex-wrap: wrap; gap: 0.8rem; }
      .search-box { order: 3; max-width: 100%; margin: 0; width: 100%; }
      .status-area h1 { font-size: 1.7rem; }
    }
  </style>
</head>
<body>
  <header>
    <div class="logo">Sole<span>Comfort</span></div>
    
    <form class="search-box" id="searchForm" onsubmit="return doSearch(event)">
      <input type="text" id="keyword" placeholder="Search anything... e.g. red slippers, nike shoes, sandals" required autocomplete="off">
      <button type="submit" id="searchBtn">Search</button>
    </form>

    <button class="cart-btn">🛒 <span id="cartCount">0</span></button>
  </header>

  <div class="status-area">
    <h1 id="title">Find Your Perfect Pair</h1>
    <p id="subtitle">Type any search word above — real images will be collected automatically</p>
    <div class="loading" id="loading">
      <span class="spinner"></span> Collecting images from Pinterest...
    </div>
  </div>

  <section class="section">
    <div class="products-grid" id="grid">
      <div class="empty-state">
        <h3>Start searching</h3>
        <p>Enter a keyword like "women slippers", "men sneakers", "beach sandals"...</p>
      </div>
    </div>
  </section>

  <footer>
    Powered by <strong>pinscrape</strong> · Images collected live from Pinterest
  </footer>

  <script>
    let cart = 0;
    const names = [
      "Classic Comfort", "Cloud Soft", "Urban Slide", "Cozy Mule",
      "Everyday Essential", "Luxe Shearling", "Minimalist Step", "Plush Indoor",
      "Street Style", "Relax Mode", "All-Day Wear", "Soft Touch"
    ];
    const categories = ["Women's", "Men's", "Unisex", "Home Wear", "Outdoor", "Casual"];

    async function doSearch(e) {
      e.preventDefault();
      const keyword = document.getElementById('keyword').value.trim();
      if (!keyword) return false;

      const btn = document.getElementById('searchBtn');
      const loading = document.getElementById('loading');
      const grid = document.getElementById('grid');
      const title = document.getElementById('title');
      const subtitle = document.getElementById('subtitle');

      btn.disabled = true;
      btn.textContent = "Searching...";
      loading.classList.add('show');
      grid.innerHTML = '';
      title.textContent = `Searching: "${keyword}"`;
      subtitle.textContent = "Collecting matching products...";

      try {
        const res = await fetch('/search?q=' + encodeURIComponent(keyword));
        const data = await res.json();

        if (data.error) {
          title.textContent = "Something went wrong";
          subtitle.textContent = data.error;
          grid.innerHTML = `<div class="empty-state"><h3>Try another keyword</h3><p>Pinterest sometimes blocks complex searches. Try simpler words.</p></div>`;
        } else if (!data.images || data.images.length === 0) {
          title.textContent = "No results";
          subtitle.textContent = `Nothing found for "${keyword}"`;
          grid.innerHTML = `<div class="empty-state"><h3>No images found</h3><p>Try a different search term</p></div>`;
        } else {
          title.textContent = `Results for "${keyword}"`;
          subtitle.textContent = `${data.images.length} products collected`;
          
          grid.innerHTML = data.images.map((img, i) => {
            const name = names[i % names.length] + " " + keyword.split(" ")[0];
            const cat = categories[i % categories.length];
            const price = (Math.random() * 40 + 25).toFixed(2);
            const old = (Math.random() > 0.4) ? (parseFloat(price) + Math.random()*20 + 10).toFixed(2) : null;
            
            return `
              <div class="product-card">
                <img class="product-img" src="${img}" alt="${name}" loading="lazy"
                     onerror="this.src='https://via.placeholder.com/400x300?text=Image'">
                <div class="product-info">
                  <h3>${name.charAt(0).toUpperCase() + name.slice(1)}</h3>
                  <div class="category">${cat}</div>
                  <div class="price-row">
                    <div class="price">
                      $${price}
                      ${old ? `<s>$${old}</s>` : ''}
                    </div>
                    <button class="add-btn" onclick="addToCart(this)">+</button>
                  </div>
                </div>
              </div>
            `;
          }).join('');
        }
      } catch (err) {
        title.textContent = "Connection error";
        subtitle.textContent = "Could not reach the server";
        grid.innerHTML = `<div class="empty-state"><h3>Error</h3><p>${err.message}</p></div>`;
      }

      btn.disabled = false;
      btn.textContent = "Search";
      loading.classList.remove('show');
      return false;
    }

    function addToCart(btn) {
      cart++;
      document.getElementById('cartCount').textContent = cart;
      btn.textContent = "✓";
      btn.style.background = "#4caf50";
      setTimeout(() => {
        btn.textContent = "+";
        btn.style.background = "";
      }, 700);
    }
  </script>
</body>
</html>
'''

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)


@app.route("/search")
def search():
    keyword = request.args.get("q", "").strip()
    if not keyword:
        return jsonify({"error": "Please enter a search keyword"})

    # Simple cache
    if keyword.lower() in search_cache:
        return jsonify({"images": search_cache[keyword.lower()], "cached": True})

    try:
        p = Pinterest(sleep_time=1.5)
        # Try the keyword, fallback to simpler version if it fails
        images = []
        try:
            images = p.search(keyword, 12)
        except Exception:
            # Fallback: take first 1-2 words only
            short = " ".join(keyword.split()[:2])
            try:
                images = p.search(short, 10)
            except Exception:
                # Last resort
                images = p.search(keyword.split()[0], 8)

        # Convert to strings
        image_urls = [str(u) for u in images if u]

        # Cache it
        search_cache[keyword.lower()] = image_urls

        return jsonify({
            "keyword": keyword,
            "count": len(image_urls),
            "images": image_urls
        })

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*50)
    print("  SoleComfort Live Search is running!")
    print(f"  Port: {port}")
    print("="*50 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)