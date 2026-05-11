import os

with open('core/templates/pricing.html', 'r', encoding='utf-8') as f:
    content = f.read()

with open('core/templates/premium.html', 'w', encoding='utf-8') as f:
    f.write(content)

os.remove('core/templates/pricing.html')
print("pricing.html -> premium.html")

with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("return render(request, 'pricing.html')", "return render(request, 'premium.html')")

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("views.py guncellendi.")

with open('core/urls.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("path('pricing/', views.pricing, name='pricing')", "path('premium/', views.pricing, name='pricing')")

with open('core/urls.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("urls.py guncellendi.")

with open('core/templates/documentation.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('href="/pricing/"', 'href="/premium/"')

with open('core/templates/documentation.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("documentation.html guncellendi.")

with open('core/templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('href="/pricing/"', 'href="/premium/"')
content = content.replace('>Pricing<', '>Premium<')

with open('core/templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("base.html guncellendi.")

print("TUM ISLEMLER TAMAMLANDI!")