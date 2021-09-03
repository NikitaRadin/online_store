from django.shortcuts import render


def clothes(request):
    context = {'title': 'Одежда',
               'header': 'Одежда',
               'subcategories': ['Куртки', 'Джинсы', 'Футболки', 'Шорты', 'Рубашки', 'Брюки', 'Трусы', 'Носки']}
    return render(request, 'category.html', context=context)


def shoes(request):
    context = {'title': 'Обувь',
               'header': 'Обувь',
               'subcategories': ['Ботинки', 'Сандали', 'Туфли', 'Тапки']}
    return render(request, 'category.html', context=context)
