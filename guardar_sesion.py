from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.facebook.com")

    print("Inicia sesión en Facebook manualmente.")
    input("Cuando estés completamente logueado y puedas ver Marketplace, presiona Enter...")

    context.storage_state(path="mi_sesion.json")
    print("Sesión guardada en mi_sesion.json")

    browser.close()