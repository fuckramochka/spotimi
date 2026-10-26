<div align="center">

# 🌸 Spoti Mi (Gothic Kawaii Edition) 🌸

### *Spotify, but make it kawaii, dark & unrestricted.*

[![Ecosystem](https://img.shields.io/badge/Ecosystem-TikTok%20Mi%20%26%20Amegram-FF2A85?style=for-the-badge)](https://github.com/fuckramochka)
[![License](https://img.shields.io/badge/License-MIT-9D4EDD?style=for-the-badge)](LICENSE)
[![Theme](https://img.shields.io/badge/Theme-Gothic%20Kawaii%20Pink-FF2A85?style=for-the-badge)](#-готично-кавайна-палітра)
[![Architecture](https://img.shields.io/badge/Engine-Pure%20DEX%20%26%20ARSC%20Patcher-00F0FF?style=for-the-badge)](#-архітектура-мода)

</div>

---

## 🖤 Огляд / Про проєкт

**Spoti Mi** — це модифікація Spotify для Android, створена в рамках екосистеми **TikTok Mi** та **Amegram**. Мод повністю позбавляє мобільний клієнт штучних обмежень безкоштовного тарифу та перевдягає фірмовий нудний зелений колір Spotify у стильний **Gothic Kawaii Pink** (неоново-рожевий акцент у темній Kuromi-естетиці).

---

## 🎀 Що вміє Spoti Mi

| Функція | Spotify Free | Spoti Mi |
| :--- | :---: | :---: |
| **Пропуск треків** | Ліміт 6 скіпів на годину | **Безлімітні пропуски** |
| **Вибір пісні (On-Demand)** | Примусовий `Shuffle-only` (випадковий порядок) | **Вільний вибір будь-якого треку** |
| **Реклама** | Аудіо-вставки, відео-перебивки, банери | **Повне блокування всієї реклами** |
| **Перемотування (Scrubbing)** | Заблоковано на мобільних | **Вільне перемотування повзунком часу** |
| **Режим повтору (Repeat)** | Вимкнено | **Повтор одного треку або всього списку** |
| **Canvas & Тексти (Lyrics)** | Обмежено або вимкнено | **Розблоковано на всіх підтримуваних треках** |
| **Інтерфейс** | Настирливі банери «Купити Premium» | **Чистий мінімалістичний UI без апселів** |
| **Колір теми** | Стандартний зелений (`#1DB954`) | **Gothic Kawaii Pink (`#FF2A85`)** |

> [!NOTE]
> **Серверні функції:** Офлайн-кешування треків та стримінг на 320 kbps шифруються на серверах Spotify через DRM (Widevine) і недоступні без платної підписки. Усі клієнтські можливості Spoti Mi розблоковує на 100%.

---

## 🎨 Готично-кавайна палітра

Замість токсично-зеленого кольору, Spoti Mi використовує математичне перенесення в просторі HSV:
* **Gothic Kawaii Pink (`#FF2A85`)**: Неоновий рожевий акцент для кнопок Play, повзунка SeekBar, активних вкладок і перемикачів.
* **Глибокий OLED-фон (`#121212` / `#141216`)**: Зберігає максимальну контрастність і заощаджує батарею на AMOLED-екранах.
* **Збереження градієнтів та прозорості**: Усі відтінки та альфа-канали вихідної графіки Spotify конвертуються пропорційно.

Вбудовані альтернативні палітри:
* `gothic_kawaii_pink` — `#FF2A85` (за замовчуванням)
* `sweet_sakura` — `#FF70A6`
* `cyber_magenta` — `#E056FD`
* `midnight_orchid` — `#BD00FF`
* `blood_rose` — `#E8175D`

---

## ⚙️ Архітектура мода

Spoti Mi побудований за принципом швидкого хірургічного патчингу (без повного декомпілювання та перескладання 200 МБ ресурсів через стандартний `apktool`):

1. **ARSC & AXML Rewriter (`spotimi/accent.py`, `arsc.py`, `axml.py`)**:
   * Напряму редагує таблицю ресурсів `resources.arsc` та скомпільовані векторні XML-файли `res/**/*.xml`, підміняючи байти кольорів у форматі `Res_value`.
2. **Surgical Bytecode Patching (`spotimi/dexpatch.py`)**:
   * Сканує файли DEX лише на наявність сигнатур `PlayerRestrictions`, `ProductState`, `AdManager` та `MainActivity`.
   * Перенаправляє виклики методів обмежень на `mi.spotimi.PlayerHooks` та `mi.spotimi.ProductStateHooks`.
3. **Injected Runtime Engine (`inject/java/mi/spotimi/`)**:
   * Власний модуль `classes.dex`, скомпільований через Google R8/D8 з мінімальним оверхедом.
   * Містить панель налаштувань `SpotiMiSettingsSheet`, логіку блокування реклами та підміну прапорців.

---

## 🚀 Як зібрати мод

### Вимоги
* **Python 3.8+**
* **JDK 17+** (або автоматично знайдений JDK з `~/.gradle/jdks/`)
* Офіційний APK Spotify (архітектура `arm64-v8a` або `universal`, не split-bundle).

### Збірка в одну команду:

```bash
# Базова збірка з Gothic Kawaii Pink:
./build.sh path/to/spotify.apk

# Збірка з вибором іншої палітри:
./build.sh path/to/spotify.apk --accent cyber_magenta

# Вказати свій шлях для збереження готового APK:
./build.sh path/to/spotify.apk -o dist/SpotiMi_v1.0.apk
```

Готовий APK буде автоматично підписаний V2/V3 підписом і готовий до встановлення на будь-який Android без Root-прав!

---

## 🧪 Запуск тестів

```bash
PYTHONPATH=. python3 -m unittest discover tests/
```

---

<div align="center">
Made with 💖 by the team behind <b>TikTok Mi</b> & <b>Amegram</b>.
</div>
