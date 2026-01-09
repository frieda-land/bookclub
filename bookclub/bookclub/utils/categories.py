from crud import crud
from fastapi import HTTPException
from requests import Session
from schemas.schema import ChallengeCategoryCreate


def create_single_category(db: Session, category: ChallengeCategoryCreate, user_id=None):
    category_exists = None
    if not category.original_number and user_id:
        category_exists = crud.get_category_by_title(db, category.title)
        if category_exists:
            raise HTTPException(status_code=400, detail="Diese Wunschkategorie gibt es dieses Jahr schon 💡")
        last_category_number = crud.get_latest_number_for_year(db)
        category.original_number = last_category_number + 1
        category.user_id_custom_category = user_id
    elif not category.original_number:
        raise HTTPException(status_code=400, detail="Original number is required")
    else:
        category_exists = crud.get_category_by_original_number(db, category.original_number, category.year)
    if category_exists:
        raise HTTPException(status_code=400, detail="Category already registered")
    return crud.create_challenge_category(db, category)


challenges = {
    # 2024: {
    #     1: "A book with with more than 40 chapters",
    #     2: "A bildungsroman",
    #     3: "A book about a 24-year-old",
    #     4: "A book about a writer",
    #     5: "A book that features the ocean",
    #     6: "A book about pirates",
    #     7: "A book about women's sports and/or by a woman athlete",
    #     8: "A book by a blind or visually impaired author",
    #     9: "A book by a deaf or hard-of-hearing author",
    #     10: "A book by a self-published author",
    #     11: "A book from a genre you typically avoid",
    #     12: "A book from an animal's POV",
    #     13: "A book originally published under a pen name",
    #     14: "A book recommended by a bookseller",
    #     15: "A book recommended by a librarian",
    #     16: "A book set 24 years before you were born",
    #     17: "A book set in a travel destination on your bucket list",
    #     18: "A book set in space",
    #     19: "A book set in the future",
    #     20: "A book set in the snow",
    #     21: "A book that came out in a year that ends with '24'",
    #     22: "A book that centers on video games",
    #     23: "A book that features dragons",
    #     24: "A book that takes place over the course of 24 hours",
    #     25: "A book that was published 24 years ago",
    #     26: "A book that was turned into a musical",
    #     27: "A book where someone dies in the first chapter",
    #     28: "A book set during a holiday you don't celebrate",
    #     29: "A book with a neurodivergent main character",
    #     30: "A book with a one-word title you had to look up in a dictionary",
    #     31: "A book with a title that is a complete sentence",
    #     32: "A book by an author that 'everyone' has read except you",
    #     33: "A book with an unreliable narrator",
    #     34: "A book with at least three POVs",
    #     35: "A book with magical realism",
    #     36: "A book written by an incarcerated or formerly incarcerated person",
    #     37: "A book you picked without reading the blurb",
    #     38: "A cozy fantasy book",
    #     39: "A fiction book by a trans or nonbinary author",
    #     40: "A memoir that explores queerness",
    #     41: "A nonfiction book about Indigenous people",
    #     42: "A second-chance romance",
    #     43: "An autobiography by a woman in rock 'n' roll",
    #     44: "An LGBTQ+ romance novel",
    #     45: "A book with 24 letters in the title",
    #     46: "The 24th book of an author",
    #     47: "A book that starts with the letter 'X'",
    #     48: "Ein Buch mit einer Widmung des Autors",
    #     49: "Ein Roman mit einem Protagonisten, der wie du selbst heißt (Schreibweise darf abweichen)",
    #     50: "Das Siegerbuch eines ausländischen Buchpreises",
    #     51: "Ein Buch von dem/der neuen Nobelpreisträger/in",
    #     52: "Ein geliehenes Buch",
    #     53: "Doppeljoker - eine Kategorie, die du schon hattest, aber dieses Buch passt sooo perfekt dazu",
    #     54: "Ein Buch, das über einen Hund geht oder in dem ein Hund vorkommt",
    #     55: "Ein Buch, in dem alternative Lebens- bzw. Seinsweisen (Familie, Arbeit, Körper-Geist, Kunst, Wirtschaft, …) dargestellt werden",
    #     56: "Ein Buch über eine Kriegerin (im weitesten Sinne)",
    #     57: "Ein Comic/ Graphic Novel",
    #     58: "Gemeinsames Buch: Echtzeitalter – Tonio Schaching",
    # },
    # 2025: {
    #     1: "A book about a POC experiencing joy and not trauma",
    #     2: "A book you want to read based on the last sentence",
    #     3: "A book about space tourism",
    #     4: "A book with two or more books on the cover or 'book' in the title",
    #     5: "A book with a snake on the cover or in the title",
    #     6: "A book that fills your favorite prompt from the 2015 PS Reading Challenge",
    #     7: "A book about a cult",
    #     8: "A book under 250 pages",
    #     9: "A book that features a character going through menopause",
    #     10: "A book you got for free",
    #     11: "A book mentioned in another book",
    #     12: "A book about a road trip",
    #     13: "A book rated less than three stars on Goodreads",
    #     14: "A book about a nontraditional education",
    #     15: "A book that an AI chatbot recommends based on your favorite book",
    #     16: "A book set in or around a body of water",
    #     17: "A book about a run club",
    #     18: "A book containing magical creatures that aren't dragons",
    #     19: "A highly anticipated read of 2025",
    #     20: "A book that fills a 2024 prompt you'd like to do over (or try out)",
    #     21: "A book where the main character is a politician",
    #     22: "A book about soccer",
    #     23: "A book that is considered healing fiction",
    #     24: "A book with a happily single woman protagonist",
    #     25: "A book where the main character is an immigrant or refugee",
    #     26: "A book where an adult character changes careers",
    #     27: "A book set at a luxury resort",
    #     28: "A book that features an unlikely friendship",
    #     29: "A book about a food truck",
    #     30: "A book that reminds you of your childhood",
    #     31: "A book where music plays an integral part of the storyline",
    #     32: "A book about an overlooked woman in history",
    #     33: "A book featuring an activity on your bucket list",
    #     34: "A book written by an author who is neurodivergent",
    #     35: "A book centering LGBTQ+ characters that isn't about coming out",
    #     36: "A book with silver on the cover or in the title",
    #     37: "Two books with the same title (1)",
    #     38: "Two books with the same title (2)",
    #     39: "A classic you've never read",
    #     40: "A book about chosen family",
    # },
    2026: {
        1: "A book where gardening or a garden is central to the plot",
        2: "A book that features a platonic friendship between a man and woman",
        3: "A book you meant to read in 2025",
        4: "A book that starts with the letter 'Z'",
        5: "A book about women astronauts",
        6: "A book with an overweight main character whose story isn't about losing weight",
        7: "A book about a granny hobby",
        8: "A book about a sexless marriage",
        9: "A book with a 'type C' character",
        10: "A book about a horse or with a horse on the cover",
        11: "A book with a dad as the primary caregiver",
        12: "A book with 'pop' or 'sugar' in the title",
        13: "A book featuring a character with a hidden past",
        14: "A book set in Michigan or written by an author from Michigan",
        15: "A book about new beginnings",
        16: "A book less than 260 pages",
        17: "A book about your favorite event in the Winter Olympics",
        18: "A love story that defies social boundaries",
        19: "A book about teen angst",
        20: "A book with a character who does Pilates or Lagree",
        21: "A book about a bachelorette trip",
        22: "A book about a book club",
        23: "A book you were hoping would fit into a prompt but doesn't",
        24: "A book about postpartum",
        25: "A book that explores influencer culture",
        26: "A book with a character who navigates infertility",
        27: "A book with a character who has curly hair",
        28: "A book about debt",
        29: "A book that takes place during harvesting season",
        30: "A travel ghost story",
        31: "A book that makes you feel FOMO",
        32: "A book with an underwater civilization",
        33: "A book about college",
        34: "A book with a trans or nonbinary protagonist",
        35: "A book that makes you want to travel to Italy",
        36: "A book about a mob (fiction or nonfiction)",
        37: "A book about a pop star",
        38: "A book with any type of fruit on the cover or in the title",
        39: "A book with a character who runs a marathon",
        40: "A book outside your comfort zone",
    },
}

advanced_challenges = {
    # 2025: {
    #     41: "A book by the oldest author in your TBR pile",
    #     42: "A book with a title that starts with the letter Y",
    #     43: "A book that includes a nonverbal character",
    #     44: "A book you have always avoided reading",
    #     45: "A book with a left-handed character",
    #     46: "A book where nature is the antagonist",
    #     47: "A book of interconnected short stories",
    #     48: "A book that features a married couple who don't live together",
    #     49: "A dystopian book with a happy ending",
    #     50: "A book that features a character with chronic pain",
    # },
    2026: {
        41: "A book in a different format than your usual: physical, audio, eBook",
        42: "A book inspired by a real song, album, band, or artist",
        43: "Two books written by real-life partners or spouses (1)",
        44: "Two books written by real-life partners or spouses (2)",
        45: "A book that features birding",
        46: "A sapphic comic",
        47: "A book told entirely through letters",
        48: "A book with a shadow daddy",
        49: "A book with a mention of your zodiac sign",
        50: "A book about Afrofuturism",
    },
}

submitted_books = {
    2024: {
        "me@frieda.dev": [
            {
                "author": "Eric Evans",
                "book_name": "Domain Driven Design",
                "original_number": 47,
                "rating": 4,
            },
            {
                "author": "Cheryl Strayed",
                "book_name": "Tiny Beautiful Things",
                "original_number": 1,
                "rating": 4,
            },
            {
                "author": "Tonio Schachinger",
                "book_name": "Echtzeitalter",
                "original_number": 58,
                "rating": 4,
            },
            {
                "author": "James Nestor",
                "book_name": "Breath",
                "original_number": 55,
                "rating": 5,
            },
            {
                "author": "Gene Kim",
                "book_name": "The Phoenix Project",
                "original_number": 37,
                "rating": 4,
            },
        ]
    }
}
