import functools

# Base de données complète des pays avec leurs drapeaux et noms normalisés en français
FLOWTAG_COUNTRIES = {
    # === EUROPE ===
    'france': ('🇫🇷', 'France'),
    'united kingdom': ('🇬🇧', 'UK'),
    'uk': ('🇬🇧', 'UK'),
    'england': ('🇬🇧', 'UK'),
    'germany': ('🇩🇪', 'Allemagne'),
    'spain': ('🇪🇸', 'Espagne'),
    'italy': ('🇮🇹', 'Italie'),
    'netherlands': ('🇳🇱', 'Pays-Bas'),
    'belgium': ('🇧🇪', 'Belgique'),
    'sweden': ('🇸🇪', 'Suède'),
    'norway': ('🇳🇴', 'Norvège'),
    'denmark': ('🇩🇰', 'Danemark'),
    'switzerland': ('🇨🇭', 'Suisse'),
    'austria': ('🇦🇹', 'Autriche'),
    'poland': ('🇵🇱', 'Pologne'),
    'portugal': ('🇵🇹', 'Portugal'),
    'ireland': ('🇮🇪', 'Irlande'),
    'scotland': ('🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Écosse'),
    'greece': ('🇬🇷', 'Grèce'),
    'romania': ('🇷🇴', 'Roumanie'),
    'ukraine': ('🇺🇦', 'Ukraine'),
    'russia': ('🇷🇺', 'Russie'),
    'czech republic': ('🇨🇿', 'République Tchèque'),
    'hungary': ('🇭🇺', 'Hongrie'),
    'croatia': ('🇭🇷', 'Croatie'),
    'serbia': ('🇷🇸', 'Serbie'),
    'finland': ('🇫🇮', 'Finlande'),
    'iceland': ('🇮🇸', 'Islande'),
    'luxembourg': ('🇱🇺', 'Luxembourg'),
    'malta': ('🇲🇹', 'Malte'),
    'cyprus': ('🇨🇾', 'Chypre'),
    
    # === AMÉRIQUE DU NORD ===
    'usa': ('🇺🇸', 'USA'),
    'united states': ('🇺🇸', 'USA'),
    'canada': ('🇨🇦', 'Canada'),
    'mexico': ('🇲🇽', 'Mexique'),
    
    # === AMÉRIQUE LATINE ===
    'brazil': ('🇧🇷', 'Brésil'),
    'argentina': ('🇦🇷', 'Argentine'),
    'colombia': ('🇨🇴', 'Colombie'),
    'chile': ('🇨🇱', 'Chili'),
    'peru': ('🇵🇪', 'Pérou'),
    'venezuela': ('🇻🇪', 'Venezuela'),
    'ecuador': ('🇪🇨', 'Équateur'),
    'bolivia': ('🇧🇴', 'Bolivie'),
    'paraguay': ('🇵🇾', 'Paraguay'),
    'uruguay': ('🇺🇾', 'Uruguay'),
    'puerto rico': ('🇵🇷', 'Porto Rico'),
    'dominican republic': ('🇩🇴', 'République Dominicaine'),
    'cuba': ('🇨🇺', 'Cuba'),
    'jamaica': ('🇯🇲', 'Jamaïque'),
    'trinidad': ('🇹🇹', 'Trinité-et-Tobago'),
    'barbados': ('🇧🇧', 'Barbade'),
    'haiti': ('🇭🇹', 'Haïti'),
    'panama': ('🇵🇦', 'Panama'),
    'costa rica': ('🇨🇷', 'Costa Rica'),
    'guatemala': ('🇬🇹', 'Guatemala'),
    'honduras': ('🇭🇳', 'Honduras'),
    'nicaragua': ('🇳🇮', 'Nicaragua'),
    'el salvador': ('🇸🇻', 'Salvador'),
    
    # === AFRIQUE ===
    'south africa': ('🇿🇦', 'Afrique du Sud'),
    'nigeria': ('🇳🇬', 'Nigéria'),
    'egypt': ('🇪🇬', 'Égypte'),
    'morocco': ('🇲🇦', 'Maroc'),
    'algeria': ('🇩🇿', 'Algérie'),
    'tunisia': ('🇹🇳', 'Tunisie'),
    'kenya': ('🇰🇪', 'Kenya'),
    'ethiopia': ('🇪🇹', 'Éthiopie'),
    'ghana': ('🇬🇭', 'Ghana'),
    'senegal': ('🇸🇳', 'Sénégal'),
    'ivory coast': ('🇨🇮', 'Côte d\'Ivoire'),
    'cameroon': ('🇨🇲', 'Cameroun'),
    'mali': ('🇲🇱', 'Mali'),
    'congo': ('🇨🇩', 'Congo'),
    'angola': ('🇦🇴', 'Angola'),
    'madagascar': ('🇲🇬', 'Madagascar'),
    'mozambique': ('🇲🇿', 'Mozambique'),
    'tanzania': ('🇹🇿', 'Tanzanie'),
    'uganda': ('🇺🇬', 'Ouganda'),
    'zimbabwe': ('🇿🇼', 'Zimbabwe'),
    
    # === ASIE ===
    'japan': ('🇯🇵', 'Japon'),
    'china': ('🇨🇳', 'Chine'),
    'south korea': ('🇰🇷', 'Corée du Sud'),
    'korea': ('🇰🇷', 'Corée du Sud'),
    'india': ('🇮🇳', 'Inde'),
    'thailand': ('🇹🇭', 'Thaïlande'),
    'indonesia': ('🇮🇩', 'Indonésie'),
    'philippines': ('🇵🇭', 'Philippines'),
    'vietnam': ('🇻🇳', 'Viêt Nam'),
    'malaysia': ('🇲🇾', 'Malaisie'),
    'singapore': ('🇸🇬', 'Singapour'),
    'pakistan': ('🇵🇰', 'Pakistan'),
    'bangladesh': ('🇧🇩', 'Bangladesh'),
    'sri lanka': ('🇱🇰', 'Sri Lanka'),
    'nepal': ('🇳🇵', 'Népal'),
    'myanmar': ('🇲🇲', 'Myanmar'),
    'taiwan': ('🇹🇼', 'Taïwan'),
    'hong kong': ('🇭🇰', 'Hong Kong'),
    
    # === MOYEN-ORIENT ===
    'turkey': ('🇹🇷', 'Turquie'),
    'israel': ('🇮🇱', 'Israël'),
    'lebanon': ('🇱🇧', 'Liban'),
    'iran': ('🇮🇷', 'Iran'),
    'iraq': ('🇮🇶', 'Irak'),
    'saudi arabia': ('🇸🇦', 'Arabie Saoudite'),
    'uae': ('🇦🇪', 'Émirats Arabes Unis'),
    'jordan': ('🇯🇴', 'Jordanie'),
    'syria': ('🇸🇾', 'Syrie'),
    'qatar': ('🇶🇦', 'Qatar'),
    'kuwait': ('🇰🇼', 'Koweït'),
    'bahrain': ('🇧🇭', 'Bahreïn'),
    'oman': ('🇴🇲', 'Oman'),
    'yemen': ('🇾🇪', 'Yémen'),
    
    # === OCÉANIE ===
    'australia': ('🇦🇺', 'Australie'),
    'new zealand': ('🇳🇿', 'Nouvelle-Zélande'),
    'fiji': ('🇫🇯', 'Fidji'),
    'papua new guinea': ('🇵🇬', 'Papouasie-Nouvelle-Guinée'),
    'new caledonia': ('🇳🇨', 'Nouvelle-Calédonie'),
    'tahiti': ('🇵🇫', 'Polynésie Française'),
}

# Mapping pour la détection du pays par la langue des paroles
LANGUAGE_TO_COUNTRY = {
    'fr': ('🇫🇷', 'France'),
    'french': ('🇫🇷', 'France'),
    'en': ('🇺🇸', 'USA'),
    'english': ('🇺🇸', 'USA'),
    'es': ('🇪🇸', 'Espagne'),
    'spanish': ('🇪🇸', 'Espagne'),
    'pt': ('🇧🇷', 'Brésil'),
    'portuguese': ('🇧🇷', 'Brésil'),
    'it': ('🇮🇹', 'Italie'),
    'italian': ('🇮🇹', 'Italie'),
    'de': ('🇩🇪', 'Allemagne'),
    'german': ('🇩🇪', 'Allemagne'),
    'ja': ('🇯🇵', 'Japon'),
    'japanese': ('🇯🇵', 'Japon'),
    'ko': ('🇰🇷', 'Corée du Sud'),
    'korean': ('🇰🇷', 'Corée du Sud'),
    'ar': ('🇪🇬', 'Égypte'),
    'arabic': ('🇪🇬', 'Égypte'),
    'hi': ('🇮🇳', 'Inde'),
    'hindi': ('🇮🇳', 'Inde'),
    'ru': ('🇷🇺', 'Russie'),
    'russian': ('🇷🇺', 'Russie'),
    'nl': ('🇳🇱', 'Pays-Bas'),
    'dutch': ('🇳🇱', 'Pays-Bas'),
    'sv': ('🇸🇪', 'Suède'),
    'swedish': ('🇸🇪', 'Suède'),
}

# Trie les clés de pays par longueur décroissante pour éviter les correspondances partielles (ex: 'uk' dans 'ukraine')
_sorted_country_keys = sorted(FLOWTAG_COUNTRIES.keys(), key=len, reverse=True)

@functools.lru_cache(maxsize=1024)
def detect_country(artist_name, language=None):
    """
    Détecte le pays d'origine d'un artiste avec une mise en cache.
    La détection se fait par nom, puis par langue, avec une valeur par défaut.
    """
    if not artist_name:
        return ('🌍', 'International')

    normalized = artist_name.lower().strip()

    # 1. Recherche d'une correspondance exacte (ex: 'Daft Punk')
    if normalized in FLOWTAG_COUNTRIES:
        return FLOWTAG_COUNTRIES[normalized]

    # 2. Recherche par mots-clés dans le nom (ex: 'Artist from Spain')
    # Les clés sont triées par longueur pour privilégier 'united kingdom' avant 'uk'.
    for country_key in _sorted_country_keys:
        if country_key in normalized:
            return FLOWTAG_COUNTRIES[country_key]

    # 3. Détection par la langue des paroles si disponible
    if language and language.lower() in LANGUAGE_TO_COUNTRY:
        return LANGUAGE_TO_COUNTRY[language.lower()]

    # 4. Valeur par défaut si aucune correspondance n'est trouvée
    return ('🌍', 'International') 