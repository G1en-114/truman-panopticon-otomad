"""bilibili video search. usage: bili_search.py KEYWORD [pages] [order]"""
import json, urllib.request, urllib.parse, hashlib, time, sys, re, http.cookiejar
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
cj=http.cookiejar.CookieJar()
op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders=[("User-Agent",UA),("Referer","https://www.bilibili.com/")]
op.open("https://www.bilibili.com/").read()
def get(url): return json.load(op.open(url))
TAB=[46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]
nav=get("https://api.bilibili.com/x/web-interface/nav")["data"]["wbi_img"]
raw=nav["img_url"].rsplit("/",1)[1].split(".")[0]+nav["sub_url"].rsplit("/",1)[1].split(".")[0]
key="".join(raw[i] for i in TAB)[:32]
kw=sys.argv[1]; pages=int(sys.argv[2]) if len(sys.argv)>2 else 1; order=sys.argv[3] if len(sys.argv)>3 else "totalrank"
for pn in range(1,pages+1):
    p={"search_type":"video","keyword":kw,"page":pn,"order":order,"wts":int(time.time())}
    q=urllib.parse.urlencode(sorted(p.items()),quote_via=urllib.parse.quote)
    q+="&w_rid="+hashlib.md5((q+key).encode()).hexdigest()
    d=get("https://api.bilibili.com/x/web-interface/wbi/search/type?"+q)
    if d["code"]!=0: print(d["code"],d.get("message")); break
    for v in d["data"].get("result",[]) or []:
        t=re.sub(r"<[^>]+>","",v["title"])
        print(v["bvid"],v["duration"],v["play"],time.strftime("%Y-%m-%d",time.localtime(v["pubdate"])),v["author"],t,sep="\t")
    time.sleep(0.6)
