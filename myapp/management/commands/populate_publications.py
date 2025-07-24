from django.core.management.base import BaseCommand
from myapp.models import Publication


class Command(BaseCommand):
    help = 'Populate publications from BibTeX data'

    def handle(self, *args, **options):
        # Clear existing publications (optional - remove this if you want to keep existing ones)
        Publication.objects.all().delete()
        self.stdout.write("Cleared existing publications")

        # Complete publications data with all your BibTeX entries
        publications_data = [
            {
                'bibtex_entry': '''@article{yahaya2024framework,
  title={A framework for compressed weighted nonnegative matrix factorization},
  author={Yahaya, Farouk and Puigt, Matthieu and Delmaire, Gilles and Roussel, Gilles},
  journal={IEEE Transactions on Signal Processing},
  year={2024},
  publisher={IEEE}
}''',
                'featured': True  # Most recent, prestigious journal
            },
            {
                'bibtex_entry': '''@article{ciulla2024two,
  title={Two-dimensional adaptive Whittaker--Shannon Sinc-based zooming},
  author={Ciulla, Carlo and Shabani, Blerta and Yahaya, Farouk},
  journal={Applied Research},
  pages={e2400018},
  year={2024}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@inproceedings{yahaya2021compressive,
  title={Compressive informed (semi-) non-negative matrix factorization methods for incomplete and large-scale data: with application to mobile crowd-sensing data},
  author={Yahaya, Farouk},
  year={2021},
  organization={Universit{\'e} du Littoral C{\^o}te d'Opale}
}''',
                'featured': True  # PhD thesis work
            },
            {
                'bibtex_entry': '''@inproceedings{yahaya2021methodes,
  title={M{\'e}thodes {\'e}tendues de factorisation inform{\'e}e de matrices ou tenseurs (semi-) non-n{\'e}gatifs pour l'analyse de donn{\'e}es incompl{\`e}tes et de grande dimension: Application au traitement de donn{\'e}es issues du mobile crowdsensing},
  author={Yahaya, Farouk},
  year={2021},
  organization={Littoral}
}''',
                'featured': False  # French version of thesis
            },
            {
                'bibtex_entry': '''@inproceedings{yahaya2021random,
  title={Random projection streams for (weighted) nonnegative matrix factorization},
  author={Yahaya, Farouk and Puigt, Matthieu and Delmaire, Gilles and Roussel, Gilles},
  booktitle={ICASSP 2021-2021 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  pages={3280--3284},
  year={2021},
  organization={IEEE}
}''',
                'featured': True  # ICASSP is prestigious
            },
            {
                'bibtex_entry': '''@inproceedings{puigt2021situ,
  title={In situ calibration of cross-sensitive sensors in mobile sensor arrays using fast informed non-negative matrix factorization},
  author={Puigt, Matthieu and Yahaya, Farouk and Delmaire, Gilles and Roussel, Gilles and others},
  booktitle={ICASSP 2021-2021 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  pages={3515--3519},
  year={2021},
  organization={IEEE}
}''',
                'featured': True  # ICASSP collaboration
            },
            {
                'bibtex_entry': '''@inproceedings{yahaya2021fast,
  title={Fast informed nonnegative matrix factorization for mobile sensor calibration},
  author={Yahaya, Farouk and Puigt, Matthieu and Thanh, Olivier Vu and Delmaire, Gilles and Roussel, Gilles},
  booktitle={GdR ISIS (Groupement de Recherche Information Signal Image viSion): Statistical learning with missing values},
  year={2021}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@article{yahaya2020gaussian,
  title={Gaussian compression stream: principle and preliminary results},
  author={Yahaya, Farouk and Puigt, Matthieu and Delmaire, Gilles and Roussel, Gilles},
  journal={arXiv preprint arXiv:2011.05390},
  year={2020}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@inproceedings{yahaya2019acceleration,
  title={Acc{\'e}l{\'e}ration de la factorisation pond{\'e}r{\'e}e en matrices non-n{\'e}gatives par projections al{\'e}atoires},
  author={Yahaya, Farouk and Puigt, Matthieu and Delmaire, Gilles and Roussel, Gilles},
  booktitle={GRETSI 2019-XXVII{\`e}me Colloque francophonede traitement du signal et des images},
  pages={265--268},
  year={2019}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@inproceedings{yahaya2019apply,
  title={How to apply random projections to nonnegative matrix factorization with missing entries?},
  author={Yahaya, Farouk and Puigt, Matthieu and Delmaire, Gilles and Roussel, Gilles},
  booktitle={2019 27th European Signal Processing Conference (EUSIPCO)},
  pages={1--5},
  year={2019},
  organization={IEEE}
}''',
                'featured': True  # EUSIPCO is well-known
            },
            {
                'bibtex_entry': '''@inproceedings{yahaya2019fast,
  title={Fast \\& furious: accelerating weighted NMF using random projections},
  author={Yahaya, Farouk and Puigt, Matthieu and Delmaire, Gilles and Roussel, Gilles},
  booktitle={Workshop on Low-Rank Models and Applications (LRMA)},
  year={2019}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@inproceedings{yahaya2019nmf,
  title={NMF for Big Data with Missing Entries: A Random Projection Based Approach},
  author={Yahaya, Farouk and Puigt, Matthieu and Delmaire, Gilles and Roussel, Gilles},
  booktitle={6{\\`e}me Journ{\'e}e R{\'e}gionale des Doctorants en Automatique et Traitement du Signal (JRDA)},
  year={2019}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@inproceedings{yahaya2019non,
  title={Non-Negative Matrix Factorization with Missing Entries: A Random Projection Based Approach},
  author={Yahaya, Farouk and Puigt, Matthieu and Delmaire, Gilles and Roussel, Gilles},
  booktitle={Journ{\'e}e des jeunes chercheurs en Traitement du signal et de l'image 2019 GRAISyHM TSI 2019},
  year={2019}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@inproceedings{puigt2019cartographie,
  title={Cartographie et {\'e}talonnage de capteurs conjoints par traitement des donn{\'e}es issues de capteurs mobiles},
  author={Puigt, Matthieu and Dorffer, Cl{\'e}ment and Yahaya, Farouk and Delmaire, Gilles and Roussel, Gilles},
  booktitle={Colloque National Capteurs et Sciences Participatives},
  year={2019}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@article{yahaya2018faster,
  title={Faster-than-fast NMF using random projections and Nesterov iterations},
  author={Yahaya, Farouk and Puigt, Matthieu and Delmaire, Gilles and Roussel, Gilles},
  journal={arXiv preprint arXiv:1812.04315},
  year={2018}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@inproceedings{yahaya2018calibration,
  title={Calibration en ligne d'un r{\'e}seau de capteurs mobiles par factorisation matricielle},
  author={Yahaya, Farouk and Dorffer, Cl{\'e}ment and Puigt, Matthieu and Delmaire, Gilles and Roussel, Gilles},
  booktitle={Individual Air Pollution Sensors: Innovation or Revolution?},
  year={2018}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@inproceedings{yahaya2018random,
  title={Do random projections fasten an already fast NMF technique using Nesterov optimal gradient?},
  author={Yahaya, Farouk and Puigt, Matthieu and Delmaire, Gilles and Roussel, Gilles},
  booktitle={5{\\`e}me Journ{\'e}e R{\'e}gionale des Doctorants en Automatique et Traitement du Signal (JRDA)},
  year={2018}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@article{yahaya2017edge,
  title={Edge finding in magnetic resonance imaging applications: the calculation of the first order derivative of two dimensional images},
  author={Yahaya, Farouk},
  journal={International Journal of Applied Pattern Recognition},
  volume={4},
  number={3},
  pages={226--245},
  year={2017},
  publisher={Inderscience Publishers (IEL)}
}''',
                'featured': True  # Single-author publication
            },
            {
                'bibtex_entry': '''@article{yahaya2017towards,
  title={Towards an Optimized Mathematical Form of an Edge Detector},
  author={Yahaya, Farouk},
  journal={European Journal of Information Science and Technology Vol},
  volume={2},
  pages={27},
  year={2017}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@article{ciulla2016novel,
  title={A novel approach to T2-weighted MRI filtering: the classic-curvature and the signal resilient to interpolation filter masks},
  author={Ciulla, Carlo and Yahaya, Farouk and Adomako, Edmund and Shikoska, Ustijana Rechkoska and Agyapong, Grace and Veljanovski, Dimitar and Risteski, Filip A},
  journal={International Journal of Information Engineering and Electronic Business},
  volume={8},
  number={1},
  pages={1},
  year={2016},
  publisher={Modern Education and Computer Science Press}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@article{carlo2015compilation,
  title={A compilation on the contribution of the classic-curvature and the intensity-curvature functional to the study of healthy and pathological MRI of the human brain},
  author={Carlo, Ciulla and Risteski, Filip A. and Veljanovski, Dimitar and Shikoska Rechkoska, Ustijana and Adomako, Edmund and Yahaya, Farouk},
  journal={Int. J. Applied Pattern Recognition, Vol. 2, No. 3, 2015 213},
  volume={2},
  year={2015},
  publisher={Inderscience}
}''',
                'featured': False
            },
            {
                'bibtex_entry': '''@article{puigtproposition,
  title={Proposition de stage recherche M2 en laboratoire 2019-2020},
  author={Puigt, Mattthieu and Yahaya, Farouk and Delmaire, Gilles and Roussel, Gilles}
}''',
                'featured': False  # Administrative document
            },
        ]

        # Create publications from the data
        created_count = 0
        for pub_data in publications_data:
            try:
                publication = Publication(
                    bibtex_entry=pub_data['bibtex_entry'],
                    featured=pub_data.get('featured', False)
                )
                publication.save()  # This will automatically parse the BibTeX
                created_count += 1
                self.stdout.write(f"Created: {publication.title}")
            except Exception as e:
                self.stdout.write(f"Error creating publication: {e}")

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} publications')
        )

        featured_count = sum(1 for pub in publications_data if pub.get('featured', False))
        self.stdout.write(f"Featured publications (will appear randomly on homepage): {featured_count}")
        self.stdout.write(f"Total publications: {created_count}")