# 591 租屋通知機器人

定期依照你設定好的 591 搜尋條件抓取新物件，有新的就用 Telegram 通知你，並提供一個網頁可以隨時瀏覽目前的物件清單，不用每次開 591 App 重設篩選條件。

## 運作方式

- GitHub Actions 每 45 分鐘自動執行一次爬蟲
- 爬到的完整物件清單會寫進 `docs/listings.json`，由 GitHub Pages 顯示成網頁
- 跟上次比對後的「新物件」會透過 Telegram Bot 推播訊息給你
- 591 若改版導致爬蟲失效，Actions 執行會顯示失敗（紅叉），並嘗試推播一則失敗通知

## 設定步驟

### 1. 取得你的 591 搜尋網址

1. 到 [rent.591.com.tw](https://rent.591.com.tw/) 設定好你要的區域、價格、房型等篩選條件，按搜尋
2. 把瀏覽器網址列上「完整的」搜尋結果網址複製下來（等一下會貼到 GitHub Secrets 的 `SEARCH_URL`）

### 2. 建立 Telegram Bot

1. 在 Telegram 搜尋 [@BotFather](https://t.me/BotFather)，傳送 `/newbot`，依指示取名字，完成後會拿到一組 **Bot Token**（長得像 `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）
2. 用 Telegram 搜尋你剛建立的 Bot，傳送任意訊息給它（例如「hi」），讓它知道你的存在
3. 瀏覽器打開 `https://api.telegram.org/bot<你的TOKEN>/getUpdates`（把 `<你的TOKEN>` 換成上面拿到的 token），在回傳的 JSON 裡找 `"chat":{"id":123456789,...}`，那個數字就是你的 **Chat ID**

### 3. 建立 GitHub Repo 並上傳這個專案

在 [github.com/new](https://github.com/new) 建立一個新的**空**（不要初始化 README/gitignore）**Public** repo，例如叫 `591-watcher`，然後在這個資料夾執行：

```bash
cd 591-watcher
git remote add origin https://github.com/<你的帳號>/591-watcher.git
git branch -M main
git push -u origin main
```

### 4. 設定 GitHub Secrets

到 repo 頁面 → **Settings → Secrets and variables → Actions → New repository secret**，新增以下三個：

| Name | Value |
|---|---|
| `SEARCH_URL` | 步驟 1 複製的搜尋網址 |
| `TELEGRAM_BOT_TOKEN` | 步驟 2 拿到的 Bot Token |
| `TELEGRAM_CHAT_ID` | 步驟 2 拿到的 Chat ID |

### 5. 開啟 GitHub Pages

到 repo 頁面 → **Settings → Pages** → Source 選擇 **Deploy from a branch** → Branch 選 `main`、資料夾選 `/docs` → Save。

儲存後過幾分鐘，頁面會顯示你的網址，通常是 `https://<你的帳號>.github.io/591-watcher/`。

### 6. 手動測試一次

到 repo 頁面 → **Actions** → 左側選 **591 Watcher** → 右側 **Run workflow** 按鈕手動觸發一次，確認：
- 這次執行是綠色勾勾（成功）
- 有收到 Telegram 訊息（如果搜尋條件真的有物件的話）
- 打開 Pages 網址能看到物件清單

之後就會照 `.github/workflows/watch.yml` 裡設定的排程（預設每 45 分鐘）自動執行，不用再手動做任何事。

## 常用調整

- **改排程頻率**：編輯 `.github/workflows/watch.yml` 裡的 `cron: "*/45 * * * *"`，例如改成 `*/30 * * * *`（30 分鐘）或 `0 * * * *`（每小時）
- **改搜尋條件**：直接去 GitHub repo 的 Secrets 更新 `SEARCH_URL` 的值即可，不需要改程式碼

## 本機測試

需要 Python 3.9+ 跟 **Node.js**（爬蟲用 Node 來解析 591 頁面裡內嵌的資料，見下方「運作原理」）。macOS 可以用 `brew install node` 安裝。

```bash
cd 591-watcher
pip install -r requirements.txt
export SEARCH_URL="你的591搜尋網址"
export TELEGRAM_BOT_TOKEN="你的bot token"
export TELEGRAM_CHAT_ID="你的chat id"
python -m src.main
```

若缺少任何環境變數，程式會直接印出缺少哪個變數並結束，不會產生誤導性的錯誤。

## 運作原理

591 現在把搜尋結果（標題、價格、坪數、連結…）直接內嵌在頁面 HTML 裡的一段 `window.__NUXT__=(function(...){...})(...)` 腳本中，而不是走一個乾淨的公開 JSON API。`src/scraper.py` 抓下頁面後，會把這段腳本丟給 `scripts/decode_nuxt.js`（用 Node 在一個模擬的 `window` 環境下執行它），還原出真正的資料物件，再取出 `pinia['rent-list']['dataList']` 裡的物件清單。分頁靠網址上的 `firstRow` 參數，排序則預設用 `order=posttime&orderType=desc`（最新的排最前面）。

## 故障排除

若 Actions 執行失敗（Actions 頁面顯示紅叉），代表 591 網站的頁面結構可能又改版了，導致爬蟲抓不到預期的資料。可以：

1. 點進失敗的那次執行紀錄，看 log 裡 `Scrape failed: ...` 的錯誤訊息（會標明是哪個環節壞的：找不到內嵌的 `__NUXT__` 資料、HTTP 非 200、還是內部欄位結構變了）
2. 依錯誤訊息去看對應的檔案：
   - 找不到 `__NUXT__` 資料、或 Node 解析失敗 → `src/scraper.py`、`scripts/decode_nuxt.js`
   - 欄位對應錯誤（例如標題、價格抓成空的） → `src/parser.py`
3. 修好後 push 上去，下次排程就會自動恢復正常，不用做其他事

## 專案結構

```
591-watcher/
├── src/            # 爬蟲程式（Python）
├── data/           # 已通知過的物件 id（程式自動維護，不用手動改）
├── docs/           # GitHub Pages 網頁（listings.json 由程式自動更新）
└── .github/workflows/watch.yml   # 排程設定
```
