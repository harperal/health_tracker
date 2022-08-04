# Author: Spencer Lynn Wahlstrom
# Date: 7/24/2022
# Description:
import time
import requests
import bs4


def get_cals(key):
    """Function scrapes google search for calories and returns calories and serving size if found, else None"""
    url = 'https://google.com/search?q='+key + ' calories'
    search = requests.get(url)
    parse = bs4.BeautifulSoup(search.text, "html.parser")
    result = parse.find("div", {"class":"BNeawe iBp4i AP7Wnd"})
    if result is None:
        result = parse.find("span", {"class":"FCUp0c rQMQod"})
    result = result.string if result else 'None'
    if result.text == "People also ask":
        result = 'None'
    serving_search = parse.find_all("div", {"class":"BNeawe s3v9rd AP7Wnd"})
    serving = None
    for tag in serving_search:
        if "Serving Size: " in tag.text:
            serving = tag
    if serving:
        serving = serving.text
        serving = serving.partition("Serving Size: ")[2].partition("Amount")[0]
        serving = serving.partition("(")[2].partition(")")[0]
    else:
        serving = 'None'
    if result == 'None' or serving == 'None':
        return 'None', 'None'

    else:
        return result, serving


def main():
    print('listening')
    while True:
        time.sleep(3)
        with open('init_search.txt', 'r') as f:
            message = f.readline()
            if message == 'run':
                with open('keyword.txt', 'r') as file:
                    search_term = file.readline()
                    result = get_cals(search_term)
                with open('calories.txt', 'w') as out:
                    out.write(str(result[0])+ "\n")
                    out.write(str(result[1]))
                open('init_search.txt', 'w').close()
                open('keyword.txt', 'w').close()


if __name__ == '__main__':
    main()