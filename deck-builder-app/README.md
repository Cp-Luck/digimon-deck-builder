# 🃏 Deck Builder App

A simple Python/FastAPI starter app for creating, searching, and saving Digimon card decks using a public API.

---

## 📌 Overview
This project is a deck-building application that integrates with the Digimon Card API.  
Users can search for cards, build custom decks, and manage their saved decks.

---

## 🚀 Features
- Search cards using filters (name, color, type, etc.)
- Retrieve all available cards
- Add/remove cards from a deck
- View your current deck
- Save decks to file (JSON)
- FastAPI backend support

---

## 🔗 API Used
Base URL:
https://digimoncard.io/api-public/

### Endpoints:
- `/search` → Search for cards with filters  
- `/getAllCards` → Get list of all cards  

### Example Request:
```bash
https://digimoncard.io/api-public/search?color=red&type=digimon