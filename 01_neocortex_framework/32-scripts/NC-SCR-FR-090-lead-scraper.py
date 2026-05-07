# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
"""---
Módulo: NC SCR FR 090 lead scraper
---
"""


import asyncio
import csv
import os
import re
from playwright.async_api import async_playwright

# Configurações de Signore Mobili
CITIES = ["Americana", "Nova Odessa", "Sumaré", "Hortolândia", "Paulínia", "Campinas", "Valinhos", "Vinhedo", "Jundiaí", "São Paulo"]
SEARCH_TERM = "Arquitetos em {}"
OUTPUT_FILE = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\DIR-DAT-FR-001-data-main\signore_mobili\leads_arquitetos_completo.csv"

def format_name(name, profession, city):
    # Formato: [NOME] ARQUITETO [CIDADE]
    clean_name = re.sub(r'[^\w\s]', '', name).strip().upper()
    return f"{clean_name} {profession.upper()} {city.upper()}"

def format_phone(phone_raw):
    # Formato: XX XXXXX-XXXX
    digits = re.sub(r'\D', '', phone_raw)
    if len(digits) == 11: # DDD + Celular com 9
        return f"{digits[:2]} {digits[2:7]}-{digits[7:]}"
    elif len(digits) == 10: # DDD + Fixo (para fins de log, mas filtramos celular)
        return f"{digits[:2]} {digits[2:6]}-{digits[6:]}"
    return phone_raw

def is_mobile(phone_raw):
    digits = re.sub(r'\D', '', phone_raw)
    # No Brasil, celulares têm 11 dígitos e o 9º dígito (posição 2) é 9
    return len(digits) == 11 and digits[2] == '9'

async def scrape_city(context, city):
    print(f"[*] Iniciando busca em {city}...")
    page = await context.new_page()
    await page.goto(f"https://www.google.com/maps/search/{SEARCH_TERM.format(city)}")
    
    leads = []
    
    # Scroll lateral para carregar mais resultados
    try:
        results_div = page.locator('div[role="feed"]')
        for _ in range(5): # 5 scrolls costumam ser suficientes para o Maps
            await results_div.evaluate("el => el.scrollBy(0, 1000)")
            await asyncio.sleep(2)
    except:
        pass

    # Locators para os itens da lista
    items = await page.locator('div[role="article"]').all()
    
    for item in items:
        try:
            name = await item.get_attribute('aria-label')
            # Clicar para ver detalhes e pegar o telefone se não estiver visível (ou tentar via texto)
            # Simplificação: O Google Maps costuma ter o telefone disponível no texto ou após clique
            # Para este script industrial, vamos focar no texto visível ou atributo
            
            # Tentar extrair o telefone via regex no texto do item
            inner_text = await item.inner_text()
            phone_match = re.search(r'\(?\d{2}\)?\s?9\d{4}-?\d{4}', inner_text)
            
            if phone_match:
                raw_phone = phone_match.group()
                if is_mobile(raw_phone):
                    formatted_phone = format_phone(raw_phone)
                    formatted_name = format_name(name, "ARQUITETO", city)
                    leads.append({
                        "Name": formatted_name,
                        "Phone": formatted_phone,
                        "City": city
                    })
        except Exception as e:
            continue
            
    await page.close()
    print(f"[+] Encontrados {len(leads)} leads em {city}.")
    return leads

async def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        all_leads = []
        for city in CITIES:
            city_leads = await scrape_city(context, city)
            all_leads.extend(city_leads)
            
        # Salvar em CSV
        keys = ["Name", "Phone", "City"]
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_leads)
            
        await browser.close()
        print(f"\n[DONE] Script finalizado. {len(all_leads)} leads salvos em {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
