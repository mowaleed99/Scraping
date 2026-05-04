# Lost & Found AI-Scraper Backend 🚀

An intelligent, on-demand backend pipeline designed to scrape lost and found posts from Facebook, process them using Large Language Models (LLMs), and serve structured data to a .NET frontend/backend ecosystem.

---

## 🌟 Overview
This project solves the problem of unstructured and messy lost and found data on social media. It provides a clean, AI-powered bridge between Facebook groups and a searchable, structured application.

### **The Pipeline**
1.  **Scrape**: High-performance Facebook scraping via Apify.
2.  **Extract**: AI-driven entity extraction (Llama 3.1 via Groq) specifically tuned for Arabic dialects.
3.  **Store**: Relational storage in PostgreSQL with deduplication logic.
4.  **Serve**: Strongly typed FastAPI endpoints for external consumption.

---

## 🛠️ Tech Stack
*   **Language**: Python 3.12+
*   **API Framework**: FastAPI
*   **Database**: PostgreSQL (Neon Serverless)
*   **AI/LLM**: Groq (Llama 3.1 8B Instant)
*   **Scraping**: Apify SDK
*   **Deployment**: Modal (Serverless)
*   **ORM**: SQLAlchemy (Asyncio)

---

## 🚀 Key Features
*   **On-Demand Scraping**: Manually trigger scrapes via API to control costs and resources.
*   **Arabic Dialect Processing**: AI prompt engineering specifically designed to extract item details, locations, and phone numbers from Egyptian and Standard Arabic.
*   **Full Traceability**: Every record includes the original Facebook group name and direct post URL for verification.
*   **Harden for .NET**: Designed with strict JSON contracts, standard error responses, and Snake_Case to PascalCase compatibility for easy HttpClient integration.
*   **Deduplication**: Automatic checking to prevent duplicate posts from cluttering the database.

---

## 📡 API Endpoints

### `GET /posts`
Retrieves all processed items.
*   **Filters**: `type` (lost/found), `limit`, `offset`.
*   **Response**: List of structured post objects including metadata.

### `POST /scrape`
Triggers a live scraping and processing job.
*   **Params**: `limit` (max posts to fetch).
*   **Response**: Summary of scraped, processed, and skipped items.

### `GET /docs`
Interactive Swagger UI documentation.

---

## ⚙️ Setup & Installation

1.  **Clone the Repository**
2.  **Configure Environment**
    Create a `.env` file with the following:
    ```env
    DATABASE_URL=
    DATABASE_POOL_URL=
    GROQ_API_KEY=
    APIFY_API_TOKEN=
    API_SECRET_KEY=
    ```
3.  **Install Dependencies**
    ```bash
    pip install -e .
    ```
4.  **Run Locally**
    ```bash
    fastapi dev app/api/main.py
    ```
5.  **Deploy to Modal**
    ```bash
    modal deploy modal_app.py
    ```

---

## 📄 Documentation
For detailed instructions on how to integrate this backend with a **.NET / C#** application, please refer to:
👉 [MAIN_BACKEND_INTEGRATION.md](./MAIN_BACKEND_INTEGRATION.md)
