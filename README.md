<div align="center">

# 🥀 Spoti Mi (Gothic Edition) 🥀

### *Spotify, but make it dark, blood rose & unrestricted.*

[![Ecosystem](https://img.shields.io/badge/Ecosystem-TikTok%20Mi%20%26%20Amegram-B81B34?style=for-the-badge)](https://github.com/fuckramochka)
[![License](https://img.shields.io/badge/License-MIT-9D4EDD?style=for-the-badge)](LICENSE)
[![Theme](https://img.shields.io/badge/Theme-Gothic%20Blood%20Rose-B81B34?style=for-the-badge)](#-готична-палітра)
[![Auto-Updater](https://img.shields.io/badge/Updater-GitHub%20Releases-00F0FF?style=for-the-badge)](#-вбудоване-автооновлення)
[![Architecture](https://img.shields.io/badge/Engine-Pure%20DEX%20%26%20ARSC%20Patcher-FF70A6?style=for-the-badge)](#-архітектура-мода)

</div>

---

## 🖤 Огляд / Про проєкт

**Spoti Mi** — це модифікація Spotify для Android, створена в рамках екосистеми **TikTok Mi** та **Amegram**. Мод повністю позбавляє мобільний клієнт штучних обмежень безкоштовного тарифу, повністю випалює залишки зеленого кольору Spotify у вишуканий **Gothic Blood Rose** (оксамитово-кривавий акцент) та додає зручне меню налаштувань і автооновлення з GitHub прямо в додатку.

---

## 🎀 Можливості Spoti Mi

| Функція | Spotify Free | Spoti Mi |
| :--- | :---: | :---: |
| **Пропуск треків** | Ліміт 6 скіпів на годину | **Безлімітні пропуски** |
| **Вибір пісні (On-Demand)** | Примусовий `Shuffle-only` (випадковий порядок) | **Вільний вибір будь-якого треку** |
| **Реклама** | Аудіо-вставки, відео-перебивки, банери | **Повне блокування всієї реклами** |
| **Перемотування (Scrubbing)** | Заблоковано на мобільних | **Вільне перемотування повзунком часу** |
| **Режим повтору (Repeat)** | Вимкнено | **Повтор одного треку або всього списку** |
| **Canvas & Тексти (Lyrics)** | Обмежено або вимкнено | **Розблоковано на всіх підтримуваних треках** |
| **Чистий інтерфейс** | Настирливі банери «Купити Premium» | **Чистий мінімалістичний UI без апселів** |
| **AMOLED Pure Black** | Темно-сірий фон `#121212` | **100% чорний `#000000` для економії OLED** |
| **Вибір палітри в додатку** | Тільки зелений (`#1DB954`) | **Blood Rose, Sakura, Cyber Magenta, Ruby** |
| **Автооновлення** | Лише Google Play | **Вбудований Updater з релізів GitHub** |

> [!NOTE]
> **Серверні функції:** Офлайн-кешування треків та стримінг на 320 kbps шифруються на серверах Spotify через DRM (Widevine) і недоступні без серверного ключа. Усі клієнтські можливості Spoti Mi розблоковує на 100%.

---

## 🎨 100% Випалювання зеленого кольору

На відміну від звичайних тем, Spoti Mi перефарбовує Spotify **на всіх рівнях**:
1. **DEX Bytecode & Jetpack Compose**: Заміна 280+ захардкодzoneних 32-бітних і 64-бітних колірних токенів Spotify Encore (`0xFF1ED760`, `0xFF1DB954`, тощо) у Dalvik-байткоді з автоматичним перерахунком SHA-1 та Adler32 чексум.
2. **ARSC & AXML**: Математичне HSV-перенесення кольорів у скомпільованих ресурсах і векторних XML.
3. **Lottie Animations & PNG Drawables**: Перефарбування анімації відтворення `play_indicator_paused.json` та растрових іконок плеєра.

---

## ⚡ Меню налаштувань Spoti Mi

* **Як відкрити меню:** Натисніть **3 пальцями одночасно** на будь-якому екрані додатка.
* Знизу плавно з'явиться шторка **Spoti Mi Settings**, де можна:
  - Змінити колірний акцент на льоту (Blood Rose, Sweet Sakura, Cyber Magenta, Dark Ruby, Spotify Green).
  - Увімкнути / вимкнути AMOLED Pure Black.
  - Налаштувати тумблери пропусків, On-Demand та блокування реклами.
  - Натиснути кнопку «Перевірити оновлення Spoti Mi».

---

## 🔄 Вбудоване автооновлення

* Додаток перевіряє актуальну версію через `version.json` у репозиторії на GitHub.
* При виході нового релізу з'являється стильний діалог із описом змін (Changelog) та кнопкою оновлення в один дотик через `DownloadManager`.

---

## 🚀 Як зібрати мод

### Вимоги
* **Python 3.8+**
* **JDK 17+** (або автоматично знайдений JDK з `~/.gradle/jdks/`)
* Офіційний APK Spotify (архітектура `arm64-v8a` або `universal`, не split-bundle).

### Збірка в одну команду:

```bash
# Базова збірка з Gothic Blood Rose (#B81B34):
./build.sh path/to/spotify.apk

# Збірка з вибором іншої палітри:
./build.sh path/to/spotify.apk --accent cherry_rose

# Вказати свій шлях для збереження готового APK:
./build.sh path/to/spotify.apk -o dist/SpotiMi_v1.0.1.apk
```

Готовий APK буде автоматично підписаний V2/V3 підписом і готовий до встановлення на будь-який Android без Root-прав!

---

## 🧪 Запуск тестів

```bash
PYTHONPATH=. python3 -m unittest discover tests/
```

---

<div align="center">
Made with 🖤 by <b>fuckramochka</b> (creator of <b>TikTok Mi</b> & <b>Amegram</b>).
</div>
