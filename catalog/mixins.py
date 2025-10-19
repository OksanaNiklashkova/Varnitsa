from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


class SearchMixin:
    """Миксин для полнотекстового поиска по нескольким моделям"""

    def perform_search(self, query, search_models):
        """
        Выполняет поиск по нескольким моделям
        Args:
            query: поисковый запрос
            search_models: список словарей с настройками моделей для поиска
                Пример: [
                    {
                        'model': Product,
                        'fields': ['product_name', 'trade_mark', 'specification', 'description'],
                        'weight': 'A'
                    },
                    {
                        'model': Publication,
                        'fields': ['title', 'text', 'rubric'],
                        'weight': 'A'
                    }
                ]
        """
        if not query:
            return []

        search_query = SearchQuery(query)
        results = []

        for config in search_models:
            model = config['model']
            fields = config['fields']
            weight = config.get('weight', 'A')

            # Создаем SearchVector для указанных полей
            search_vectors = []
            for field in fields:
                search_vectors.append(SearchVector(field, weight=weight))

            # Объединяем векторы
            combined_vector = search_vectors[0]
            for vector in search_vectors[1:]:
                combined_vector += vector

            # Выполняем поиск с ранжированием
            model_results = model.objects.annotate(
                search=combined_vector,
                rank=SearchRank(combined_vector, search_query)
            ).filter(
                search=search_query
            ).order_by('-rank')  # Сортировка по релевантности

            # Добавляем тип модели для идентификации в шаблоне
            for obj in model_results:
                obj.model_type = model.__name__.lower()
                obj.app_label = model._meta.app_label

            results.extend(list(model_results))

        # Сортируем все результаты по релевантности
        results.sort(key=lambda x: x.rank, reverse=True)
        return results