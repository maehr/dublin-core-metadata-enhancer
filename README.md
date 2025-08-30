# dublin-core-metadata-enhancer

Enhance Dublin Core records with reproducible enrichment workflows. The data in this repository is openly available to everyone and is intended to support reproducible research.

[![GitHub issues](https://img.shields.io/github/issues/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer.svg)](https://github.com/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer/issues)
[![GitHub forks](https://img.shields.io/github/forks/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer.svg)](https://github.com/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer/network)
[![GitHub stars](https://img.shields.io/github/stars/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer.svg)](https://github.com/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer/stargazers)
[![Code license](https://img.shields.io/github/license/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer.svg)](https://github.com/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer/blob/main/LICENSE-AGPL.md)
[![Data license](https://img.shields.io/github/license/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer.svg)](https://github.com/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer/blob/main/LICENSE-CCBY.md)
[![DOI](https://zenodo.org/badge/GITHUB_REPO_ID.svg)](https://zenodo.org/badge/latestdoi/ZENODO_RECORD)

## Repository Structure

The structure of this repository follows the [Advanced Structure for Data Analysis](https://the-turing-way.netlify.app/project-design/project-repo/project-repo-advanced.html) of _The Turing Way_ and is organized as follows:

- `analysis/`: scripts and notebooks used to analyze the data
- `assets/`: images, logos, etc. used in the README and other documentation
- `build/`: scripts and notebooks used to build the data
- `data/`: data files
- `documentation/`: documentation for the data and the repository
- `project-management/`: project management documents (e.g., meeting notes, project plans, etc.)
- `src/`: source code for the data (e.g., scripts used to collect or process the data)
- `test/`: tests for the data and source code
- `report.md`: a report describing the analysis of the data

## Data Description

This repository contains Dublin Core metadata enhancement tools and workflows designed to improve the quality and completeness of Dublin Core metadata records. The data includes:

- **Enhancement Workflows**: Reproducible processes for enriching Dublin Core metadata
- **Validation Tools**: Scripts and utilities for quality assurance of enhanced metadata
- **Documentation**: Comprehensive guides and examples for using the enhancement pipelines
- **Test Data**: Sample Dublin Core records for testing and validation purposes

All enhancement workflows are documented and version-controlled to ensure reproducibility. The tools support various Dublin Core metadata formats and can be adapted for different types of digital collections.

Data models and field mappings are documented in the [documentation/](documentation/) directory. All code is released under the AGPL-3.0 license, and data products are released under the Creative Commons Attribution 4.0 International (CC BY 4.0) license.

## Use

### Metadata Enhancement Pipeline

This repository includes an automated metadata enhancement pipeline that generates WCAG 2.2-compliant alternative text for images using OpenAI's GPT-4o API.

#### Prerequisites

1. Python 3.8 or higher
2. OpenAI API key

#### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"
```

#### Usage

```bash
# Enhance metadata from the default source
python enhance_metadata.py

# Specify custom metadata URL and output file
python enhance_metadata.py --metadata-url "https://example.com/metadata.json" --output "enhanced_metadata.json"

# Use API key from command line
python enhance_metadata.py --api-key "your-api-key"
```

#### How it works

The enhancement pipeline:

1. **Loads** Dublin Core metadata from a JSON source
2. **Downloads** thumbnail images for each metadata object
3. **Analyzes** images using GPT-4o with contextual metadata
4. **Generates** WCAG-compliant alternative text in German
5. **Outputs** enhanced metadata as JSON

The AI prompt is designed to:

- Identify image types (informative, complex diagrams/maps, or text images)
- Generate appropriate alt text (max 120-200 characters)
- Create long descriptions for complex content when needed
- Follow accessibility best practices

#### Output Format

```json
{
	"objectid": "example001",
	"alt_text": "Karte von Basel als befestigte Grenzstadt, umgeben von Breisgau und Sundgau.",
	"longdesc": ""
}
```

#### Testing

```bash
# Run tests
python -m unittest test.test_metadata_enhancer
```

### Citation and Data Access

These data are openly available to everyone and can be used for any research or educational purpose. If you use this data in your research, please cite as specified in [CITATION.cff](CITATION.cff). The following citation formats are also available through _Zenodo_:

- [BibTeX](https://zenodo.org/record/ZENODO_RECORD/export/hx)
- [CSL](https://zenodo.org/record/ZENODO_RECORD/export/csl)
- [DataCite](https://zenodo.org/record/ZENODO_RECORD/export/dcite4)
- [Dublin Core](https://zenodo.org/record/ZENODO_RECORD/export/xd)
- [DCAT](https://zenodo.org/record/ZENODO_RECORD/export/dcat)
- [JSON](https://zenodo.org/record/ZENODO_RECORD/export/json)
- [JSON-LD](https://zenodo.org/record/ZENODO_RECORD/export/schemaorg_jsonld)
- [GeoJSON](https://zenodo.org/record/ZENODO_RECORD/export/geojson)
- [MARCXML](https://zenodo.org/record/ZENODO_RECORD/export/xm)

_Zenodo_ provides an [API (REST & OAI-PMH)](https://developers.zenodo.org/) to access the data. For example, the following command will return the metadata for the most recent version of the data

```bash
curl -i https://zenodo.org/api/records/ZENODO_RECORD
```

## Support

This project is maintained by [@Stadt-Geschichte-Basel](https://github.com/Stadt-Geschichte-Basel). Please understand that we can't provide individual support via email. We also believe that help is much more valuable when it's shared publicly, so more people can benefit from it.

| Type                                   | Platforms                                                                                                 |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| 🚨 **Bug Reports**                     | [GitHub Issue Tracker](https://github.com/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer/issues)    |
| 📊 **Report bad data**                 | [GitHub Issue Tracker](https://github.com/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer/issues)    |
| 📚 **Docs Issue**                      | [GitHub Issue Tracker](https://github.com/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer/issues)    |
| 🎁 **Feature Requests**                | [GitHub Issue Tracker](https://github.com/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer/issues)    |
| 🛡 **Report a security vulnerability** | See [SECURITY.md](SECURITY.md)                                                                            |
| 💬 **General Questions**               | [GitHub Discussions](https://github.com/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer/discussions) |

## Roadmap

No changes are currently planned.

## Contributing

All contributions to this repository are welcome! If you find errors or problems with the data, or if you want to add new data or features, please open an issue or pull request. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Versioning

We use [SemVer](http://semver.org/) for versioning. The available versions are listed in the [tags on this repository](https://github.com/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer/tags).

## Authors and acknowledgment

- **Moritz Mähr** - _Initial work_ - [maehr](https://github.com/maehr)

See also the list of [contributors](https://github.com/Stadt-Geschichte-Basel/dublin-core-metadata-enhancer/graphs/contributors) who contributed to this project.

## License

The data in this repository is released under the Creative Commons Attribution 4.0 International (CC BY 4.0) License - see the [LICENSE-CCBY](LICENSE-CCBY.md) file for details. By using this data, you agree to give appropriate credit to the original author(s) and to indicate if any modifications have been made.

The code in this repository is released under the GNU Affero General Public License v3.0 - see the [LICENSE-AGPL](LICENSE-AGPL.md) file for details. By using this code, you agree to make any modifications available under the same license.
