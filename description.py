import sys
import json
import pgf
import re
import requests
from datetime import datetime

GRAMMAR_PLACE = '../grammars/Descriptions.pgf'
grammar_place = pgf.readPGF(GRAMMAR_PLACE)
english_place = grammar_place.languages['DescriptionsEng']
chinese_place = grammar_place.languages['DescriptionsChi']

GRAMMAR_HUMAN = '../grammars/HumanDescriptions.pgf'
grammar_human = pgf.readPGF(GRAMMAR_HUMAN)
chinese_human = grammar_human.languages['HumanDescriptionsChi']
english_human = grammar_human.languages['HumanDescriptionsEng']
# bengali_human = grammar_human.languages['HumanDescriptionsBen']

GRAMMAR_CREATURE = '../grammars/CreatureDescriptions.pgf'
grammar_creature = pgf.readPGF(GRAMMAR_CREATURE)
creature_eng = grammar_creature.languages['CreatureDescriptionsEng']
creature_chi = grammar_creature.languages['CreatureDescriptionsChi']



# dictionary of cities, city kinds, provinces, and countries

def extract_qid_functions(filepath, typename):
    with open(filepath, encoding="utf-8-sig") as f:  # 自动去除 BOM
        text = f.read()
    pattern = re.compile(
        rf'(?:fun\s+)?(Q\d+)_([^\s:]+)\s*:\s*{re.escape(typename)}\s*;', 
        re.MULTILINE
    )
    qid_map = {}
    for qid, suffix in pattern.findall(text):
        func_name = f"{qid}_{suffix}"
        qid_map[qid] = func_name
    return qid_map

cities = extract_qid_functions("../grammars/Cities.gf", "City")
city_kinds = extract_qid_functions("../grammars/CityKinds.gf", "CityKinds")
provinces = extract_qid_functions("../grammars/Provinces.gf", "Province")
countries = extract_qid_functions("../grammars/Countries.gf", "Country")
waterbodies = extract_qid_functions("../grammars/Waterbodies.gf", "Waterbody")
professions = extract_qid_functions("../grammars/Professions.gf", "Profession")
families = extract_qid_functions("../grammars/Family.gf", "Family")
genera = extract_qid_functions("../grammars/Genus.gf", "Genus")


# maps for ancient to modern country names
ancient_to_modern = {
    'Q43287_German_Empire_Country': 'Q183_Germany_Country',
    'Q29999_Kingdom_of_the_Netherlands_Country': 'Q55_Netherlands_Country',
    'Q153015_Kingdom_of_Saxony_Country': 'Q183_Germany_Country',
    'Q27306_Kingdom_of_Prussia_Country': 'Q183_Germany_Country',
    'Q38872_Prussia_Country': 'Q183_Germany_Country',
    'Q1206012_German_Reich_Country': 'Q183_Germany_Country',
    'Q10985258_German_Empire_Country': 'Q183_Germany_Country',
    'Q41304_Weimar_Republic_Country': 'Q183_Germany_Country',
    'Q154741_Confederation_of_the_Rhine_Country': 'Q183_Germany_Country',
    'Q155570_Saxe_Weimar_Eisenach_Country': 'Q183_Germany_Country',
    'Q186320_Grand_Duchy_of_Baden_Country': 'Q183_Germany_Country',
    'Q34266_Russian_Empire_Country': 'Q159_Russia_Country',
    'Q552033_Bavaria_Munich_Country': 'Q183_Germany_Country',
    'Q164079_Kingdom_of_Hanover_Country': 'Q183_Germany_Country',
    'Q186096_Tsardom_of_Russia_Country': 'Q159_Russia_Country',
    'Q326029_Duchy_of_Brunswick_Country': 'Q183_Germany_Country',
    'Q42199_Principality_of_Ansbach_Country': 'Q183_Germany_Country',
    'Q693669_Grand_Duchy_of_Oldenburg_Country': 'Q183_Germany_Country',
    'Q28513_Austria_Hungary_Country': 'Q40_Austria_Country',
    'Q173065_Kingdom_of_Naples_Country': 'Q38_Italy_Country',
    'Q155019_Duchy_of_Lorraine_Country': 'Q142_France_Country',
    'Q533534_Cisleithania_Country': 'Q40_Austria_Country',
    'Q129286_British_Raj_Country': 'Q145_United_Kingdom_Country',
    'Q174193_United_Kingdom_of_Great_Britain_and_Ireland_Country': 'Q145_United_Kingdom_Country',
    'Q172579_Kingdom_of_Italy_Country': 'Q38_Italy_Country',
    'Q389004_Wallachia_Country': 'Q218_Romania_Country',
    'Q1031430_Habsburg_Netherlands_Country': 'Q55_Netherlands_Country',
    'Q11750528_Duchy_of_Moscow_Country': 'Q159_Russia_Country',
    'Q153529_Duchy_of_Milan_Country': 'Q38_Italy_Country',
    'Q49697_Liu_Song_dynasty_Country': 'Q148_China_Country',
    'Q274488_Eastern_Wu_Country': 'Q148_China_Country',
    'Q171150_Kingdom_of_Hungary_Country': 'Q28_Hungary_Country',
    'Q203493_Kingdom_of_Romania_Country': 'Q218_Romania_Country',
    'Q45670_Kingdom_of_Portugal_Country': 'Q45_Portugal_Country',
    'Q154849_Grand_Duchy_of_Tuscany_Country': 'Q38_Italy_Country',
    'Q70972_Kingdom_of_France_Country': 'Q142_France_Country',
    'Q7462_Song_dynasty_Country': 'Q148_China_Country',
    'Q169460_Miletus_Country': 'Q41_Greece_Country',
    'Q161885_Kingdom_of_Great_Britain_Country': 'Q145_United_Kingdom_Country',
    'Q215530_Kingdom_of_Ireland_Country': 'Q145_United_Kingdom_Country',
    'Q230791_Kingdom_of_Scotland_Country': 'Q145_United_Kingdom_Country',
    'Q23366230_Republic_of_Geneva_Country': 'Q39_Switzerland_Country',
    'Q320930_Cao_Wei_Country': 'Q148_China_Country',
    'Q64576860_Lordship_of_Bologna_Country': 'Q38_Italy_Country',
    'Q170072_Dutch_Republic_Country': 'Q55_Netherlands_Country',
    'Q1147037_Eastern_Han_Country': 'Q148_China_Country',
    'Q148540_Republic_of_Florence_Country': 'Q38_Italy_Country',
    'Q221457_Congress_Poland_Country': 'Q36_Poland_Country',
    'Q217196_Crown_of_Castile_Country': 'Q29_Spain_Country',
    'Q7313_Yuan_dynasty_Country': 'Q148_China_Country',
    'Q204920_Crown_of_Aragon_Country': 'Q29_Spain_Country',
    'Q2252973_Duchy_of_Florence_Country': 'Q38_Italy_Country',
    'Q1649871_Kingdom_of_Poland_Country': 'Q36_Poland_Country',
    'Q47261_Duchy_of_Bavaria_Country': 'Q183_Germany_Country',
    'Q435583_Old_Swiss_Confederacy_Country': 'Q39_Switzerland_Country',
    'Q4420718_ancient_Syracuse_Country': 'Q41_Greece_Country',
    'Q1365493_Republic_of_Pisa_Country': 'Q38_Italy_Country',
    'Q2227570_Duchy_of_Wurttemberg_Country': 'Q183_Germany_Country',
    'Q22_Scotland_Country': 'Q145_United_Kingdom_Country',
    'Q1072949_Western_Han_Country': 'Q148_China_Country',
    'Q13580795_Samos_Country': 'Q41_Greece_Country',
    'Q153136_Habsburg_monarchy_Country': 'Q40_Austria_Country',
    'Q158151_Saxe_Altenburg_Country': 'Q183_Germany_Country',
    'Q1233672_County_of_Barcelona_Country': 'Q29_Spain_Country',
    'Q11768_Ancient_Egypt_Country': 'Q79_Egypt_Country',
    'Q871091_British_Malaya_Country': 'Q145_United_Kingdom_Country',
    'Q1236847_Lordship_of_Kniphausen_Country': 'Q183_Germany_Country',
    'Q694594_Duchy_of_Bremen_and_Verden_Country': 'Q183_Germany_Country',
    'Q693551_Landgraviate_of_Hesse_Darmstadt_Country': 'Q183_Germany_Country',
    'Q3139179_Hohenlohe_Kirchberg_Country': 'Q183_Germany_Country',
    'Q561334_Prince_Bishopric_of_Bamberg_Country': 'Q183_Germany_Country',
    'Q16957_German_Democratic_Republic_Country': 'Q183_Germany_Country',
    'Q13427044_Prince_Bishopric_of_Wurzburg_Country': 'Q183_Germany_Country',
    'Q20135_Grand_Duchy_of_Hesse_Country': 'Q183_Germany_Country',
    'Q696640_Duchy_of_Pomerania_Country': 'Q183_Germany_Country',
    'Q2281221_Principality_of_Orange_Country': 'Q142_France_Country',
    'Q43048_Rhodes_Country': 'Q41_Greece_Country',
    'Q207272_Second_Polish_Republic_Country': 'Q36_Poland_Country',
    'Q330533_Seventeen_Provinces_Country': 'Q55_Netherlands_Country',
    'Q9903_Ming_dynasty_Country': 'Q148_China_Country',
    'Q33946_Czechoslovakia_Country': 'Q213_Czech_Republic_Country',
    'Q188712_Empire_of_Japan_Country': 'Q17_Japan_Country',
    'Q8733_Qing_dynasty_Country': 'Q148_China_Country',
    'Q11225429_Thebes_Country': 'Q41_Greece_Country',
    'Q211274_Polish_People_s_Republic_Country': 'Q36_Poland_Country',
    'Q15102440_Kingdom_of_Serbs_Croats_and_Slovenes_Country': 'Q36704_Yugoslavia_Country',
    'Q241748_Kingdom_of_Serbia_Country': 'Q403_Serbia_Country',
    'Q4734309_Alokopennesos_Country': 'Q41_Greece_Country',
    'Q11772_Ancient_Greece_Country': 'Q41_Greece_Country',
    'Q12560_Ottoman_Empire_Country': 'Q43_Turkey_Country',
    'Q42585_Kingdom_of_Bohemia_Country': 'Q213_Czech_Republic_Country',
    'Q13526919_Kroton_Country': 'Q41_Greece_Country',
    'Q622783_Spanish_Netherlands_Country': 'Q29_Spain_Country',
    'Q70802_French_Third_Republic_Country': 'Q142_France_Country',
    'Q684030_Principality_of_Serbia_Country': 'Q403_Serbia_Country',
    'Q180393_Kingdom_of_the_Two_Sicilies_Country': 'Q38_Italy_Country',
    'Q551067_Northern_Zhou_Country': 'Q148_China_Country',
    'Q9683_Tang_dynasty_Country': 'Q148_China_Country',
    'Q7209_Han_dynasty_Country': 'Q148_China_Country',
    'Q5066_Jin_dynasty_Country': 'Q148_China_Country',
    'Q13498_Taranto_Country': 'Q38_Italy_Country',
    'Q2022162_Kingdom_of_Pergamon_Country': 'Q41_Greece_Country',
    'Q252580_Duchy_of_Modena_and_Reggio_Country': 'Q38_Italy_Country',
    'Q174306_Republic_of_Genoa_Country': 'Q38_Italy_Country',
    'Q80702_Spanish_Empire_Country': 'Q29_Spain_Country',
    'Q1233764_Doric_hexapolis_Country': 'Q41_Greece_Country',
    'Q2305208_Russian_Socialist_Federative_Soviet_Republic_Country': 'Q159_Russia_Country',
    'Q2396442_Kingdom_of_Galicia_and_Lodomeria_Country': 'Q36_Poland_Country',
    'Q319460_Northern_Song_dynasty_Country': 'Q148_China_Country',
    'Q83286_Socialist_Federal_Republic_of_Yugoslavia_Country': 'Q36704_Yugoslavia_Country',
    'Q49696_Northern_and_Southern_dynasties_Country': 'Q148_China_Country',
    'Q3149991_Ancient_India_Country': 'Q668_India_Country',
    'Q123559_al_Andalus_Country': 'Q29_Spain_Country',
    'Q33296_Mughal_Empire_Country': 'Q668_India_Country',
    'Q656954_Soli_Country': 'Q41_Greece_Country',
    'Q6681_Crotone_Country': 'Q38_Italy_Country',
    'Q704300_Free_City_of_Frankfurt_Country': 'Q183_Germany_Country',
    'Q256961_Electorate_of_Bavaria_Country': 'Q183_Germany_Country',
    'Q836680_Duchy_of_Nassau_Country': 'Q183_Germany_Country',
    'Q15864_United_Kingdom_of_the_Netherlands_Country': 'Q55_Netherlands_Country',
    'Q30623_Manchukuo_Country': 'Q148_China_Country',
    'Q7318_Nazi_Germany_Country': 'Q183_Germany_Country',
    'Q165154_Kingdom_of_Sardinia_Country': 'Q38_Italy_Country',
    'Q170770_Grand_Principality_of_Moscow_Country': 'Q159_Russia_Country',
    'Q212439_Cossack_Hetmanate_Country': 'Q212_Ukraine_Country',
    'Q133356_Ukrainian_Soviet_Socialist_Republic_Country': 'Q212_Ukraine_Country',
    'Q702224_Duchy_of_Carinthia_Country': 'Q40_Austria_Country',
    'Q243610_Ukrainian_People_s_Republic_Country': 'Q212_Ukraine_Country',
    'Q42406_English_people_Country': 'Q145_United_Kingdom_Country',
    'Q28025_Ryukyu_Kingdom_Country': 'Q17_Japan_Country',
    'Q26234937_First_Syrian_Republic_Country': 'Q858_Syria_Country',
    'Q124943_Kingdom_of_Egypt_Country': 'Q79_Egypt_Country',
    'Q426025_Duchy_of_Savoy_Country': 'Q38_Italy_Country',
    'Q12060881_Chinese_Empire_Country': 'Q148_China_Country',
    'Q2184_Russian_Soviet_Federative_Socialist_Republic_Country': 'Q159_Russia_Country',
    'Q1290149_Federal_People_s_Republic_of_Yugoslavia_Country': 'Q36704_Yugoslavia_Country',
    'Q151624_German_Confederation_Country': 'Q183_Germany_Country',
    'Q188586_Kingdom_of_Sicily_Country': 'Q38_Italy_Country',
    'Q158445_Grand_Duchy_of_Mecklenburg_Schwerin_Country': 'Q183_Germany_Country',
    'Q200464_Portuguese_Empire_Country': 'Q45_Portugal_Country',
    'Q209857_Kingdom_of_LombardyVenetia_Country': 'Q38_Italy_Country',
    'Q1054923_British_Hong_Kong_Country': 'Q148_China_Country',
    'Q713750_West_Germany_Country': 'Q183_Germany_Country',
    'Q264970_Anhalt_Kothen_Country': 'Q183_Germany_Country',
    'Q2162698_Duchy_of_Bohemia_Country': 'Q213_Czech_Republic_Country',
    'Q2670751_Margraviate_of_Moravia_Country': 'Q213_Czech_Republic_Country',
    'Q205662_Tokugawa_shogunate_Country': 'Q17_Japan_Country',
    'Q12738_Neuchatel_Country': 'Q39_Switzerland_Country',
    "Q156199_Electorate_of_Saxony_Country": "Q183_Germany_Country" ,
    "Q12548_Holy_Roman_Empire_Country": "Q183_Germany_Country"}

def is_type_via_sparql(qid, target_qid):
    """
    Use SPARQL to check if a Wikidata entity (qid) is an instance of or subclass (via P31/P279*) 
    of a target entity type (target_qid).

    Args:
        qid (str): The QID of the entity to check (e.g., "Q8686" for Shanghai).
        target_qid (str): The QID of the target type (e.g., "Q515" for city).

    Returns:
        bool: True if the entity is an instance or subclass of the target type, otherwise False.
    """
    url = "https://query.wikidata.org/sparql"
    query = f"""
    ASK WHERE {{
      wd:{qid} wdt:P31/wdt:P279* wd:{target_qid} .
    }}
    """
    headers = {
        "Accept": "application/sparql-results+json"
    }
    resp = requests.get(url, params={'query': query}, headers=headers, timeout=10)
    data = resp.json()
    return data['boolean']

def get_entity_type(entity):
    """
    Determine the high-level type of a Wikidata entity by checking its QID against 
    common target types (human, city, university, island, lake, etc.) using SPARQL.

    Args:
        entity (dict): The Wikidata entity JSON object.

    Returns:
        str: The determined entity type, such as 'human', 'city', 'university', etc.
    """
    qid = entity.get('id')
    if is_type_via_sparql(qid, 'Q5'):
        return 'human'
    if is_type_via_sparql(qid, 'Q515'):
        return 'city'
    if is_type_via_sparql(qid, 'Q3918'):
        return 'university'
    if is_type_via_sparql(qid, 'Q23442'):
        return 'island'
    if is_type_via_sparql(qid, 'Q23397'):
        return 'lake'
    if is_type_via_sparql(qid, 'Q16521'):   
        return 'taxon'
    # Add more types if needed
    return 'unknown'

def get_wikidata_entity(qid):
    url = f'https://www.wikidata.org/wiki/Special:EntityData/{qid}.json'
    resp = requests.get(url, timeout=10)
    data = resp.json()
    return data['entities'][qid]

# get the first qid for P31 (instance of) 
def get_first_instance_of_qid(entity):
    claims = entity.get('claims', {})
    p31_claims = claims.get('P31', [])
    instance_qid = None

    for claim in p31_claims:
        mainsnak = claim.get('mainsnak', {})
        datavalue = mainsnak.get('datavalue', {})
        value = datavalue.get('value', {})
        qid = value.get('id')
        if qid is not None:
            instance_qid = qid
            break  # 找到第一个就跳出

    return instance_qid

#     Map a Wikidata country QID to the corresponding GF country function name, using modern country mapping if the QID refers to a historical country.
def get_country_fun_from_qid(qid):
    if not qid:
        return None

    
    func_name = countries.get(qid)
    if not func_name:
        return None

    
    mapped = ancient_to_modern.get(func_name)
    if mapped:
        mapped_qid = mapped.split('_')[0]
        return countries.get(mapped_qid, mapped)
    
    return func_name

# get the first qid for P17 (country) 
def get_first_country_qid(entity):
    claims = entity.get('claims', {})
    p17_claims = claims.get('P17', [])
    country_qid = None

    for claim in p17_claims:
        mainsnak = claim.get('mainsnak', {})
        datavalue = mainsnak.get('datavalue', {})
        value = datavalue.get('value', {})
        qid = value.get('id')
        if qid is not None:
            country_qid = qid
            break  # 找到第一个就跳出

    return country_qid

# get the located province qid
# def get_city_located_province_qid(entity, province_qids, country_qids):
#     self_qid = entity.get('id')
#     if self_qid in province_qids:
#         return self_qid

#     claims = entity.get('claims', {}).get('P131', [])
#     for claim in claims:
#         mainsnak = claim.get('mainsnak', {})
#         datavalue = mainsnak.get('datavalue', {})
#         value = datavalue.get('value', {})
#         qid = value.get('id')

#         if qid in country_qids:
#             return None

#         if qid in province_qids:
#             return qid

#     return None


def get_city_located_province_qid(entity, province_qids, country_qids):
    visited = set()
    MAX_DEPTH = 5  # 防止无限递归
    candidates = []

    def _find_province(qid, depth):
        if qid in visited or depth > MAX_DEPTH:
            return
        visited.add(qid)

        if qid in province_qids:
            candidates.append((qid, depth))
            return
        if qid in country_qids:
            return

        parent_entity = get_wikidata_entity(qid)
        claims = parent_entity.get('claims', {}).get('P131', [])
        for claim in claims:
            mainsnak = claim.get('mainsnak', {})
            datavalue = mainsnak.get('datavalue', {})
            value = datavalue.get('value', {})
            parent_qid = value.get('id')
            if parent_qid:
                _find_province(parent_qid, depth + 1)

    self_qid = entity.get('id')
    if self_qid in province_qids:
        return self_qid

    claims = entity.get('claims', {}).get('P131', [])
    for claim in claims:
        mainsnak = claim.get('mainsnak', {})
        datavalue = mainsnak.get('datavalue', {})
        value = datavalue.get('value', {})
        qid = value.get('id')
        if qid:
            _find_province(qid, 1)

    if candidates:
        # 取深度最小的那个省
        candidates.sort(key=lambda x: x[1])
        return candidates[0][0]
    return None



# check if the city is capital
def get_city_capital_of_qid_and_type(entity, province_qids, country_qids):
    now = datetime.now().year
    claims = entity.get('claims', {})
    p1376_claims = claims.get('P1376', [])

    for claim in p1376_claims:
        # === 判断时间是否仍有效 ===
        qualifiers = claim.get('qualifiers', {})
        start = qualifiers.get('P580', [])
        end = qualifiers.get('P582', [])

        def extract_year(time_obj):
            try:
                time_str = time_obj.get('datavalue', {}).get('value', {}).get('time', '')
                return int(time_str[1:5]) if time_str else None
            except:
                return None

        start_year = extract_year(start[0]) if start else None
        end_year = extract_year(end[0]) if end else None

        if (start_year and now < start_year) or (end_year and now > end_year):
            continue  # 该断言不在当前年份范围内，跳过

        # === 提取 QID 并判断类型 ===
        mainsnak = claim.get('mainsnak', {})
        datavalue = mainsnak.get('datavalue', {})
        value = datavalue.get('value', {})
        qid = value.get('id')

        if qid:
            if qid in country_qids:
                return qid, 'country'
            elif qid in province_qids:
                return qid, 'province'

    return None, None

# get the located city qid
# this function is recursive, it will find the city qid in the parent qids
def get_university_located_city_qid(entity, city_qids):
    visited = set()
    MAX_DEPTH = 5  
    def _find_city(qid, depth):
        if qid in visited or depth > MAX_DEPTH:
            return None
        visited.add(qid)
        if qid in city_qids:
            return qid
        up_entity = get_wikidata_entity(qid)
        claims = up_entity.get('claims', {})
        p131s = claims.get('P131', [])
        for claim in p131s:
            mainsnak = claim.get('mainsnak', {})
            datavalue = mainsnak.get('datavalue', {})
            value = datavalue.get('value', {})
            up_qid = value.get('id')
            if up_qid:
                result = _find_city(up_qid, depth + 1)
                if result:
                    return result
        return None

    claims = entity.get('claims', {})
    p131_claims = claims.get('P131', [])
    for claim in p131_claims:
        mainsnak = claim.get('mainsnak', {})
        datavalue = mainsnak.get('datavalue', {})
        value = datavalue.get('value', {})
        qid = value.get('id')
        if qid:
            result = _find_city(qid, 1)
            if result:
                return result
    return None

# get the country qid
def get_university_country_qid(entity):
    claims = entity.get('claims', {})
    p17_claims = claims.get('P17', [])
    for claim in p17_claims:
        mainsnak = claim.get('mainsnak', {})
        datavalue = mainsnak.get('datavalue', {})
        value = datavalue.get('value', {})
        qid = value.get('id')
        if qid:
            return qid
    return None

# check if the university is private or public
public_qids = {'Q875538', 'Q62078547'}     # public university
private_qids = {'Q902104', 'Q23002054'}    # private university

def get_university_type(entity, public_qids, private_qids):
    claims = entity.get('claims', {})
    p31_claims = claims.get('P31', [])
    for claim in p31_claims:
        mainsnak = claim.get('mainsnak', {})
        datavalue = mainsnak.get('datavalue', {})
        value = datavalue.get('value', {})
        qid = value.get('id')
        if qid in public_qids:
            return 'public'
        if qid in private_qids:
            return 'private'
    return None

# founded year
def get_university_foundation_year(entity):
    claims = entity.get('claims', {})
    p571_claims = claims.get('P571', [])
    for claim in p571_claims:
        mainsnak = claim.get('mainsnak', {})
        datavalue = mainsnak.get('datavalue', {})
        value = datavalue.get('value', {})
        time_str = value.get('time')
        if time_str and len(time_str) >= 5:
            return time_str[1:5]
    return None

# waterbody
def get_single_body_of_water_qid(entity):
    claims = entity.get('claims', {})
    p206_claims = claims.get('P206', [])

    water_qids = set()
    for claim in p206_claims:
        mainsnak = claim.get('mainsnak', {})
        datavalue = mainsnak.get('datavalue', {})
        value = datavalue.get('value', {})
        qid = value.get('id')
        if qid:
            water_qids.add(qid)

    if len(water_qids) == 1:
        return True, next(iter(water_qids))  
    else:
        return False, None




# functions for building humans

# get gender
def get_gender_str(entity):
    claims = entity.get('claims', {})
    p21 = claims.get('P21', [])
    if not p21:
        return "unknown"
    mainsnak = p21[0].get('mainsnak', {})
    datavalue = mainsnak.get('datavalue', {})
    value = datavalue.get('value', {})
    qid = value.get('id')
    if qid == 'Q6581097':
        return "male"
    if qid == 'Q6581072':
        return "female"
    return "unknown"

# get labels
def get_name(entity):
    return entity.get('labels', {}).get('en', {}).get('value', '')


def get_birth_year(entity):
    claims = entity.get('claims', {})
    p569 = claims.get('P569', [])
    if not p569:
        return None
    mainsnak = p569[0].get('mainsnak', {})
    datavalue = mainsnak.get('datavalue', {})
    value = datavalue.get('value', {})
    time = value.get('time', '')
    if time.startswith('+'):
        return time[1:5]
    return None

def get_citizenship_qid(entity):
    p27 = entity.get('claims', {}).get('P27', [])
    if not p27:
        return None
    return p27[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')

def get_death_year(entity):
    claims = entity.get('claims', {})
    p570 = claims.get('P570', [])
    if not p570:
        return None
    mainsnak = p570[0].get('mainsnak', {})
    datavalue = mainsnak.get('datavalue', {})
    value = datavalue.get('value', {})
    time = value.get('time', '')
    if time.startswith('+'):
        return time[1:5]
    return None

def get_birthplace_qid(entity):
    claims = entity.get('claims', {})
    p19 = claims.get('P19', [])
    if not p19:
        return None
    mainsnak = p19[0].get('mainsnak', {})
    datavalue = mainsnak.get('datavalue', {})
    value = datavalue.get('value', {})
    return value.get('id')

def get_country_of_place_at_year(place_qid, year):
    url = f'https://www.wikidata.org/wiki/Special:EntityData/{place_qid}.json'
    resp = requests.get(url, timeout=10)
    data = resp.json()
    claims = data['entities'][place_qid].get('claims', {})
    p17 = claims.get('P17', [])

    for claim in p17:
        snak = claim.get('mainsnak', {})
        if snak.get('snaktype') != 'value':
            continue
        qid = snak.get('datavalue', {}).get('value', {}).get('id')

        qualifiers = claim.get('qualifiers', {})
        from_year = to_year = None

        if 'P580' in qualifiers:
            from_time = qualifiers['P580'][0]['datavalue']['value']['time']
            from_year = int(from_time[1:5])  # "+1871-01-01T00:00:00Z" → 1871

        if 'P582' in qualifiers:
            to_time = qualifiers['P582'][0]['datavalue']['value']['time']
            to_year = int(to_time[1:5])  # "+1918-11-09T00:00:00Z" → 1918

        if from_year and to_year and from_year <= int(year) <= to_year:
            return qid
        if from_year and int(year) >= from_year:
            return qid
        if to_year and int(year) <= to_year:
            return qid

    if p17:
        snak = p17[0].get('mainsnak', {})
        return snak.get('datavalue', {}).get('value', {}).get('id')

    return None

def build_year_expr(birth, death):
    if birth and death:
        return f'(BornAndDied "{birth}" "{death}")'
    elif birth:
        return f'(OnlyBorn "{birth}")'
    elif death:
        return f'(OnlyDied "{death}")'
    else:
        return 'NoBirthOrDeath'

def english_to_bangla_number(input_str):
    eng_to_bangla = {
        '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
        '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'
    }
    input_str = str(input_str)
    return ''.join(eng_to_bangla.get(ch, ch) for ch in input_str)

def build_bangla_year_expr(birth, death):
    if birth:
        birth = english_to_bangla_number(birth)
    if death:
        death = english_to_bangla_number(death)
    return build_year_expr(birth, death)

def get_profession_qids(entity, max_num=3):
    claims = entity.get('claims', {}).get('P106', [])
    qids = []
    for claim in claims:
        qid = claim.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')
        if qid:
            qids.append(qid)
        if len(qids) >= max_num:
            break
    return qids

def get_profession_fun_from_qid(qid):
    return professions.get(qid)

def build_profession_expr(prof_qids):
    prof_funs = [get_profession_fun_from_qid(qid) for qid in prof_qids if get_profession_fun_from_qid(qid)]
    if not prof_funs:
        return ValueError("no profession found for the given QIDs")

    elif len(prof_funs) == 1:
        # 用 BaseProfession p1 p1 生成单元素列表
        return prof_funs[0]
    elif len(prof_funs) == 2:
        # BaseProfession p1 p2
        return f"ConjProfession (BaseProfession {prof_funs[0]} {prof_funs[1]})"
    else:
        # 三个及以上，用 ConsProfession 拼成列表，然后 ConjProfession
        # ConsProfession p (BaseProfession p2 p3)
        return f"ConjProfession (ConsProfession {prof_funs[0]} (BaseProfession {prof_funs[1]} {prof_funs[2]}))"


def find_nearest_taxon_qid(qid, dict_):
    visited = set()
    while qid and qid not in dict_ and qid not in visited:
        visited.add(qid)
        entity = get_wikidata_entity(qid)
        claims = entity.get('claims', {})
        p171_claims = claims.get('P171', [])
        if not p171_claims:
            return None
        qid = p171_claims[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')
    return qid if qid in dict_ else None

def build_species_description_expr(species_entity):

    claims = species_entity.get('claims', {})
    p171_claims = claims.get('P171', [])
    if not p171_claims:
        raise ValueError("No parent taxon for this species")

    parent_qid = p171_claims[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')
    genus_qid = find_nearest_taxon_qid(parent_qid, genera)
    if not genus_qid:
        raise ValueError("No genus found for this species")
    family_qid = find_nearest_taxon_qid(genus_qid, families)
    if not family_qid:
        raise ValueError("No family found for this species")
    expr_str = f'SpeciesDescriptionBuilding {genera[genus_qid]} {families[family_qid]}'
    expr = pgf.readExpr(expr_str)
    return expr

def build_genus_description_expr(genus_entity):

    claims = genus_entity.get('claims', {})
    p171_claims = claims.get('P171', [])
    if not p171_claims:
        raise ValueError("No parent taxon for this genus")
    parent_qid = p171_claims[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')
    family_qid = find_nearest_taxon_qid(parent_qid, families)
    if not family_qid:
        raise ValueError("No family found for this genus")
    expr_str = f'GenusDescriptionBuilding {families[family_qid]}'
    expr = pgf.readExpr(expr_str)
    return expr


def get_taxon_rank_qid(entity):
    claims = entity.get('claims', {})
    p105_claims = claims.get('P105', [])
    if not p105_claims:
        return None
    return p105_claims[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')


def build_university_expr(entity):
    uni_type = get_university_type(entity, public_qids, private_qids)
    if uni_type == 'public':
        kind_expr = 'publicKind'
    elif uni_type == 'private':
        kind_expr = 'privateKind'
    else:
        kind_expr = 'university_Kind'
    
    city_qid = get_university_located_city_qid(entity, set(cities.keys()))
    country_qid = get_university_country_qid(entity)

    print(f'[university] city_qid: {city_qid}, country_qid: {country_qid}')

    if city_qid and city_qid in cities and country_qid and country_qid in countries:
        location_expr = f'(CityCountryLocation {cities[city_qid]} {countries[country_qid]})'
        print(f'[university] CityCountryLocation: {location_expr}')
    elif country_qid and country_qid in countries:
        location_expr = f'(CountryLocation {countries[country_qid]})'
        print(f'[university] CountryLocation: {location_expr}')
    else:
        location_expr = 'noLocation'
        print(f'[university] no location found')

    year = get_university_foundation_year(entity)
    if year:
        attr_expr = f'(FoundedIn "{year}")'
    else:
        attr_expr = 'noAttr'

    expr_str = f'UniversityDescription {kind_expr} {location_expr} {attr_expr}'
    print(f'[university] expr_str: {expr_str}')
    expr = pgf.readExpr(expr_str)
    return expr


def build_city_expr(entity):
    province_qids = set(provinces.keys())
    country_qids = set(countries.keys())
    capital_of_qid, capital_type = get_city_capital_of_qid_and_type(entity, province_qids, country_qids)

    print(f'[city] capital_of_qid: {capital_of_qid}, capital_type: {capital_type}')

    if capital_type == 'country' and capital_of_qid in countries:
        print(f'[city] CountryForCaptial: {countries[capital_of_qid]}')
        expr_str = f'CountryForCaptial {countries[capital_of_qid]}'
        print(f'[city] expr_str: {expr_str}')
        expr = pgf.readExpr(expr_str)
        return expr

    elif capital_type == 'province' and capital_of_qid in provinces:
        country_qid = get_first_country_qid(entity)
        print(f'[city] ProvinceForCaptial: {provinces[capital_of_qid]}, country_qid: {country_qid}')
        if country_qid not in countries:
            raise ValueError(f"省会所属国家QID {country_qid} 不在 countries 字典中，数据异常！")
        expr_str = f'ProvinceForCaptial {provinces[capital_of_qid]} {countries[country_qid]}'
        print(f'[city] expr_str: {expr_str}')
        expr = pgf.readExpr(expr_str)
        return expr

    kind_qid = get_first_instance_of_qid(entity)
    kind_fun = city_kinds.get(kind_qid, 'Q515_City')
    kind_expr = kind_fun

    print(f'[city] kind_qid: {kind_qid}, kind_fun: {kind_fun}')

    province_qid = get_city_located_province_qid(entity, province_qids, country_qids)
    country_qid = get_first_country_qid(entity)
    print(f'[debug] province_qid = {province_qid}, in provinces = {province_qid in provinces}')
    print(f'[debug] country_qid = {country_qid}, in countries = {country_qid in countries}')

    if province_qid is not None and province_qid in provinces and country_qid is not None and country_qid in countries:
        location_expr = f'(ProvinceCountryLocation {provinces[province_qid]} {countries[country_qid]})'
        print(f'[city] ProvinceCountryLocation: {location_expr}')
    elif country_qid is not None and country_qid in countries:
        location_expr = f'(CountryLocation {countries[country_qid]})'
        print(f'[city] CountryLocation: {location_expr}')
    else:
        location_expr = 'noLocation'
        print(f'[city] no location found')

    expr_str = f'CityDescription {kind_expr} {location_expr}'
    print(f'[city] expr_str: {expr_str}')
    expr = pgf.readExpr(expr_str)
    return expr

def build_island_expr(entity):
    province_qids = set(provinces.keys())
    country_qids = set(countries.keys())
    waterbody_qids = set(waterbodies.keys())


    has_one_water, water_qid = get_single_body_of_water_qid(entity)
    print(f'[island] water_qid: {water_qid}')


    province_qid = get_city_located_province_qid(entity, province_qids, country_qids)
    country_qid = get_first_country_qid(entity)

    if province_qid and province_qid in provinces and country_qid and country_qid in countries:
        location_expr = f'(ProvinceCountryLocation {provinces[province_qid]} {countries[country_qid]})'
    elif country_qid and country_qid in countries:
        location_expr = f'(CountryLocation {countries[country_qid]})'
    else:
        location_expr = 'noLocation'


    kind_expr = 'Island'  

    if has_one_water and water_qid in waterbodies:
        expr_str = f'IslandDescription {waterbodies[water_qid]} {kind_expr} {location_expr}'
    else:
        expr_str = f'NoWaterIslandDescription {kind_expr} {location_expr}'

    print(f'[island] expr_str: {expr_str}')
    expr = pgf.readExpr(expr_str)
    return expr

def build_lake_expr(entity):
    province_qids = set(provinces.keys())
    country_qids = set(countries.keys())

    kind_expr = 'Lake'  

    province_qid = get_city_located_province_qid(entity, province_qids, country_qids)
    country_qid = get_first_country_qid(entity)

    if province_qid and province_qid in provinces and country_qid and country_qid in countries:
        location_expr = f'(ProvinceCountryLocation {provinces[province_qid]} {countries[country_qid]})'
    elif country_qid and country_qid in countries:
        location_expr = f'(CountryLocation {countries[country_qid]})'
    else:
        location_expr = 'noLocation'

    expr_str = f'LakeDescription {kind_expr} {location_expr}'
    print(f'[lake] expr_str: {expr_str}')
    expr = pgf.readExpr(expr_str)
    return expr

def build_human_expr(entity, language):
    name = get_name(entity)

    gender_str = get_gender_str(entity)
    gender_param = {
        "male": "Male",
        "female": "Female",
        "unknown": "Unknown"
    }[gender_str]
    person_expr = f'(PersonBuilding "{name}" {gender_param})'

    birth = get_birth_year(entity)
    death = get_death_year(entity)

    if language == 'ben':
        year_expr = build_bangla_year_expr(birth, death)
    else:
        year_expr = build_year_expr(birth, death)

    citizenship_qid = get_citizenship_qid(entity)
    birthplace_qid = get_birthplace_qid(entity)
    birthplace_country_qid = get_country_of_place_at_year(birthplace_qid, birth) if birthplace_qid and birth else None

    citizenship_fun = get_country_fun_from_qid(citizenship_qid) or None
    birthplace_fun = get_country_fun_from_qid(birthplace_country_qid)
    birthplace_expr = f'(Bornin {birthplace_fun})' if birthplace_fun else None

    prof_qids = get_profession_qids(entity, max_num=3)
    prof_expr = build_profession_expr(prof_qids)


    if not prof_expr or prof_expr.strip() == "":
        raise Exception("profession 没有在wikidata记录")


    if not citizenship_fun or citizenship_fun == "Unknown_Country":

        result = f"NationalityUnknown {person_expr} {prof_expr} {year_expr}"
        print(f"[build_human_expr] NationalityUnknown: {result}")
        return result

    if citizenship_fun == birthplace_fun or not birthplace_expr:
        result = f"SameNationalityBuilding {person_expr} {citizenship_fun} ({prof_expr}) {year_expr}"
        print(f"[build_human_expr] SameNationalityBuilding: {result}")
        return result
    else:
        result = f"DiffNationalityBuilding {person_expr} {citizenship_fun} {birthplace_expr} ({prof_expr}) {year_expr}"
        print(f"[build_human_expr] DiffNationalityBuilding: {result}")
        return result

def get_label(entity, lang='en'):
    return entity.get('labels', {}).get(lang, {}).get('value', '')

def build_description(qid):
    """
    Build description for a given QID.
    Automatically detect entity type and dispatch to the corresponding builder.
    Returns: (name_zh, name_en, zh, en) 
    """
    entity = get_wikidata_entity(qid)
    entity_type = get_entity_type(entity)
    name = get_name(entity)
    name_zh = get_label(entity, 'zh') or name
    name_en = get_label(entity, 'en') or name   

    if entity_type == 'human':
        expr_str = build_human_expr(entity, "chi")
        expr = pgf.readExpr(expr_str)
        zh = chinese_human.linearize(expr)
        expr_str = build_human_expr(entity, "eng")
        expr = pgf.readExpr(expr_str)
        en = english_human.linearize(expr)
        return name_zh, name_en, zh, en

    elif entity_type == 'university':
        expr = build_university_expr(entity)
        zh = chinese_place.linearize(expr)
        en = english_place.linearize(expr)
        return name_zh, name_en, zh, en

    elif entity_type == 'city':
        expr = build_city_expr(entity)
        zh = chinese_place.linearize(expr)
        en = english_place.linearize(expr)
        return name_zh, name_en, zh, en

    elif entity_type == 'island':
        expr = build_island_expr(entity)
        zh = chinese_place.linearize(expr)
        en = english_place.linearize(expr)
        return name_zh, name_en, zh, en

    elif entity_type == 'lake':
        expr = build_lake_expr(entity)
        zh = chinese_place.linearize(expr)
        en = english_place.linearize(expr)
        return name_zh, name_en, zh, en
    
    elif entity_type == 'taxon':  # instance of: taxon
        rank_qid = get_taxon_rank_qid(entity)
        if rank_qid == 'Q7432':  # species
            expr = build_species_description_expr(entity)
            zh = creature_chi.linearize(expr)
            en = creature_eng.linearize(expr)
            return name_zh, name_en, zh, en
        elif rank_qid == 'Q34740':  # genus
            expr = build_genus_description_expr(entity)
            zh = creature_chi.linearize(expr)
            en = creature_eng.linearize(expr)
            return name_zh, name_en, zh, en
        else:
            # 其它 taxon，不处理/raise/可自定义
            raise ValueError(f"Unsupported taxon rank QID: {rank_qid}")

    else:
        raise ValueError(f"Unsupported entity type: {entity_type}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <QID>")
        sys.exit(1)
    qid = sys.argv[1]
    try:
        name_zh, name_en, zh, en = build_description(qid)
        print(f"{name_zh}：{zh}")
        print(f"{name_en}: {en}")
        # if ben:
        #     print(f"{name_en} (Bengali): {ben}")
    except Exception as e:
        print(f"[ERROR] failed to process {qid}: {e}")