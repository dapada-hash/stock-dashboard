# dashboard_console.py
import time
import os
from scanner import scan

REFRESH_INTERVAL = 60  # seconds, adjust as needed

def clear_console():
    """Clear the terminal screen (works on Windows/Linux/Mac)."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_dashboard(stocks):
    """Print stock table with moving averages and position status."""
    print("="*70)
    print(f"{'TICKER':<6} {'PRICE':<8} {'MA10':<8} {'MA50':<8} {'MA200':<8} STATUS")
    print("="*70)
    for s in stocks:
        status = "🟢 IN" if s["in_position"] else "⚪ OUT"
        print(f"{s['ticker']:<6} {s['price']:<8} {s['ma10']:<8} {s['ma50']:<8} {s['ma200']:<8} {status}")
    print("="*70)
    print(f"Last update: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

def main():
    """Run the console dashboard repeatedly."""
    while True:
        try:
            stocks = scan(interval="1d")
            clear_console()
            print_dashboard(stocks)
        except KeyboardInterrupt:
            print("\nExiting dashboard.")
            break
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    main()
