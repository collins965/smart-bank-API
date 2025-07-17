import requests

def fetch_current_price(asset_type, symbol):
    if asset_type == 'stock':
        # Example: Twelve Data
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey=YOUR_API_KEY"
        response = requests.get(url)
        data = response.json()
        if 'price' in data:
            return float(data['price'])
        else:
            raise Exception(data.get("message", "Invalid stock symbol"))

    elif asset_type == 'crypto':
        # Example: CoinGecko
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        if symbol.lower() in data and 'usd' in data[symbol.lower()]:
            return float(data[symbol.lower()]['usd'])
        else:
            raise Exception("Invalid crypto symbol")
    
    else:
        raise ValueError("Unsupported asset type")
