import copy
import os
import pickle
import re
import sys
import time

import PyPDF2
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

username = 'email@website.com'
password = 'password'
base_url = 'https://am.mazdaserviceinfo.com/mazdagms3/index?page=<use the dropdown>'


def login_to_service_portal(driver):
    driver.get('https://www.mazdaserviceinfo.com/login')
    time.sleep(2)
    try:
        driver.find_element(By.CLASS_NAME, "delete").click()
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.CLASS_NAME, "is-primary").click()
        time.sleep(2)
        driver.find_element(By.CLASS_NAME, "is-danger").click()
    except:
        driver.find_element(By.CLASS_NAME, "is-danger").click()
    time.sleep(2)
    driver.get('https://www.mazdaserviceinfo.com/electronic-service')
    driver.find_element(By.CLASS_NAME, "is-default").click()
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[1])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def expand_menu_tree(driver):
    ids = []
    for i in range(5):
        items = driver.find_elements(By.XPATH, '//*[@id="vcfacets"]//font')
        for item in reversed(items):
            if item.id not in ids:
                ActionChains(driver).move_to_element(item).click().perform()
                ids.append(item.id)


def scrape_menu_tree(driver):
    leaves = {}
    items = driver.find_elements(By.XPATH, '//*[@id="vcfacets"]//div')
    filtered = []

    for item in items:
        onclick = item.get_attribute('onclick')
        if onclick and onclick.startswith('TREE.displayDoc'):
            filtered.append(item)

    for key, item in enumerate(filtered):
        onclick = item.get_attribute('onclick')
        item_id = onclick.split('\'')[1]
        item_name = item.text
        parent = item.find_element(By.XPATH, '../../font')
        item_parent_raw = parent.get_attribute('onclick').split('\'')
        item_root_cat = item_parent_raw[1]
        item_sub_cats = item_parent_raw[5].split('^.')[1:]
        leaf = [item_root_cat] + item_sub_cats
        leaf.append({'name': item_name, 'id': item_id})
        leaves[key] = leaf

    return leaves


def get_menu_tree(driver):
    if os.path.exists('tree'):
        with open('tree', 'rb') as tf:
            return pickle.load(tf)
    else:
        print('Cataloging service articles - this will take ~10 mins...')
        expand_menu_tree(driver)
        t = scrape_menu_tree(driver)
        with open('tree', 'wb') as tf:
            pickle.dump(t, tf)
        print('Catalogue made and cached to disk. Starting downloads...')
        return t


def get_authenticated_requests_session(driver):
    session_cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in session_cookies:
        session.cookies.set(cookie['name'], cookie['value'])
        session.headers.update({'referer': base_url})
    return session


def parse_path_and_create_directory(leaf):
    path = 'MANUAL/'
    head = leaf.pop(0)
    while type(head) is not dict:
        safe = head.translate(str.maketrans(r'\/:*?"<>|', r'.........'))
        path += safe + '/'
        head = leaf.pop(0)
    name = head['name'].translate(str.maketrans(r'\/:*?"<>|', r'.........'))
    path += name + ' [' + head['id'] + '].pdf'

    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def pdf_has_data(path):
    try:
        doc = PyPDF2.PdfFileReader(path)
        if doc.getNumPages() > 1:
            return True
        text = doc.getPage(0).extractText()
        pattern = re.compile('\nid.{12}\n')
        matches = re.findall(pattern, text)
        if matches or 'Mazda North American Operations' in text:
            return True
    except:
        pass
    return False


def report_progress():
    percentage = round((progress_count / num_articles) * 100, 4)
    print("\r{}/{} articles downloaded [{}%] - {} failures".format(progress_count,
                                                                   num_articles,
                                                                   percentage,
                                                                   num_fails), end='')
    sys.stdout.flush()


def try_download(article_to_download):
    for _attempt in range(5):
        try:
            pdf_url = 'http://am.mazdaserviceinfo.com/mazdagms3/' \
                      'ExecutePDF?id={}'.format(article_to_download[-1]['id'])
            save_path = parse_path_and_create_directory(article_to_download[:])
            raw = requests_session.get(pdf_url)
            with open(save_path, 'wb') as f:
                f.write(raw.content)
            if pdf_has_data(save_path):
                return True
            else:
                if os.path.exists(save_path):
                    os.remove(save_path)
                continue
        except Exception:
            continue
    return False


def download_all(article_dict):
    global progress_count
    global num_fails
    for key, article in article_dict.items():
        if try_download(article):
            progress_count += 1
            del all_articles[key]
            if progress_count % 10 == 0:
                with open('tree', 'wb') as f:
                    pickle.dump(all_articles, f)
        else:
            num_fails += 1

        report_progress()
    with open('tree', 'wb') as f:
        pickle.dump(all_articles, f)


options = Options()
options.add_argument('-headless')
chrome = webdriver.Chrome(options=options)
chrome.implicitly_wait(5)

login_to_service_portal(chrome)
chrome.get(base_url)
time.sleep(4.5)
all_articles = get_menu_tree(chrome)
num_articles = len(all_articles)
requests_session = get_authenticated_requests_session(chrome)

chrome.quit()

progress_count = 0
num_fails = 0
if not os.path.exists('MANUAL'):
    os.mkdir('MANUAL')

print('Downloading started...')
download_all(copy.copy(all_articles))
print('Retrying failed items...')
download_all(copy.copy(all_articles))

with open('articles_to_manually_download.txt', 'w') as f:
    for article in all_articles.values():
        f.write(str(article) + '\n')
print('{}/{} articles downloaded. Please consult articles_to_manually_download.'
      'txt and download any remaining articles manually.'.format(progress_count,
                                                                 num_articles))
