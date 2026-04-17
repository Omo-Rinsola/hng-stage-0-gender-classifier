# Gender Classification API (FastAPI)

##  Overview
This project is a REST API built with FastAPI that predicts the gender associated with a given name using an external API.

It also computes a confidence level and returns structured metadata.

---

##  Live API
Base URL:  
[Live API](hng-stage-0-gender-classifier-production.up.railway.app)

---

## 📌 How to Use
### Endpoint: GET /api/classify


### Example Request (in browser or Postman): 
[Try the API](https://your-railway-url.up.railway.app/api/classify?name=Rinsola)

## ✅ Successful Response

```json
{
  "name": "rinsola",
  "gender": "female",
  "probability": 0.99,
  "sample_size": 1200,
  "is_confident": true,
  "processed_at": "2026-04-17T07:30:12Z"
}


