# === main.py — автотрейдинг BTC/USDT с ChatGPT (через HTTP) + RSI + стоп-лосс ===

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
import requests, time, hmac, hashlib, json, os

# ======= Загрузка конфигурации API =======
CONFIG_PATH = "config.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_config(api_key, secret, openai_key):
    with open(CONFIG_PATH, "w") as f:
        json.dump({
            "MEXC_API_KEY": api_key,
            "MEXC_SECRET": secret,
            "OPENAI_KEY": openai_key
        }, f)

config = load_config()
API_KEY = config.get("MEXC_API_KEY", "")
API_SECRET = config.get("MEXC_SECRET", "").encode()
OPENAI_KEY = config.get("OPENAI_KEY", "")

BASE_URL = "https://api.mexc.com"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
PAIR = "BTCUSDT"
TRADE_AMOUNT = 0.001
INTERVAL = 60
STOP_LOSS_PERCENT = 2.5

price_history = []
RSI_PERIOD = 14
last_buy_price = None

def calculate_rsi(prices):
    if len(prices) < RSI_PERIOD + 1:
        return None
    gains = [max(prices[i] - prices[i - 1], 0) for i in range(1, len(prices))]
    losses = [max(prices[i - 1] - prices[i], 0) for i in range(1, len(prices))]
    avg_gain = sum(gains[-RSI_PERIOD:]) / RSI_PERIOD
    avg_loss = sum(losses[-RSI_PERIOD:]) / RSI_PERIOD
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def ask_chatgpt(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Ты опытный криптотрейдер. Отвечай чётко: Покупать, Продавать или Ждать."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 100
        }
        response = requests.post(OPENAI_URL, headers=headers, data=json.dumps(data))
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Ошибка ChatGPT: {e}"

class MainWindow(BoxLayout):
    logs = StringProperty("")
    auto_mode = BooleanProperty(True)
    balance_text = StringProperty("Баланс: —")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.auto_loop, INTERVAL)
        self.get_balance()

    def log(self, msg):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.logs += timestamp + msg + "\n"
        self.ids.scroll_view.scroll_y = 0

    def sign(self, params: str) -> str:
        return hmac.new(API_SECRET, params.encode(), hashlib.sha256).hexdigest()

    def get_price(self):
        try:
            r = requests.get(f"{BASE_URL}/api/v3/ticker/price?symbol={PAIR}")
            return float(r.json()["price"])
        except:
            self.log("❌ Не удалось получить цену.")
            return None

    def get_balance(self):
        try:
            ts = int(time.time() * 1000)
            sig = self.sign(f"timestamp={ts}")
            url = f"{BASE_URL}/api/v3/account?timestamp={ts}&signature={sig}"
            headers = {"X-MEXC-APIKEY": API_KEY}
            r = requests.get(url, headers=headers)
            balances = r.json()["balances"]
            usdt = next((b["free"] for b in balances if b["asset"] == "USDT"), "0")
            btc = next((b["free"] for b in balances if b["asset"] == "BTC"), "0")
            self.balance_text = f"Баланс: {btc} BTC / {usdt} USDT"
        except:
            self.balance_text = "Баланс: ошибка"

    def place_order(self, side, price):
        ts = int(time.time() * 1000)
        params = f"symbol={PAIR}&side={side}&type=LIMIT&timeInForce=GTC&quantity={TRADE_AMOUNT}&price={price}&timestamp={ts}"
        sig = self.sign(params)
        url = f"{BASE_URL}/api/v3/order?{params}&signature={sig}"
        headers = {"X-MEXC-APIKEY": API_KEY}
        r = requests.post(url, headers=headers)
        self.log(f"{side} ордер → {r.status_code}: {r.json()}")

    def auto_loop(self, dt):
        global last_buy_price

        if not self.auto_mode:
            return

        price = self.get_price()
        if not price:
            return

        price_history.append(price)
        if len(price_history) > RSI_PERIOD + 1:
            price_history.pop(0)

        rsi = calculate_rsi(price_history)
        rsi_display = f"RSI: {rsi:.2f}" if rsi else "RSI: расчёт..."
        self.ids.price_label.text = f"BTC: {price:.2f} USDT | {rsi_display}"

        if last_buy_price:
            loss_threshold = last_buy_price * (1 - STOP_LOSS_PERCENT / 100)
            if price < loss_threshold:
                self.log(f"⚠️ Сработал стоп-лосс: текущая цена {price:.2f} ниже {loss_threshold:.2f}")
                self.place_order("SELL", price)
                last_buy_price = None
                return

        prompt = (
            f"Цена BTC: {price:.2f} USDT\n"
            f"RSI: {rsi:.2f if rsi else 'недостаточно данных'}\n"
            f"Я хочу покупать при RSI < 30 и продавать при RSI > 70.\n"
            f"Что делать?"
        )

        advice = ask_chatgpt(prompt)
        self.log(f"🤖 Совет: {advice}")

        if "покупа" in advice.lower():
            self.place_order("BUY", price)
            last_buy_price = price
        elif "прода" in advice.lower():
            self.place_order("SELL", price)
            last_buy_price = None
        elif "жд" in advice.lower():
            self.log("⏳ GPT советует ждать.")
        else:
            self.log("🤔 Непонятный ответ, пропуск.")

    def toggle_auto(self):
        self.auto_mode = not self.auto_mode
        self.log(f"🔁 Авто-режим: {'ВКЛ' if self.auto_mode else 'ВЫКЛ'}")

    def save_keys(self):
        api = self.ids.input_api.text.strip()
        secret = self.ids.input_secret.text.strip()
        openai = self.ids.input_openai.text.strip()
        save_config(api, secret, openai)
        self.log("🔐 Ключи сохранены! Перезапустите приложение.")

class GPTTradeApp(App):
    def build(self):
        return MainWindow()
