#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep

def download_metadata(target_directory):
    for fake_file in [
        'http://example.org/file1',
        'http://example.org/file2',
        'http://example.org/file3'
    ]:
        fake_filesize = 1234
        for i in range(0, fake_filesize, 123):
            yield {
                'url': '' + fake_file,
                'completed': i,
                'total': fake_filesize
            }
            sleep(0.5)

def list_articles(target_directory, supplementary_materials=False, skip=[]):
    for fake_media in [
        {
            'name': "Parasit_Vectors/Parasit_Vectors_2008_Sep_1_1_29.nxml".decode('utf-8'),
            'doi': '10.1186/1756-3305-1-29',
            'article-contrib-authors': "Behnke J, Buttle D, Stepek G, Lowe A, Duce I".decode('utf-8'),
            'article-title': "Developing novel anthelmintics from plant cysteine proteinases".decode('utf-8'),
            'article-abstract': "Intestinal helminth infections of livestock and humans are predominantly controlled by treatment with three classes of synthetic drugs, but some livestock nematodes have now developed resistance to all three classes and there are signs that human hookworms are becoming less responsive to the two classes (benzimidazoles and the nicotinic acetylcholine agonists) that are licensed for treatment of humans. New anthelmintics are urgently needed, and whilst development of new synthetic drugs is ongoing, it is slow and there are no signs yet that novel compounds operating through different modes of action, will be available on the market in the current decade. The development of naturally-occurring compounds as medicines for human use and for treatment of animals is fraught with problems. In this paper we review the current status of cysteine proteinases from fruits and protective plant latices as novel anthelmintics, we consider some of the problems inherent in taking laboratory findings and those derived from folk-medicine to the market and we suggest that there is a wealth of new compounds still to be discovered that could be harvested to benefit humans and livestock.".decode('utf-8'),
            'journal-title': "Parasites & Vectors".decode('utf-8'),
            'article-year': 2008,
            'article-month': 9,
            'article-day': 1,
            'article-url': "http://dx.doi.org/10.1186/1756-3305-1-29".decode('utf-8'),
            'article-license-url': "http://creativecommons.org/licenses/by/2.0".decode('utf-8'),
            'article-copyright-holder': "Behnke et al; licensee BioMed Central Ltd.".decode('utf-8'),
            'supplementary-materials': [
                {
                    'label': "".decode('utf-8'),
                    'caption': "Additional file 1 A single adult female living specimen of  Heligmosomoides bakeri  was mounted on a microscope slide in Hanks's saline and sandwiched beneath a glass coverslip supported on petroleum jelly. The worm was imaged using a Zeiss Axiovert 135TV inverted microscope and photographed using a Scion CFW 1310 M digital camera. A solution of 25 μM papain was introduced below the coverslip and images were captured on a PC using Streampix III time-lapse software at a frame rate of approximately 1 image every 3 seconds for 30 minutes. The video file was edited and exported as an mpeg running at 10 times the original speed. The file is titled ""H. bakeri female papain.mpg"" and initially shows the worm freely moving in the papain solution. After the animal forms a helical coil, a lesion appears on the left of the worm. This is followed by rupture of the worm and loss of the viscera through the rupture leading to the death of the parasite.".decode('utf-8'),
                    'mimetype': "video".decode('utf-8'),
                    'mime-subtype': "mpeg".decode('utf-8'),
                    'url': "http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2559997/bin/1756-3305-1-29-S1.mpg".decode('utf-8')
                }
            ]
        }
    ]:
        yield fake_media
