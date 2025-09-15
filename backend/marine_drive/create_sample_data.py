"""
Sample data creation script for Marine Drive
Run with: python manage.py shell < create_sample_data.py
"""

from organisms.models import TaxonomyRank, MarineOrganism, OrganismDetectionProfile

def create_sample_taxonomy():
    """Create basic taxonomy hierarchy"""
    
    # Create Kingdom level
    protista = TaxonomyRank.objects.create(name="Protista", level=1)
    plantae = TaxonomyRank.objects.create(name="Plantae", level=1)
    
    # Create Phylum level
    dinoflagellata = TaxonomyRank.objects.create(name="Dinoflagellata", level=2, parent=protista)
    bacillariophyta = TaxonomyRank.objects.create(name="Bacillariophyta", level=2, parent=protista)
    chlorophyta = TaxonomyRank.objects.create(name="Chlorophyta", level=2, parent=plantae)
    
    # Create Class level
    dinophyceae = TaxonomyRank.objects.create(name="Dinophyceae", level=3, parent=dinoflagellata)
    coscinodiscophyceae = TaxonomyRank.objects.create(name="Coscinodiscophyceae", level=3, parent=bacillariophyta)
    
    # Create Order level
    peridiniales = TaxonomyRank.objects.create(name="Peridiniales", level=4, parent=dinophyceae)
    
    # Create Family level
    peridiniaceae = TaxonomyRank.objects.create(name="Peridiniaceae", level=5, parent=peridiniales)
    
    # Create Genus level
    peridinium = TaxonomyRank.objects.create(name="Peridinium", level=6, parent=peridiniaceae)
    alexandrium = TaxonomyRank.objects.create(name="Alexandrium", level=6, parent=peridiniaceae)
    thalassiosira = TaxonomyRank.objects.create(name="Thalassiosira", level=6, parent=coscinodiscophyceae)
    
    # Create Species level
    peridinium_cinctum = TaxonomyRank.objects.create(name="cinctum", level=7, parent=peridinium)
    alexandrium_tamarense = TaxonomyRank.objects.create(name="tamarense", level=7, parent=alexandrium)
    thalassiosira_pseudonana = TaxonomyRank.objects.create(name="pseudonana", level=7, parent=thalassiosira)
    
    print("Created basic taxonomy hierarchy")
    
    return {
        'protista': protista,
        'plantae': plantae,
        'dinoflagellata': dinoflagellata,
        'bacillariophyta': bacillariophyta,
        'chlorophyta': chlorophyta,
        'peridinium': peridinium,
        'alexandrium': alexandrium,
        'thalassiosira': thalassiosira,
        'peridinium_cinctum': peridinium_cinctum,
        'alexandrium_tamarense': alexandrium_tamarense,
        'thalassiosira_pseudonana': thalassiosira_pseudonana
    }

def create_sample_organisms(taxonomy):
    """Create sample marine organisms"""
    
    organisms = []
    
    # Peridinium cinctum - Non-harmful dinoflagellate
    peridinium_organism = MarineOrganism.objects.create(
        scientific_name="Peridinium cinctum",
        common_name="Banded Peridinium",
        kingdom=taxonomy['protista'],
        phylum=taxonomy['dinoflagellata'],
        genus=taxonomy['peridinium'],
        species=taxonomy['peridinium_cinctum'],
        typical_size_min=25.0,
        typical_size_max=45.0,
        optimal_temperature_min=15.0,
        optimal_temperature_max=25.0,
        salinity_tolerance_min=0.5,
        salinity_tolerance_max=35.0,
        trophic_level='primary_producer',
        is_harmful=False,
        toxicity_level='none',
        carbon_sequestration_importance='moderate',
        description="A freshwater dinoflagellate commonly found in lakes and ponds. Important primary producer in aquatic ecosystems.",
        identification_notes="Distinctive brown coloration with visible plates. Moves with characteristic spinning motion."
    )
    organisms.append(peridinium_organism)
    
    # Alexandrium tamarense - Harmful algal bloom species
    alexandrium_organism = MarineOrganism.objects.create(
        scientific_name="Alexandrium tamarense",
        common_name="Alexandrium",
        kingdom=taxonomy['protista'],
        phylum=taxonomy['dinoflagellata'],
        genus=taxonomy['alexandrium'],
        species=taxonomy['alexandrium_tamarense'],
        typical_size_min=18.0,
        typical_size_max=32.0,
        optimal_temperature_min=10.0,
        optimal_temperature_max=20.0,
        salinity_tolerance_min=25.0,
        salinity_tolerance_max=35.0,
        trophic_level='primary_producer',
        is_harmful=True,
        toxicity_level='high',
        carbon_sequestration_importance='low',
        description="Marine dinoflagellate responsible for paralytic shellfish poisoning. Forms harmful algal blooms in coastal waters.",
        identification_notes="Reddish-brown color, chain-forming. Produces saxitoxin. Key indicator species for red tide events."
    )
    organisms.append(alexandrium_organism)
    
    # Thalassiosira pseudonana - Marine diatom
    thalassiosira_organism = MarineOrganism.objects.create(
        scientific_name="Thalassiosira pseudonana",
        common_name="Thalassiosira Diatom",
        kingdom=taxonomy['protista'],
        phylum=taxonomy['bacillariophyta'],
        genus=taxonomy['thalassiosira'],
        species=taxonomy['thalassiosira_pseudonana'],
        typical_size_min=4.0,
        typical_size_max=6.0,
        optimal_temperature_min=15.0,
        optimal_temperature_max=25.0,
        salinity_tolerance_min=30.0,
        salinity_tolerance_max=37.0,
        trophic_level='primary_producer',
        is_harmful=False,
        toxicity_level='none',
        carbon_sequestration_importance='high',
        description="Small marine diatom, important model organism for marine phytoplankton studies. Significant contributor to ocean carbon cycling.",
        identification_notes="Circular silica frustule with radial pattern. Very small size requires high magnification for identification."
    )
    organisms.append(thalassiosira_organism)
    
    print(f"Created {len(organisms)} sample organisms")
    
    # Create detection profiles for each organism
    for organism in organisms:
        profile = OrganismDetectionProfile.objects.create(
            organism=organism,
            model_confidence_threshold=0.75,
            shape_descriptors={
                "circularity": 0.8,
                "aspect_ratio": 1.2,
                "convexity": 0.9
            },
            color_profile={
                "dominant_hue": "brown" if "Peridinium" in organism.scientific_name else "green",
                "brightness_range": [0.3, 0.7],
                "saturation": 0.6
            },
            texture_features={
                "roughness": 0.4,
                "uniformity": 0.7,
                "entropy": 0.8
            }
        )
        print(f"Created detection profile for {organism.scientific_name}")
    
    return organisms

def main():
    """Main function to create all sample data"""
    print("Creating sample data for Marine Drive...")
    
    # Create taxonomy hierarchy
    taxonomy = create_sample_taxonomy()
    
    # Create sample organisms
    organisms = create_sample_organisms(taxonomy)
    
    print("\nSample data creation complete!")
    print(f"- Created {TaxonomyRank.objects.count()} taxonomy ranks")
    print(f"- Created {MarineOrganism.objects.count()} marine organisms")
    print(f"- Created {OrganismDetectionProfile.objects.count()} detection profiles")
    
    print("\nSample organisms created:")
    for organism in organisms:
        print(f"- {organism.scientific_name} ({organism.common_name})")
        print(f"  Size: {organism.size_range}, Harmful: {organism.is_harmful}")

if __name__ == "__main__":
    main()