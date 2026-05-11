path = 'core/templates/base.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old = 'href="/rooms/"'
new_btn = '''href="/documentation/" style="border:1.5px solid rgba(255,255,255,0.6); color:white; background:transparent;" onmouseover="this.style.background='rgba(255,255,255,0.25)'" onmouseout="this.style.background='transparent'">Documentation</a>
                <a class="btn me-2" href="/rooms/"'''

content = content.replace('href="/rooms/"', new_btn, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("base.html guncellendi - Documentation butonu eklendi!")