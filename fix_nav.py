 
path = 'core/templates/base.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old = 'href="/documentation/"'
new = 'href="/pricing/" style="border:1.5px solid rgba(255,255,255,0.6); color:white; background:transparent;" onmouseover="this.style.background=\'rgba(255,255,255,0.25)\'" onmouseout="this.style.background=\'transparent\'">Pricing</a>\n                <a class="btn me-2" href="/documentation/"'

content = content.replace('href="/documentation/"', new, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Pricing butonu eklendi!")