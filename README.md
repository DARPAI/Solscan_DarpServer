# 🚀 Solscan_DarpServer

> A DARP server implementation for querying Solana blockchain data via Solscan API.

## ✨ Features

- 📊 Real-time Solana blockchain data querying
- 💎 Comprehensive token and account information
- 📝 Automatic request/response logging
- 🔄 SSE (Server-Sent Events) support
- 🌐 RESTful API endpoints

## 🛠️ Setup

### Prerequisites
- Python 3.8+
- uv package manager

### Installation

1. Create a `.env` file:
```bash
SOLSCAN_API_TOKEN=your_api_token_here
```

2. Start server:
```bash
uv run ./server.py
```

> Server runs on `http://0.0.0.0:3011`

## 🔧 API Tools

| Tool | Description |
|------|-------------|
| `get-token-info` | Get token metadata by CA address |
| `get-sol-token-price` | Get token price data |
| `get-latest-blocks` | Get recent Solana blocks |
| `get-account-info` | Get account token holdings |
| `get-account-activities` | Get account DeFi activities |

## 📊 Logging

All API requests and responses are automatically logged to `solscan_api.log`

## 🔨 Development

### Built with
- Solscan API




---




