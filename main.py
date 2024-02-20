import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def scrape_android_details(app_id):
    url = f"https://play.google.com/store/apps/details?id={app_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extracting app name
        app_name = soup.find('h1', {'class': 'Fd93Bb'}).text.strip()

        download = ''
        ulasan = []
        for d in soup.find_all('div', {'class': 'EGFGHd'}):
            try:
                name_element = d.find('div', {'class': 'X5PpBb'})
                name = name_element.text.strip() if name_element else ''
            except Exception as e:
                print("Error saat mencari nama:", e)
                name = ''
            body = d.find('div', {'class': 'h3YV2d'}).text
            ratings = len(d.find('div', {'class': 'iXRFPc'}).find_all(
                'span', {'class': 'Z1Dz7b'}))
            ulasan.append({
                'name': name,
                'body': body,
                'ratings': float(ratings)
            })
        update_on = soup.find('div', {'class': 'xg1aie'}).text.strip()
        reviews = soup.find('div', {'class': 'g1rdde'}).text.strip().replace(
            'reviews', '').strip()
        if len(soup.find_all('div', {'class': 'ClM7O'})) > 2:
            download = soup.find_all('div', {'class': 'ClM7O'})[1].text.strip()
            app_ratings = soup.find_all('div', {'class': 'ClM7O'})[
                0].text.strip().replace('star', '')
            app_ratings = float(app_ratings)
        else:
            app_ratings = 0.0
            download = soup.find_all('div', {'class': 'ClM7O'})[0].text.strip()
        return {
            'app_name': app_name,
            'downloads': download,
            'app_ratings': app_ratings,
            'reviews': reviews,
            'update_on': update_on,
            'ulasan': ulasan
        }
    else:
        print("Failed to retrieve the page.")
        return None

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/{app_id}")
def read_item(app_id: str):
    app_details = {
        "play_store":scrape_android_details(app_id),
        "app_store": None
    }
    return app_details

