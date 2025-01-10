import sys
import requests
import xml.etree.ElementTree as ElementTree
from urllib.parse import urlparse

class Everytime:
    def __init__(self, path):
        url = urlparse(path)
        if url.netloc == "everytime.kr":
            self.path = url.path.replace("/@", "")
            return
        self.path = path

    def get_timetable(self):
        r = requests.post(
            "https://api.everytime.kr/find/timetable/table/friend",
            data={
                "identifier": self.path,
                "friendInfo": 'true'
            },
            headers={
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Host": "api.everytime.kr",
                "Origin": "https://everytime.kr",
                "Referer": "https://everytime.kr/",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
            }).text

        try:
            tree = ElementTree.parse(r)
            root = tree.getroot()
        except:
            tree = ElementTree.fromstring(r)
            root = tree

        if root.tag == 'response' and root.text.strip() == '-1':
            return None

        result = [[0 for _ in range(7)] for _ in range(56)]

        for subject in root.iter('subject'):
            for x in subject.find("time").findall("data"):
                for i in range(int(x.get("starttime"))//3-32, int(x.get("endtime"))//3-32):
                    result[i][int(x.get("day"))] = 1

        return result


def main():
    e = Everytime(sys.argv[1])
    print(e.get_timetable())
    return e.get_timetable()

if __name__ == '__main__':
    main()
