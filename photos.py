import fire
import requests
import shutil
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from pprint import pprint
from bs4 import BeautifulSoup
from datetime import datetime
from nanoid import generate
from selenium.webdriver.common.by import By

DRIVER_PATH = './chromedriver'

def visit_website(url):
    try:
        webpage_response = requests.get(url)
        webpage_response.raise_for_status()
        return webpage_response
    except Exception as e:
        print('Website page visit error.')
        pprint(e)

def download_photo(url, name):
    photo_response = requests.get(url, stream=True) # stream as True, response is split into chunks
    photo_response.raw.decode_content = True
    filename = './{}/{}-{}-{}.jpg'.format('downloads', name, generate(), datetime.now().strftime('%d-%m-%Y %H:%M:%S').replace(' ', '_'))
    with open(filename,'wb') as f:
        shutil.copyfileobj(photo_response.raw, f)
    print('Image sucessfully downloaded')

class PhotoDownloader:
    # can use urllib as well urllib.request.urlretrieve
    def download_single_photo(self, link, name='single-photo'):
        response = visit_website(link)
        soup = BeautifulSoup(response.text, 'html.parser') # using response.txt, you dont need any parser
        all_img_tags = soup.find_all('img')
        photo_name = name

        if len(all_img_tags) > 0:
            try:
                img_url = 'https:{}'.format(all_img_tags[0].get('src'))
                download_photo(img_url, photo_name)
            except Exception as e:
                print('GET single photo error')
                print(e)
        else:
            return 'No image found on website'

    def download_photos(self, csv_path):
        print(csv_path)
        with open('./{}'.format(csv_path), mode='r') as file:
            data = csv.reader(file)
            for _, row in enumerate(data):
                img_url = row[0]
                self.download_single_photo(img_url, 'group-photos')

            print('All images downloaded!')

    def download_profile(self, link):
        chrome_service = Service(DRIVER_PATH)
        driver = webdriver.Chrome(service=chrome_service)
        driver.get(link)
        images = driver.find_elements(By.CLASS_NAME, 'overlay')
        for image in images:
            img_href = image.get_attribute('href')
            self.download_single_photo(img_href, 'selenium')

        print('Selenium completed!')

if __name__ == "__main__":
    fire.Fire(PhotoDownloader)