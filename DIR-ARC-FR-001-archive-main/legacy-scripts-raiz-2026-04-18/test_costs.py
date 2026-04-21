import csv
from collections import defaultdict

cost_file = r'C:\Users\Lucas Valrio\Downloads\usage_data_2026_4 (2)\cost-2026-4.csv'
amount_file = r'C:\Users\Lucas Valrio\Downloads\usage_data_2026_4 (2)\amount-2026-4.csv'

data = defaultdict(lambda: defaultdict(int))
total_ds_cost = 0.0

with open(amount_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        date = row['utc_date']
        if date < "2026-04-08":
            continue
        try:
            amt = float(row['amount']) if row['amount'] else 0
        except:
            amt = 0
        data[date][row['type']] += amt

with open(cost_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        date = row['utc_date']
        if date < "2026-04-08":
            continue
        total_ds_cost += float(row['cost'])

total_hit = sum(d['input_cache_hit_tokens'] for d in data.values()) / 1e6
total_miss = sum(d['input_cache_miss_tokens'] for d in data.values()) / 1e6
total_out = sum(d['output_tokens'] for d in data.values()) / 1e6

models = {
    "Claude 3.5 Sonnet": {"hit": 0.30, "miss": 3.00, "out": 15.00},
    "Claude 3 Opus": {"hit": 1.50, "miss": 15.00, "out": 75.00},
    "Claude 3 Haiku": {"hit": 0.03, "miss": 0.25, "out": 1.25},
    "Gemini 1.5 Pro (>128k)": {"hit": 0.625, "miss": 2.50, "out": 7.50},
    "Gemini 1.5 Flash (>128k)": {"hit": 0.0375, "miss": 0.15, "out": 0.60},
    "GPT-4o": {"hit": 1.25, "miss": 2.50, "out": 10.00},
    "GPT-4o-mini": {"hit": 0.075, "miss": 0.15, "out": 0.60},
    "OpenAI o1-mini": {"hit": 1.50, "miss": 3.00, "out": 12.00},
    "Mistral Large 2": {"hit": 2.00, "miss": 2.00, "out": 6.00},
    "DeepSeek Reasoner (API Tabela)": {"hit": 0.028, "miss": 0.28, "out": 0.42}
}

print("COMPARATIVE COSTS FOR SAME VOLUME (441.56M Cache Hit, 19.12M Miss, 3.61M Out)")
print("-" * 75)
print(f"{'Model':<35} | {'Cost (USD)':>15} | {'Multiplier':>15}")
print("-" * 75)
print(f"{'DeepSeek (Custo Real Faturado)':<35} | ${total_ds_cost:>14.2f} | {'1.0x':>15}")

results = []
for name, price in models.items():
    cost = total_hit * price['hit'] + total_miss * price['miss'] + total_out * price['out']
    mult = cost / total_ds_cost if total_ds_cost > 0 else 0
    results.append((name, cost, mult))

results.sort(key=lambda x: x[1])

for name, cost, mult in results:
    if name != "DeepSeek Reasoner (API Tabela)":
         print(f"{name:<35} | ${cost:>14.2f} | {mult:>14.1f}x")
    else:
         print(f"{name:<35} | ${cost:>14.2f} | {mult:>14.1f}x (Estimativa pura)")

