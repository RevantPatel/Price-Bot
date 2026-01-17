# 📉 Amazon Price Tracker Bot

> **Never miss a price drop again.** A high-performance, asynchronous Telegram bot that monitors Amazon products and notifies you instantly when prices fall.

<p align="center">
  <img src="assets/bot_qr.png" alt="Scan to Chat with Bot" width="200"/>
  <br>
  <a href="https://t.me/HAWKEYE_PRICEBOT"><strong>Click to Chat with Bot (@HAWKEYE_PRICEBOT)</strong></a>
</p>

---

## ✨ Features

-   **⚡ Real-Time Tracking**: Automatically checks prices every 30 minutes.
-   **📉 Price Drop Alerts**: Get notified with the exact price difference (e.g., `Diff: -₹500.00`).
-   **🛡️ Smart Validation**: Automatically cleans URLs to store only canonical links (`/dp/ASIN`).
-   **🚫 Duplicate Prevention**: Prevents tracking the same product twice.
-   **🚀 Scalable Architecture**: Uses streaming database cursors to handle thousands of products without memory leaks.
-   **📱 User-Friendly**: Simple commands (`/start`, `/list`, `/stop_ID`).

---

## 🚀 Getting Started

### Prerequisites
-   Python 3.8 or higher.
-   A Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather)).

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/price-bot.git
    cd price-bot
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file in the root directory and add your token:
    ```env
    TELEGRAM_TOKEN=your_telegram_bot_token_here
    ```

4.  **Run the Bot**
    ```bash
    python bot.py
    ```

---

## 📖 Usage

### 1. Start Tracking
Simply paste any Amazon product link into the chat:
> **User:** `https://www.amazon.in/dp/B08L5TNJHG`
>
> **Bot:** `✅ Tracking Started! iPhone 13... Price: ₹49,999`

### 2. View Watchlist
Use the `/list` command to see all tracked items:
> **User:** `/list`
>
> **Bot:** 
> `🆔 1 | ₹49,999`
> `iPhone 13 (128GB)...`
> `/stop_1`

### 3. Stop Tracking
Click the command shown in the list or type it manually:
> **User:** `/stop_1`
>
> **Bot:** `🗑️ Item 1 deleted.`

---

## 🛠️ Tech Stack

-   **Core**: Python 3, `asyncio`
-   **Bot Framework**: `python-telegram-bot`
-   **Database**: SQLite (`aiosqlite`)
-   **Scraping**: `curl_cffi` (Impersonates Chrome to bypass bot detection), `BeautifulSoup4`

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---