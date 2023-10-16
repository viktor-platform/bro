# Changelog

## (v0.2.9) (16/10/2023)
### Added

### Fixed
- Rerolled changes in XML file returned from BRO REST API as the API changed back to working with package version v0.2.6

## (v0.2.8) (06/10/2023)
### Added
- Added calculation of total cpt length as property of CPTCharacteristics, if available

### Fixed
- Breaking change in XML file returned from BRO REST API 

## (v0.2.7) (04/10/2023)
### Fixed
- Breaking change in XML file returned from BRO REST API 

## (v0.2.6) (17/5/2023)
### Fixed
- Fix failing built due to wrong PyPI Classifier 

## (v0.2.5) (17/5/2023)
### Fixed
- Fixed fetching of quality class in CPtcharacteristics
- Fixed wrong licensing in setup.py

## (v0.2.4) (07/4/2023)
### Fixed
- Fixed type comparison if there are no documents 

## (v0.2.3) (07/4/2023)
### Fixed
- Fixed character length in setup.py project_urls

## (v0.2.2) (07/4/2023)
### Added
- Added rejection reason in get_cpt_characteristics

### Fixed
- Fixed bugs for optional values in CPTCharacteristics

## (v0.2.1rc5) (31/3/2023)
### Fixed
- Inconsistent tags

## (v0.2.1rc4) (31/3/2023)
### Removed
- Temporarily remove project urls

## (v0.2.1rc3) (31/3/2023)

### Added
- Added functionality to define an area (Circle, Envelope)  
- Added functionality to communicate with BRO REST API and retrieve CPT availability in area
- Added parsing functionality of the Characteristics
- Added parsing functionality of the returned CPT XML files from the BRO
- Added functionality to get the available CPTs within the requested area in GeoJSON format
- Added tests

### Changed

### Deprecated

### Removed

### Fixed

### Security
