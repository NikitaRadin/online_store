from django.shortcuts import render


def clothes(request):
    context = {'subcategories': ['Куртки', 'Джинсы', 'Футболки', 'Шорты', 'Рубашки', 'Брюки', 'Трусы', 'Носки']}
    return render(request, 'clothes.html', context=context)


def shoes(request):
    context = {'subcategories': ['Ботинки', 'Сандали', 'Туфли', 'Тапки']}
    return render(request, 'shoes.html', context=context)
