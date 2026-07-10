async function main() {
  const updatedAtEl = document.getElementById("updated-at");
  const container = document.getElementById("listings");
  const emptyStateEl = document.getElementById("empty-state");

  let data;
  try {
    const res = await fetch("./listings.json", { cache: "no-store" });
    data = await res.json();
  } catch (err) {
    updatedAtEl.textContent = "無法載入物件清單";
    return;
  }

  updatedAtEl.textContent = data.updated_at ? `最後更新：${data.updated_at}` : "";

  const listings = data.listings || [];
  if (listings.length === 0) {
    emptyStateEl.hidden = false;
    return;
  }

  container.innerHTML = listings.map(cardHtml).join("");
}

function cardHtml(listing) {
  const image = listing.image_url
    ? `<img loading="lazy" src="${escapeAttr(listing.image_url)}" alt="">`
    : `<img loading="lazy" src="" alt="" style="display:none">`;
  return `<a class="card" href="${escapeAttr(listing.link)}" target="_blank" rel="noopener">
    ${image}
    <div class="card-body">
      <div class="price">$${escapeHtml(listing.price)}</div>
      <div class="title">${escapeHtml(listing.title)}</div>
      <div class="meta">${escapeHtml(listing.kind)} · ${escapeHtml(listing.region_text)} · ${escapeHtml(listing.floor)}</div>
    </div>
  </a>`;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function escapeAttr(str) {
  return escapeHtml(str).replace(/"/g, "&quot;");
}

main();
