from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json

driver_path = "/home/ahmetturgut/chromedriver"
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path=driver_path,chrome_options=chrome_options)
elastic_array=[]
elastic_company=[]
elastic_size=[]
elastic_indices=[]
mongodb_array=[]
mongodb_company=[]
mongodb_size=[]
mongodb_indices=[]
data = {}
def login():
    driver.get("https://account.shodan.io/login")
    driver.find_element_by_id("username").send_keys("YOUR ID")
    driver.find_element_by_id("password").send_keys("YOUR PASSWORD$")
    driver.find_element_by_name("login_submit").click()

def elastic():
    result=driver.find_elements_by_class_name('search-result')
    for i in range(len(result)):
        a = result[i].find_element_by_class_name('ip')
        elastic_array.append(a.text)
        company = result[i].find_element_by_class_name('os')
        elastic_company.append(company.text)
        try:
            companys = result[i].find_element_by_class_name('section-green')
            elastic_size.append(companys.text)
        except:
            elastic_size.append("NULL")
        all_indicex = result[i].text
        indices = all_indicex.split('Elastic Indices:')
        elastic_indices.append(indices[1])

    return len(elastic_array)

def mongodb():
    result = driver.find_elements_by_class_name('search-result')
    for i in range(len(result)):
        a = result[i].find_element_by_class_name('ip')
        mongodb_array.append(a.text)
        company = result[i].find_element_by_class_name('os')
        mongodb_company.append(company.text)
        try:
            companys = result[i].find_element_by_class_name('section-green')
            mongodb_size.append(companys.text)
        except:
            mongodb_size.append("NULL")
        indices = result[i].find_elements_by_class_name('table')
        b = ""
        for aa in indices:
            b += aa.text
        mongodb_indices.append(b)
    return len(mongodb_array)

def nextpage():
    next = driver.find_element_by_link_text("Next")
    next.click()

def get_elastic():
    driver.get("https://www.shodan.io/search?query=port%3A%229200%22+all%3A%22elastic+indices%22++country%3A%22tr%22")
    while True:
        prelen = len(elastic_array)
        a = elastic()
        if a != (prelen + 10):
            break
        else:
            nextpage()

def get_mongodb():
    driver.get("https://www.shodan.io/search?query=all%3A%22mongodb+server+information%22+all%3A%22metrics%22+country%3A%22tr%22")
    while True:
        prelen = len(mongodb_array)
        a = mongodb()
        if a != (prelen + 10):
            break
        else:
            nextpage()


def write():
    data['ElasticSearch'] = []
    for i in range(len(elastic_array)):
        indices=elastic_indices[i]
        indicesarray=indices.split('\n')
        for j in range(len(indicesarray)):
            indicesarray[j]=indicesarray[j].strip()
        indicesarray.pop(0)
        data['ElasticSearch'].append({
            'ip': elastic_array[i],
            'company': elastic_company[i],
            'size': elastic_size[i],
            'indices': indicesarray
        })
    data['MongoDb'] = []
    for i in range(len(mongodb_array)):
        indices=mongodb_indices[i]
        indicesarray=indices.split('\n')
        indicesarray.pop(0)
        data['MongoDb'].append({
            'ip': mongodb_array[i],
            'company': mongodb_company[i],
            'size': mongodb_size[i],
            'indices': indicesarray
        })
    with open('data.txt', 'w') as outfile:
        json.dump(data, outfile, indent=4)

def main():
    login()
    get_elastic()
    get_mongodb()
    driver.close()
    write()

if __name__ == '__main__':
    main()
