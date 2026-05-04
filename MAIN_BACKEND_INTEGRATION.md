# Main Backend Integration Guide: Lost & Found AI-Scraper

This document provides technical instructions for the .NET Backend team to integrate with the Lost & Found Scraping service.

---

## 1. System Overview
This service is an automated pipeline that scrapes Facebook, extracts structured information from Arabic text using AI (Groq/Llama 3.1), and stores it in a central database.

**Base URL**: `https://mowaleed99--lost-found-backend-fastapi-server.modal.run`
**Interactive Docs**: `/docs` (Swagger UI)

---

## 2. API Endpoints

### **A. Get Processed Posts**
Fetches the latest structured items from the database.
- **Method**: `GET`
- **Path**: `/posts`
- **Query Params**:
  - `type`: (Optional) "lost" or "found"
  - `limit`: (Default: 20, Max: 50)
- **Response**: `List[PostResponse]`

### **B. Trigger Manual Scrape**
Forces the system to visit Facebook and look for new items immediately.
- **Method**: `POST`
- **Path**: `/scrape`
- **Query Params**:
  - `limit`: (Default: 10, Max: 30)
- **Response**: `ScrapeResponse`

---

## 3. .NET / C# Implementation

### **Response Model**
Use `[JsonPropertyName]` to map Python's `snake_case` to C# `PascalCase`.

```csharp
using System.Text.Json.Serialization;

public class PostResponse
{
    [JsonPropertyName("id")]
    public string Id { get; set; }

    [JsonPropertyName("type")]
    public string Type { get; set; }

    [JsonPropertyName("item")]
    public string? Item { get; set; }

    [JsonPropertyName("location")]
    public string? Location { get; set; }

    [JsonPropertyName("contact")]
    public string? Contact { get; set; }

    [JsonPropertyName("group_name")]
    public string? GroupName { get; set; }

    [JsonPropertyName("post_url")]
    public string? PostUrl { get; set; }

    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
}
```

### **Usage Example (HttpClient)**
```csharp
public async Task<List<PostResponse>> FetchDataFromScraper()
{
    using var client = new HttpClient();
    client.BaseAddress = new Uri("https://mowaleed99--lost-found-backend-fastapi-server.modal.run/");
    
    var response = await client.GetAsync("posts?limit=20");
    
    if (response.IsSuccessStatusCode)
    {
        var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
        return await response.Content.ReadFromJsonAsync<List<PostResponse>>(options);
    }
    
    return new List<PostResponse>();
}
```

---

## 4. Error Handling
The API is hardened to **always** return a consistent error structure if a request fails (e.g., 400, 401, 500).

**Error Schema:**
```json
{
  "status": "error",
  "message": "Human readable description of the problem"
}
```

---

## 5. Deployment Note
The backend is hosted on **Modal**. The database is persistent (Neon PostgreSQL). All data scraped locally or via the live URL goes to the same database.
