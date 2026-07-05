"""
Домашнее задание 1: ThreadPoolExecutor 🧵

Вы пишете сервис, который собирает данные из нескольких внешних API.
Каждый запрос занимает ~50 мс (I/O-bound). Нужно использовать
пул потоков для ускорения.

Задания:
    1.1 — Базовый пул потоков
    1.2 — Обработка ошибок
    1.3 — Прогресс-бар (повышенная сложность)

📖 См. лекцию 1, раздел 3 (Threading) и примеры:
   lectures/01_lecture/examples/02_threading/01_simple_thread.py
   lectures/01_lecture/examples/02_threading/02_thread_pool.py
"""

from typing import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed


# ═══════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ — не меняйте их
# ═══════════════════════════════════════════════════════════


def fetch_one(url: str) -> str:
    """Заглушка HTTP-запроса. 'Скачивает' URL за ~50 мс."""
    import time

    time.sleep(0.05)
    return f"data:{url}"


def fetch_one_with_delay(url_delay: tuple[str, float]) -> str:
    """Заглушка с кастомной задержкой: (url, delay) -> data."""
    url, delay = url_delay
    import time

    time.sleep(delay)
    return f"data:{url}"


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 1.1 — Базовый пул потоков
# ═══════════════════════════════════════════════════════════


def fetch_all(urls: list[str], max_workers: int = 4) -> list[str]:
    """Скачать все URL через ThreadPoolExecutor.

    Требования:
        - Использовать ThreadPoolExecutor как context manager
        - Результаты в том же порядке, что и urls
        - Не создавать потоки вручную

    Параметры:
        urls: список строк-URL
        max_workers: размер пула

    Пример:
        >>> fetch_all(["a", "b", "c"], max_workers=2)
        ['data:a', 'data:b', 'data:c']
    """
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(fetch_one, url) for url in urls]
        res = []
        for f in futures:
            res.append(f.result())
        return res

# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 1.2 — Обработка ошибок
# ═══════════════════════════════════════════════════════════


def fetch_all_with_errors(urls: list[str], max_workers: int = 4) -> list[str | None]:
    """Скачать URL, возвращая None для упавших.

    Некоторые URL могут вызывать исключение (например, ConnectionError).
    Нужно перехватить исключения и вернуть None для таких URL,
    не прерывая обработку остальных.

    Для имитации ошибок: если в URL есть подстрока "bad" — считать его
    проблемным и имитировать ошибку соединения.

    Требования:
        - Все URL должны быть обработаны (первая ошибка не прерывает)
        - Для "bad" URL вернуть None
        - Для остальных — результат fetch_one()
    """
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [None if 'bad' in url else pool.submit(fetch_one, url) for url in urls]
        res = []
        for f in futures:
            if f is not None:
                res.append(f.result())
            else:
                res.append(None)
        return res
            

# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 1.3 — Прогресс-бар (повышенная сложность)
# ═══════════════════════════════════════════════════════════


def fetch_all_with_progress(
    urls: list[str],
    max_workers: int = 4,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[str]:
    """Скачать URL с уведомлением о прогрессе.

    После завершения каждого URL вызывать progress_callback(completed, total).
    Результаты вернуть в порядке завершения, а не в порядке urls.

    Параметры:
        urls: список URL
        max_workers: размер пула
        progress_callback: функция(completed, total)

    Требования:
        - progress_callback вызывается после каждого завершённого URL
        - Результаты в порядке завершения (as completed)

    Пример:
        completed = []
        def on_progress(done, total):
            completed.append(done)

        results = fetch_all_with_progress(
            ["a", "b", "c"], max_workers=2, progress_callback=on_progress
        )
        # completed[-1] == 3 """
    with ThreadPoolExecutor(max_workers) as pool:
        futures = [pool.submit(fetch_one, url) for url in urls]
        res = []
        completed = 0
        total = len(futures)
        for f in as_completed(futures):
            completed += 1
            res.append(f.result())
            if progress_callback is not None:
                progress_callback(completed, total)
    return res

