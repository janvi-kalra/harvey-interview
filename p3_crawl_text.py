import fitz
import os
from openai import OpenAI
import ast
import csv

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

CLASSIFY_PROMPT = "You are an expert at classifying whether the provided text relates to the Termination, Indemnification, or Confidentiality of an acquisition. Given the section name and the section content, return Termination, Indemnification, Confidentiality, or None"


def clean(str):
    return str.strip("\n").replace("\n", " ")


def classify(section_name, section_body):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "system",
            "content": CLASSIFY_PROMPT,
        }, {
            "role":
            "user",
            "content":
            f"section name: {section_name}. section content: {section_body}"
        }])
    result = completion.choices[0].message.content
    if result == "Termination" or result == "Indemnification" or result == "Confidentiality" or result == "None":
        return result
    return "None"


def create_page_to_num(pdf_path, toc_pages):
    page_to_num = {}

    doc = fitz.open(pdf_path)
    for page_num in toc_pages:
        page = doc.load_page(page_num)

        links = page.get_links()
        for link in links:
            if link['kind'] == fitz.LINK_GOTO:
                link_text = page.get_text("text", clip=link['from'])
                toc_page_num = link['page']
                page_to_num[clean(link_text)] = toc_page_num

    return page_to_num


def add_section_bodies(pdf_path, toc_pages, page_to_num):
    doc = fitz.open(pdf_path)
    csv_file_path = os.path.join(
        'chunks',
        os.path.basename(pdf_path).replace('.Pdf', '.csv'))

    updated_data = []

    for page_num in toc_pages:
        page = doc.load_page(page_num)

        with open(csv_file_path, mode='r', newline='',
                  encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)  # Read the header
            header.append(
                "Classification")  # Add 'Classification' column to the header
            updated_data.append(header)

            for line in reader:
                section_name = line[1]
                text = ""

                search_start = page_to_num[clean(section_name)]
                # search_end = page_to_num[section_name]
                for page_num in range(search_start, search_start + 1):
                    page = doc.load_page(page_num)
                    text += page.get_text()

                classification = classify(section_name, text)

                line[2] = text
                line.append(classification)
                updated_data.append(line)

        with open(csv_file_path, mode='w', newline='',
                  encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(updated_data)


def iterate_folder(folder_path):
    final_result = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            toc_pages = sorted(TOC_PAGES_PART_ONE_MAPPING[filename])

            page_to_num = create_page_to_num(pdf_path, toc_pages)
            add_section_bodies(pdf_path, toc_pages, page_to_num)
    print(final_result)


TOC_PAGES_PART_ONE_MAPPING = {
    'NATIONAL INSTRUMENTS CORP_20230525_DEFM14A_20911673_4672792.Pdf': {8, 6},
    'Myovant Sciences Ltd._20230123_DEFM14A_20573637_4573939.Pdf': {8, 9, 6},
    'Argo Group International Holdings, Ltd._20230320_DEFM14A_20737540_4621891.Pdf':
    {5, 6, 7},
    'Seagen Inc._20230424_DEFM14A_20812583_4650531.Pdf': {5, 6},
    'STORE CAPITAL Corp_20221104_DEFM14A_20428387_4540170.Pdf': {4, 5},
    'Veoneer, Inc._20211115_DEFM14A_19656349_4335019.Pdf': {9, 10, 11, 7},
    'Blue Safari Group Acquisition Corp_20230327_DEFM14A_20752338_4627890.Pdf':
    {8, 9},
    'ChemoCentryx, Inc._20220914_DEFM14A_20340331_4518092.Pdf': {8, 7},
    'GCP Applied Technologies Inc._20220131_DEFM14A_19806508_4372223.Pdf':
    {6, 7},
    'ALKURI GLOBAL ACQUISITION CORP._20210930_DEFM14A_19561988_4303635.Pdf':
    {6},
    'Intersect ENT, Inc._20210907_DEFM14A_19520364_4290965.Pdf': {5, 7},
    'SYNNEX CORP_20210609_DEFM14A_19338736_4236234.Pdf': {8, 9, 7},
    'KANSAS CITY SOUTHERN_20211103_DEFM14A_19625972_4325028.Pdf':
    {9, 10, 11, 12},
    'HANGER, INC._20220826_DEFM14A_20309851_4510081.Pdf': {6, 7},
    'Meridian Bancorp, Inc._20210622_DEFM14A_19361639_4244116.Pdf': {8, 9, 10},
    'Radius Global Infrastructure, Inc._20230505_DEFM14A_20858042_4661091.Pdf':
    {8, 9},
    'TIVITY HEALTH, INC._20220524_DEFM14A_20120335_4468156.Pdf': {8, 19, 6, 7},
    'McAfee Corp._20220104_DEFM14A_19754815_4361365.Pdf': {8, 6, 7},
    'RAVEN INDUSTRIES INC_20210806_DEFM14A_19454710_4273900.Pdf': {2, 3},
    'TEGNA INC_20220413_DEFM14A_20013265_4441404.Pdf': {8, 9, 7},
    'QAD INC_20210909_DEFM14A_19523541_4291901.Pdf': {8, 6, 7},
    'PREFERRED APARTMENT COMMUNITIES INC_20220414_DEFM14A_20015574_4442255.Pdf':
    {4, 5, 6},
    'Sumo Logic, Inc._20230405_DEFM14A_20779809_4641204.Pdf': {8, 6},
    'CorePoint Lodging Inc._20220114_DEFM14A_19776758_4365965.Pdf': {6, 7},
    'MONMOUTH REAL ESTATE INVESTMENT CORP_20211221_DEFM14A_19731738_4356032.Pdf':
    {5, 7},
    'NATUS MEDICAL INC_20220602_DEFM14A_20144466_4472051.Pdf': {8, 6, 7},
    'Spirit Airlines MA.Pdf': {6, 7},
    'AMERICAN CAMPUS COMMUNITIES INC_20220616_DEFM14A_20169998_4477606.Pdf':
    {5, 6},
    '1Life Healthcare Inc_20220824_DEFM14A_20299948_4508791.Pdf': {5, 6},
    'Switch, Inc._20220627_DEFM14A_20186829_4481092.Pdf': {17, 5, 6, 7},
    'CORPORATE PROPERTY ASSOCIATES 18 GLOBAL INC_20220427_DEFM14A_20041574_4449712.Pdf':
    {8, 6},
    'Anaplan, Inc._20220502_DEFM14A_20059827_4454121.Pdf': {6, 7},
    'Sailpoint Technologies Holdings, Inc._20220531_DEFM14A_20138375_4470787.Pdf':
    {8, 6, 7},
    'AVALARA, INC._20220912_DEFM14A_20334857_4516123.Pdf': {8, 7},
    'PLANTRONICS INC CA_20220517_DEFM14A_20103137_4464750.Pdf': {6, 7},
    'IROBOT CORP_20220907_DEFM14A_20329897_4514467.Pdf': {6, 7},
    'Ping Identity Holding Corp._20220916_DEFM14A_20342713_4518798.Pdf':
    {8, 6, 7},
    'BOTTOMLINE TECHNOLOGIES INC_20220202_DEFM14A_19817567_4374090.Pdf': {
        5, 6
    },
    'Cornerstone OnDemand Inc_20210910_DEFM14A_19526835_4292932.Pdf': {
        5, 6, 7
    },
    'Hilton Grand Vacations Inc._20210621_DEFM14A_19358725_4243052.Pdf': {
        6, 7
    },
    'Inovalon Holdings, Inc._20211015_DEFM14A_19586362_4312352.Pdf': {8, 9, 7},
    'KnowBe4, Inc._20221222_DEFM14A_20521596_4563944.Pdf': {8, 9, 7},
    'Cloudera, Inc._20210719_DEFM14A_19410828_4260317.Pdf': {5, 6},
    'COWEN INC._20221011_DEFM14A_20384577_4528659.Pdf': {8, 6, 7},
    'SPX FLOW, Inc._20220201_DEFM14A_19813071_4373457.Pdf': {4, 5, 6, 7, 8},
    'MOMENTIVE GLOBAL INC._20230427_DEFM14A_20826404_4653973.Pdf': {8, 6},
    'Watermark Lodging Trust, Inc._20220615_DEFM14A_20166959_4476791.Pdf': {4},
    'Hill-Rom Holdings, Inc._20211020_DEFM14A_19594022_4314928.Pdf': {4, 6},
    'ForgeRock, Inc._20221208_DEFM14A_20498573_4557310.Pdf': {8, 6},
    'Poshmark, Inc._20221125_DEFM14A_20473310_4552195.Pdf': {8, 6, 7},
    'Univar Solutions Inc._20230502_DEFM14A_20844849_4658083.Pdf': {5, 6},
    'TERMINIX GLOBAL HOLDINGS INC_20220907_DEFM14A_20330027_4514503.Pdf': {
        9, 10, 11, 12, 13, 16
    },
    'Zendesk MA.Pdf': {8, 6},
    'CAI International, Inc._20210804_DEFM14A_19444962_4270736.Pdf': {
        9, 11, 7
    },
    'MEREDITH CORP_20211108_DEFM14A_19636450_4328874.Pdf': {6, 7},
    'ALLEGHANY CORP DE_20220429_DEFM14A_20052995_4452227.Pdf': {12, 5, 6, 7},
    'PS BUSINESS PARKS, INC.MD_20220608_DEFM14A_20155205_4474225.Pdf': {5, 6},
    'ATLAS AIR WORLDWIDE HOLDINGS INC_20221019_DEFM14A_20395325_4531934.Pdf': {
        8, 6, 7
    },
    'DUCK CREEK TECHNOLOGIES, INC._20230228_DEFM14A_20680687_4596980.Pdf': {
        9, 7
    },
    'ARENA PHARMACEUTICALS INC_20220103_DEFM14A_19751337_4360734.Pdf': {
        8, 6, 7
    },
    'Echo Global Logistics, Inc._20211021_DEFM14A_19595960_4315476.Pdf': {
        5, 6, 7
    },
    'Sierra Oncology, Inc._20220516_DEFM14A_20099747_4463777.Pdf': {6, 7},
    'US Ecology, Inc._20220329_DEFM14A_19977995_4426339.Pdf': {11, 6},
    'Bluerock Residential Growth REIT, Inc._20220311_DEFM14A_19938922_4406918.Pdf':
    {15, 5, 6, 7},
    'NUVASIVE INC_20230328_DEFM14A_20755850_4630097.Pdf': {16, 14, 15},
    'TravelCenters of America Inc. MD_20230403_DEFM14A_20770239_4639300.Pdf': {
        5, 6, 7
    },
    'Medallia, Inc._20210914_DEFM14A_19531748_4294624.Pdf': {8, 6, 7},
    'Diversey Holdings, Ltd._20230515_DEFM14A_20878784_4665936.Pdf': {
        9, 10, 11
    },
    'TENNECO INC_20220426_DEFM14A_20034100_4448087.Pdf': {1, 5, 6, 7, 19},
    'XILINX INC_20210305_DEFM14A_19107214_4148221.Pdf': {10},
    'BTRS Holdings Inc._20221110_DEFM14A_20444054_4544754.Pdf': {9, 10, 6, 7},
    'AEROJET ROCKETDYNE HOLDINGS, INC._20230213_DEFM14A_20635156_4584450.Pdf':
    {4, 6},
    'VONAGE HOLDINGS CORP_20220110_DEFM14A_19765909_4363201.Pdf': {5, 6, 7},
    'SANDERSON FARMS INC_20210913_DEFM14A_19528141_4293580.Pdf': {6, 7},
    'COVETRUS, INC._20220913_DEFM14A_20336819_4516858.Pdf': {6, 7},
    'Ranger Oil Corp_20230518_DEFM14A_20894462_4669228.Pdf': {9, 10, 11, 12},
    'CVENT HOLDING CORP._20230503_DEFM14A_20848314_4658730.Pdf': {8, 6},
    'Maxar Technologies Inc._20230316_DEFM14A_20730460_4617137.Pdf': {8, 6, 7},
    'UserTesting, Inc._20221206_DEFM14A_20494905_4556398.Pdf': {6, 7},
    'Oak Street Health, Inc._20230330_DEFM14A_20760527_4632592.Pdf': {8, 6, 7},
    'MERITOR, INC._20220418_DEFM14A_20019751_4444368.Pdf': {4, 5, 6},
    'Activision Blizzard, Inc._20220321_DEFM14A_19960426_4418687.Pdf': {
        8, 9, 10
    },
    'MERIDIAN BIOSCIENCE INC_20220908_DEFM14A_20331967_4514903.Pdf': {6, 7},
    'ROGERS CORP_20211216_DEFM14A_19721647_4352864.Pdf': {5, 6, 7},
    'Prometheus Biosciences, Inc._20230516_DEFM14A_20886960_4667711.Pdf': {
        8, 9
    },
    'CITRIX SYSTEMS INC_20220316_DEFM14A_19951567_4414270.Pdf': {12, 13},
    'VMWARE, INC._20221003_DEFM14A_20371516_4525585.Pdf': {7},
    'CyrusOne Inc._20211230_DEFM14A_19745922_4359686.Pdf': {5, 6, 7},
    'MAGELLAN HEALTH INC_20210219_DEFM14A_19054835_4126183.Pdf': {5, 6, 7},
    'DUKE REALTY CORP_20220802_DEFM14A_20251209_4495981.Pdf': {8, 9, 10},
    'Coupa Software Inc_20230123_DEFM14A_20571922_4573621.Pdf': {8, 17, 6, 7},
    'MONEYGRAM INTERNATIONAL INC_20220421_DEFM14A_20027475_4446252.Pdf': {
        5, 6, 7
    },
    'Mandiant, Inc._20220428_DEFM14A_20042183_4449873.Pdf': {8, 6, 7},
    'Resource REIT, Inc._20220314_DEFM14A_19942780_4408792.Pdf': {4, 5, 6},
    'AEROJET ROCKETDYNE HOLDINGS, INC._20210205_DEFM14A_19007640_4113036.Pdf':
    {4, 5, 7},
    'Nuance Communications, Inc._20210517_DEFM14A_19281720_4221662.Pdf': {
        8, 6
    },
    'HESKA CORP_20230508_DEFM14A_20858914_4661346.Pdf': {9, 7},
    'Altra Industrial Motion Corp._20221214_DEFM14A_20506388_4559723.Pdf': {
        19, 6, 7
    },
    'Global Blood Therapeutics, Inc._20220829_DEFM14A_20311227_4510555.Pdf': {
        8, 6
    },
    'Kadmon Holdings, Inc._20211004_DEFM14A_19567888_4305283.Pdf': {6},
    'Archaea Energy Inc._20221114_DEFM14A_20445339_4545162.Pdf': {12, 6, 7}
}

# iterate_folder("dataset")

filename = 'ALKURI GLOBAL ACQUISITION CORP._20210930_DEFM14A_19561988_4303635.Pdf'
pdf_path = f'dataset/{filename}'
toc_pages = sorted(TOC_PAGES_PART_ONE_MAPPING[filename])
page_to_num = create_page_to_num(pdf_path, toc_pages)
print('page to num', page_to_num)
add_section_bodies(pdf_path, toc_pages, page_to_num)
