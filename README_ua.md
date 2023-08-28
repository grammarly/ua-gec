[English version](./README.md)

# UA-GEC: перший анотований GEC-корпус української мови

Цей репозиторій містить дані UA-GEC і супровідну бібліотеку Python.

## Новини

* **May 2023**: Опубліковано результати [Shared Task on Ukrainian GEC](https://unlp.org.ua/shared-task/)
* **November 2022**: Версія 2.0 корпусу. Більше даних та більш детальні анотації.
* **January 2021**: Перший реліз.

[CHANGELOG.md](./CHANGELOG.md) містить більш детальні оновлення.

## Дані

Усі дані корпусу та метадані вміщені в `./data`. Директорія має дві вкладені папки
для двох версій корпусу: [gec-fluency і gec-only](#annotation-format)

Обидві версії корпусу містять дві вкладені папки [тренувальна та тестувальна частини](#train-test-split) з різними репрезентаціями даних:

`./data/{gec-fluency,gec-only}/{train,test}/annotated` зберігає документи в [анотованому форматі](#annotation-format)

`./data/{gec-fluency,gec-only}/{train,test}/source` і `./data/{gec-fluency,gec-only}/{train,test}/target` зберігають
оригінали та виправлені версії документів. Текстові файли в цих
папках є простим текстом без розмітки анотацій. Ці файли були
створені з анотованих даних і є певним чином надлишковими. Ми їх зберігаємо,
оскільки цей формат зручно використовувати в деяких випадках.

## Метадані

`./data/metadata.csv` містить метадані кожного документа. Це файл CSV із
такими полями:

- `id` (str): ідентифікатор документа;
- `author_id` (str): ідентифікатор автора документа;
- `is_native` (int): 1, якщо автор є носієм мови, 0 в іншому випадку;
- `region` (str): регіон народження автора. Особливу категорію "Інше";
  використовують і для авторів, які народилися за межами України, і для авторів
  які воліли не вказувати свій регіон;
- `gender` (str): може бути "Жіноча" (жіночий), "Чоловіча" (чоловічий) або "Інша" (інший);
- `occupation` (str): одне з "Технічна", "Гуманітарна", "Природнича", "Інша";
- `submission_type` (str): одне з "essay", "translation" або "text\_donation";
- `source_language` (str): це поле для матеріалів типу "переклад",
    вказує вихідну мову тексту перекладу. Можливі значення:
    "de", "en", "fr", "ru" та "pl";
- `annotator_id` (int): ідентифікатор анотатора, який виправив документ;
- `partition` (str): тренувальна або тестувальна частина ("test" або "train");
- `is_sensitive` (int): 1, якщо документ містить ненормативну або образливу лексику.

## Формат анотації

Анотовані файли — це текстові файли, які використовують такий формат внутрішньотекстових анотацій:
`{error=>edit:::error_type=Tag}`, де `error` і `edit` означають текстовий елемент перед
і після виправлення відповідно, а `Tag` позначає категорію помилок і підкатегорію помилок, пов'язаних з Grammar i Fluency.

Приклад анотованого речення:
```
    Мені {подобається=>подобаються:::error_type=G/Number} черепахи.
```

Нижче наведено список типів помилок, представлених у корпусі:

Орфографічні помилки:
- `Spelling`.

Пунктуаційні помилки:
- `Punctuation`.

Граматичні помилки:
- `G/Case`: некоректне вживання відмінкової форми самостійних частин мови;
- `G/Gender`: некоректне вживання форми роду самостійних частин мови;
- `G/Number`: некоректне вживання форми числа самостійних частин мови;
- `G/Aspect`: некоректне вживання форми виду дієслова;
- `G/Tense`: некоректне вживання часової форми дієслова;
- `G/VerbVoice`: некоректне вживання форми стану дієслова або дієприкметника;
- `G/PartVoice`: некоректне вживання форми стану дієприкметника;
- `G/VerbAForm`: некоректне вживання аналітичної форми дієслова;
- `G/Prep`: некоректне вживання прийменника;
- `G/Participle`: некоректне вживання граматичної категорії дієприслівника;
- `G/UngrammaticalStructure`: порушення граматичних норм у синтаксичних конструкція;
- `G/Comparison`: некоректно утворена форма вищого та найвищого ступенів порівняння прикметників та прислівників;
- `G/Conjunction`: некоректне вживання сполучників щодо виду підрядності, порушення структури і значення парних сполучників у складнопідрядних реченнях;
- `G/Other`: інші граматичні помилки.

Помилки, пов'язані зі стилем:
- `F/Style`: помилки стилю;
- `F/Calque`: дослівний переклад з інших мов;
- `F/Collocation`: порушення норм слововжитку;
- `F/PoorFlow`: вживання конструкцій, що погіршують читабельність та милозвучність тексту;
- `F/Repetition`: стилістично невиправдане вживання повторів;
- `F/Other`: інші помилки стилю.

Супровідний пакет Python, `ua_gec`, надає багато інструментів для роботи
з анотованими текстами.

## Pозбиття корпусу на тренувальну і тестувальну частини

Ми очікуємо, що користувачі корпусу тренуватимуть свої моделі лише на __train__ split. За необхідністю, додатково розділіть його на train-dev (або використайте крос-валюдацію).

Будь ласка, використовуйте __test__ split лише для звітування про результати вашої остаточної моделі.
Зокрема, ніколи не оптимізуйте модель на тестовому сеті. Не підбирайте на ньому гіперпараметри. Ні в якому разі не використовуйте його для вибору моделі.

У наступному розділі наведено статистику для кожного розділення.

## Статистика

UA-GEC містить:

### GEC+Fluency

| Розбиття  | Документи | Речення   |  Токени | Автори  | Помилки | 
|:---------:|:---------:|----------:|--------:|:-------:|--------|
| train     | 1,706     | 31,038    | 457,017 | 752     | 38,213 |
| test      |   166     |  2,697    | 43,601  | 76      |  7,858 |
| **TOTAL** | 1,872     | 33,735    | 500,618 | 828     | 46,071 |

Дивіться [stats.gec-fluency.txt](./stats.gec-fluency.txt) для детальної статистики.


### GEC-only

| Розбиття  | Документи | Речення   |  Токени | Автори  | Помилки | 
|:---------:|:---------:|----------:|--------:|:-------:|--------|
| train     | 1,706     | 31,046    | 457,004 | 752     | 30,049 |
| test      |   166     |  2,704    |  43,605 |  76     |  6,169 |
| **TOTAL** | 1,872     | 33,750    | 500,609 | 828     | 36,218 |

Дивіться [stats.gec-only.txt](./stats.gec-only.txt) для детальної статистики.

## Python бібліотека

Як альтернативу прямій роботі з файлами даних ви можете використовувати пакет Python
під назвою `ua_gec`. Цей пакет містить дані та  категорії для ітерації по
документах, читання метаданих, роботи з анотаціями тощо.

### Початок роботи

Пакет можна легко встановити за допомогою `pip`:

```
    $ pip install ua_gec
```

Крім того, ви можете встановити його з вихідного коду:

```
    $ cd python
    $ python setup.py development
```
### Ітерація по корпусу

Після інсталяції, анотовані документи будуть доступні з коду Python:

```python
    
    >>> from ua_gec import Corpus
    >>> corpus = Corpus(partition="train", annotation_layer="gec-only")
    >>> for doc in corpus:
    ...     print(doc.source)         # "I likes it."
    ...     print(doc.target)         # "I like it."
    ...     print(doc.annotated)      # <AnnotatedText("I {likes=>like} it.")
    ...     print(doc.meta.region)    # "Київська"
```

Зауважте, що властивість `doc.annotated` має тип `AnnotatedText`. Цей
клас описано в [наступному розділі](#working-with-annotations)

### Робота з анотаціями

`ua_gec.AnnotatedText` — це клас, який надає інструменти для обробки
анотованих текстів. Він може ітеруватися по анотаціям, отримувати анотацію
типу помилки, видалити деякі анотації тощо.

Ось приклад для початку. Це видалить усі анотації F/Style з тексту:

```python
    >>> from ua_gec import AnnotatedText
    >>> text = AnnotatedText("Мені {подобається=>подобаються:::error_type=G/Number} це.")
    >>> для ann у text.iter_annotations():
    ... print(ann.source_text) # подобається
    ... print(ann.top_suggestion) # подобаються
    ... print(ann.meta) # {'error_type': 'Grammar'}
    ... if ann.meta["error_type"] == "F/Style":
    ... text.remove(ann) # або `text.apply(ann)`
```
## Кілька анотаторів

Деякі документи анотували декілька анотаторів. Такі документи
мають спільний `doc_id`, але відрізняються `doc.meta.annotator_id`.

Наразі набори тестів для gec-fluency та gec-only проанотовані двома анотаторами.
Категорії корупусу містять 45 подвійно анотованих документів.

## Покращення корпусу

Покращення даних та коду вітається. Буль ласка, створіть мердж ріквест.

## Цитування

[Супровідна стаття](https://arxiv.org/abs/2103.16997):

```
@inproceedings{syvokon-etal-2023-ua,
    title = "{UA}-{GEC}: Grammatical Error Correction and Fluency Corpus for the {U}krainian Language",
    author = "Syvokon, Oleksiy  and
      Nahorna, Olena  and
      Kuchmiichuk, Pavlo  and
      Osidach, Nastasiia",
    booktitle = "Proceedings of the Second Ukrainian Natural Language Processing Workshop (UNLP)",
    month = may,
    year = "2023",
    address = "Dubrovnik, Croatia",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.unlp-1.12",
    pages = "96--102",
    abstract = "We present a corpus professionally annotated for grammatical error correction (GEC) and fluency edits in the Ukrainian language. We have built two versions of the corpus {--} GEC+Fluency and GEC-only {--} to differentiate the corpus application. To the best of our knowledge, this is the first GEC corpus for the Ukrainian language. We collected texts with errors (33,735 sentences) from a diverse pool of contributors, including both native and non-native speakers. The data cover a wide variety of writing domains, from text chats and essays to formal writing. Professional proofreaders corrected and annotated the corpus for errors relating to fluency, grammar, punctuation, and spelling. This corpus can be used for developing and evaluating GEC systems in Ukrainian. More generally, it can be used for researching multilingual and low-resource NLP, morphologically rich languages, document-level GEC, and fluency correction. The corpus is publicly available at https://github.com/grammarly/ua-gec",
}
```


## Контакти

* nastasiya.osidach@grammarly.com
* olena.nahorna@grammarly.com
* oleksiy.syvokon@gmail.com
* pavlo.kuchmiichuk@gmail.com
