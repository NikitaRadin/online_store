from django.shortcuts import render


def category(request):
    category_id = request.GET.get('category_id', None)
    if category_id == '1':
        context = {'title': 'Одежда',
                   'header': 'Одежда',
                   'subcategories': ['Куртки', 'Джинсы', 'Футболки', 'Шорты', 'Рубашки', 'Брюки', 'Трусы', 'Носки']}
    elif category_id == '2':
        context = {'title': 'Обувь',
                   'header': 'Обувь',
                   'subcategories': ['Ботинки', 'Сандали', 'Туфли', 'Тапки']}
    return render(request, 'category.html', context=context)
