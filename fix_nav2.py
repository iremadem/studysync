 
with open('core/templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '>Premium<'
new = '>Premium</a>\n                <a class="btn me-2" href="/premium-rooms/" style="border:1.5px solid rgba(255,255,255,0.6); color:white; background:transparent;" onmouseover="this.style.background=\'rgba(255,255,255,0.25)\'" onmouseout="this.style.background=\'transparent\'">Premium Rooms<'

content = content.replace(old, new, 1)

with open('core/templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Navbar guncellendi!")