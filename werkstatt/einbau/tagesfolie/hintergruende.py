# 20) Zwei Hintergrund-Vorlagen im Stil der Eulenkiste / Klassenkiste (Teil von patch.py, nach patch2.py)
#   «Eulenkiste»: Himmelblau-Aquarell, Eule auf dem Ast, goldene Sterne ✦ ✧, Wölkchen
#   «Goldsterne»: warmes Papier, Sternen-Girlande oben, kleine Sterne am Rand
rep('''  klassenrat: { name: "Klassenrat",''', r'''  eulen: { name: "Eulenkiste", base: "radial-gradient(ellipse at 50% 40%,#fdfeff,#eef6fc)", fill: "#f4f9fd",
    theme: { title: "#3f78a8", blobs: ["#9fd0f3", "#f3d27a", "#a5cf98", "#eba7a0", "#c4a9e2", "#7fb6e0"], cal: ["#3f78a8", "#e6f2fc"] },
    draw(W, H){
      const s = Math.min(W, H), G = "#d6ad45";
      const cloud = (x, y, w, o) => `<g fill="#fff" opacity="${o}"><ellipse cx="${x}" cy="${y}" rx="${w * .5}" ry="${w * .16}"/><circle cx="${x - w * .16}" cy="${y - w * .08}" r="${w * .15}"/><circle cx="${x + w * .08}" cy="${y - w * .13}" r="${w * .2}"/><circle cx="${x + w * .3}" cy="${y - w * .03}" r="${w * .12}"/></g>`;
      const sp = edgeSpots(W, H, 26, 31, .2, .18);
      const stars = sp.map(([x, y, r], i) => i % 3 === 2 ? sternRand(x, y, s * (.012 + r * .012), G, r * 40) : stern(x, y, s * (.01 + r * .016), i % 4 ? G : "#f3d27a", r * 30)).join("");
      // Ast mit Eule unten links
      const by = H - s * .13, bx = s * .5;
      const ast = `<path d="M${-s * .02} ${by + s * .03}C${bx * .3} ${by - s * .01} ${bx * .6} ${by + s * .02} ${bx} ${by - s * .03}" stroke="#a07c5c" stroke-width="${s * .02}" stroke-linecap="round" fill="none"/>
        <path d="M${bx * .72} ${by}q${s * .05} ${-s * .03} ${s * .09} ${-s * .08}" stroke="#a07c5c" stroke-width="${s * .01}" stroke-linecap="round" fill="none"/>
        ${[[.2, .02, -30], [.38, -.005, 25], [.62, .012, -15], [.86, -.035, 30], [.95, -.07, -40]].map(([t, dy, rot], i) => `<ellipse cx="${bx * t}" cy="${by + s * dy - s * .03}" rx="${s * .022}" ry="${s * .045}" fill="${i % 2 ? "#a5cf98" : "#8fbf7f"}" transform="rotate(${rot} ${bx * t} ${by + s * dy - s * .03})" opacity=".9"/>`).join("")}`;
      const ox = bx * .48, oy = by - s * .1, u = s * .01;
      const eule = `<g>
        <path d="M${ox - 6.5 * u} ${oy - 7 * u}l${-1.5 * u} ${-5 * u}l${4.5 * u} ${3 * u}zM${ox + 6.5 * u} ${oy - 7 * u}l${1.5 * u} ${-5 * u}l${-4.5 * u} ${3 * u}z" fill="#a8916f"/>
        <ellipse cx="${ox}" cy="${oy}" rx="${8 * u}" ry="${9.5 * u}" fill="#c4ae8c"/>
        <ellipse cx="${ox - 7.2 * u}" cy="${oy + 2 * u}" rx="${2.6 * u}" ry="${6 * u}" fill="#a8916f" transform="rotate(12 ${ox - 7.2 * u} ${oy + 2 * u})"/>
        <ellipse cx="${ox + 7.2 * u}" cy="${oy + 2 * u}" rx="${2.6 * u}" ry="${6 * u}" fill="#a8916f" transform="rotate(-12 ${ox + 7.2 * u} ${oy + 2 * u})"/>
        <ellipse cx="${ox}" cy="${oy + 3 * u}" rx="${5 * u}" ry="${5.5 * u}" fill="#f1e6d2"/>
        ${[[-2, 1.5], [1.5, 2], [-1, 4.5], [2.5, 5], [0, 7]].map(([dx, dy]) => `<path d="M${ox + dx * u - u} ${oy + dy * u}q${u} ${u} ${2 * u} 0" stroke="#c4ae8c" stroke-width="${u * .5}" fill="none" stroke-linecap="round"/>`).join("")}
        <circle cx="${ox - 3.2 * u}" cy="${oy - 4 * u}" r="${3.4 * u}" fill="#fff" stroke="${G}" stroke-width="${u * .6}"/><circle cx="${ox + 3.2 * u}" cy="${oy - 4 * u}" r="${3.4 * u}" fill="#fff" stroke="${G}" stroke-width="${u * .6}"/>
        <circle cx="${ox - 2.8 * u}" cy="${oy - 3.8 * u}" r="${1.7 * u}" fill="#2b2f2c"/><circle cx="${ox + 2.8 * u}" cy="${oy - 3.8 * u}" r="${1.7 * u}" fill="#2b2f2c"/>
        <circle cx="${ox - 2.3 * u}" cy="${oy - 4.4 * u}" r="${.55 * u}" fill="#fff"/><circle cx="${ox + 3.3 * u}" cy="${oy - 4.4 * u}" r="${.55 * u}" fill="#fff"/>
        <path d="M${ox - 1.1 * u} ${oy - 1.6 * u}h${2.2 * u}l${-1.1 * u} ${2 * u}z" fill="#e0a43b"/>
        <path d="M${ox - 3 * u} ${oy + 9.2 * u}v${1.6 * u}M${ox - 1.6 * u} ${oy + 9.2 * u}v${1.6 * u}M${ox + 1.6 * u} ${oy + 9.2 * u}v${1.6 * u}M${ox + 3 * u} ${oy + 9.2 * u}v${1.6 * u}" stroke="#e0a43b" stroke-width="${u * .7}" stroke-linecap="round"/></g>`;
      return softBlobs(W, H, [[0, 1, .28, .32, "#bfe0f7", .6], [1, 0, .26, .3, "#cfe8fb", .55], [1, 1, .22, .26, "#f8e6b8", .45], [0, 0, .2, .22, "#e3f0e0", .45]]) +
        cloud(W * .1, H * .14, s * .2, .9) + cloud(W * .86, H * .78, s * .24, .85) + cloud(W * .9, H * .12, s * .14, .7) +
        stars + ast + eule;
    } },
  sterne: { name: "Goldsterne", base: "radial-gradient(ellipse at 50% 45%,#fffefa,#f8f3e6)", fill: "#fbf7ec",
    theme: { title: "#b5852a", blobs: ["#f3d27a", "#9fd0f3", "#eba7a0", "#a5cf98", "#c4a9e2", "#f3b37c"], cal: ["#c99a3b", "#fbf3dc"] },
    draw(W, H){
      const s = Math.min(W, H), C = ["#d6ad45", "#f3d27a", "#e2b84e", "#9fc8ea"];
      const sag = s * .045, y0 = s * .005, n = Math.max(11, Math.round(W / (s * .09)));
      const yAt = t => y0 + 4 * sag * t * (1 - t);
      let g = `<path d="M0 ${y0}Q${W / 2} ${y0 + 2 * sag} ${W} ${y0}" stroke="#c9b48a" stroke-width="2.5" fill="none"/>`;
      for (let i = 0; i < n; i++) { const t = (i + .5) / n, x = t * W, y = yAt(t), L = s * (.025 + ((i * 37) % 5) * .011), r = s * (.012 + ((i * 53) % 3) * .005), c = C[i % C.length];
        g += `<path d="M${x} ${y}v${L}" stroke="#c9b48a" stroke-width="1.5"/>` + (i % 4 === 3 ? sternRand(x, y + L + r, r, "#d6ad45", 0) : stern(x, y + L + r, r, c, 0)); }
      const sp = edgeSpots(W, H, 20, 57, .2, .3).filter(p => p[1] > H * .3);
      const deko = sp.map(([x, y, r], i) => i % 2 ? sternRand(x, y, s * (.01 + r * .012), "#d6ad45", r * 40) : stern(x, y, s * (.008 + r * .012), i % 3 ? "#e9c768" : "#9fc8ea", r * 30)).join("");
      return softBlobs(W, H, [[0, 1, .28, .3, "#f6e3b5", .6], [1, 1, .26, .3, "#d6e9f8", .55], [1, .3, .18, .25, "#f3d6d0", .4], [0, .35, .16, .22, "#e3efdc", .45]]) + g + deko;
    } },
  klassenrat: { name: "Klassenrat",''')
rep('''const HAND = `font-family="Patrick Hand,Comic Sans MS,cursive"`;''', '''const HAND = `font-family="Patrick Hand,Comic Sans MS,cursive"`;
// Stern wie ✦ (gefüllt) und ✧ (nur Umriss)
const sternPfad = r => `M0 ${-r}Q${r * .16} ${-r * .16} ${r} 0Q${r * .16} ${r * .16} 0 ${r}Q${-r * .16} ${r * .16} ${-r} 0Q${-r * .16} ${-r * .16} 0 ${-r}Z`;
const stern = (x, y, r, c, rot) => `<path d="${sternPfad(r)}" fill="${c}" transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${(rot || 0).toFixed(0)})"/>`;
const sternRand = (x, y, r, c, rot) => `<path d="${sternPfad(r)}" fill="none" stroke="${c}" stroke-width="${Math.max(1.2, r * .14).toFixed(1)}" stroke-linejoin="round" transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${(rot || 0).toFixed(0)})"/>`;''')
