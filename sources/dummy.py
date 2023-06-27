import os
import requests
from time import sleep


def download_metadata(
    target_directory,
    links=[
        "http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2559997/bin/1756-3305-1-29-S1.mpg",
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10036205/bin/10-1055-a-2048-6170-i3798ev2.jpg",
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=9206064%E2%80%9D"
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10036205/figure/FI3798-2/",
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC460005/figure/F1/",
    ],
):
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    for link in links:
        try:
            # Dateinamen aus dem Link extrahieren
            filename = os.path.basename(link)

            # Datei herunterladen
            response = requests.get(link)
            with open(os.path.join(target_directory, filename), "wb") as file:
                file.write(response.content)

            # Fortschritt melden
            print("Datei heruntergeladen:", filename)

        except Exception as e:
            print("Fehler beim Herunterladen der Datei:", str(e))

        fake_filesize = 1234
        for i in range(0, fake_filesize, 123):
            yield {"url": "" + filename, "completed": i, "total": fake_filesize}
            sleep(0.5)

    # Nachdem alle Links abgearbeitet wurden, wird das Skript beendet
    return


def list_articles(target_directory, supplementary_materials=False, skip=[]):
    for fake_media in [
        {
            "name": "Parasit_Vectors/Parasit_Vectors_2008_Sep_1_1_29.nxml",
            "doi": "10.1186/1756-3305-1-29",
            "article-contrib-authors": "Behnke J, Buttle D, Stepek G, Lowe A, Duce I",
            "article-title": "Developing novel anthelmintics from plant cysteine proteinases",
            "article-abstract": "Intestinal helminth infections of livestock and humans are predominantly controlled by treatment with three classes of synthetic drugs, but some livestock nematodes have now developed resistance to all three classes and there are signs that human hookworms are becoming less responsive to the two classes (benzimidazoles and the nicotinic acetylcholine agonists) that are licensed for treatment of humans. New anthelmintics are urgently needed, and whilst development of new synthetic drugs is ongoing, it is slow and there are no signs yet that novel compounds operating through different modes of action, will be available on the market in the current decade. The development of naturally-occurring compounds as medicines for human use and for treatment of animals is fraught with problems. In this paper we review the current status of cysteine proteinases from fruits and protective plant latices as novel anthelmintics, we consider some of the problems inherent in taking laboratory findings and those derived from folk-medicine to the market and we suggest that there is a wealth of new compounds still to be discovered that could be harvested to benefit humans and livestock.",
            "journal-title": "Parasites & Vectors",
            "article-year": 2008,
            "article-month": 9,
            "article-day": 1,
            "article-url": "http://dx.doi.org/10.1186/1756-3305-1-29",
            "article-license-url": "http://creativecommons.org/licenses/by/2.0",
            "article-copyright-holder": "Behnke et al; licensee BioMed Central Ltd.",
            "supplementary-materials": [
                {
                    "label": "",
                    "caption": "Additional file 1 A single adult female living specimen of  Heligmosomoides bakeri  was mounted on a microscope slide in Hanks's saline and sandwiched beneath a glass coverslip supported on petroleum jelly. The worm was imaged using a Zeiss Axiovert 135TV inverted microscope and photographed using a Scion CFW 1310 M digital camera. A solution of 25 μM papain was introduced below the coverslip and images were captured on a PC using Streampix III time-lapse software at a frame rate of approximately 1 image every 3 seconds for 30 minutes. The video file was edited and exported as an mpeg running at 10 times the original speed. The file is titled "
                    "H. bakeri female papain.mpg"
                    " and initially shows the worm freely moving in the papain solution. After the animal forms a helical coil, a lesion appears on the left of the worm. This is followed by rupture of the worm and loss of the viscera through the rupture leading to the death of the parasite.",
                    "mimetype": "video",
                    "mime-subtype": "mpeg",
                    "url": "http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2559997/bin/1756-3305-1-29-S1.mpg",
                }
            ],
        }
    ]:
        yield fake_media

        if "supplementary-materials" in fake_media and supplementary_materials:
            for material in fake_media["supplementary-materials"]:
                if material["url"] not in skip:
                    download_metadata(target_directory, material["url"])

    return
