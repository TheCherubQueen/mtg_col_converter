# Ramble
## Why?
I use the Dragon Shield scanning app to scan any new cards I get, but I then use Archidekt to store my collection and create decklists and the like. I chose Dragon Shield because they don't currently seem to have any significant limits on exporting the scans from there app for use elsewhere, but the formatting can be a little janky. So I made this tool to deal with some of the more annoying things that come up when transferring scans to Archidekt.

## Key issues
* The order of columns that Dragon Shield use in its CSV output are different to the order that Archidekt's importer pre-set for Dragon Shield will populate.
* Dragon Shield adds in a lot of superfluous columns for my needs.
* The name formatting for double faced cards differs between Dragon Shield's output and Archidekt's inputs. This often means the Archidekt importer will fail to find double faced cards.

# Converter Features
* Remove any unneeded columns from input CSVs (such as purchase price, LOW, AVG, High price information etc.)
* Replace any double sided card names with the Scryfall double sided naming conventions and flag any that could be double sided but were not able to be identified with certainty.
* Creation of a formatted csv ready for upload to Archidekt

## Notes
* In order to carry out double faced name checks and replacements the tool will require access to the Scryfall unique artwork database. The tool can automatically download and use the latest database from Scryfall via the Scryfall API. The tool can also run in offline mode, where a CSV version of the database is used instead. If you do not have a CSV version of the database, running the tool with offline mode set to off and selecting Y to saving oracle database will write the latest version of the database to a local folder for use offline at later times.
* Currently everything is hardcoded to my own personal file paths. This is a tool that I doubt anyone else will have use for and is mostly an excuse for me to develop my coding skills while actually carrying out a useful task for me

## Possible Future Developments
These are not concrete commitments from me, rather something I would do if I were to develop this further at some point.
* Adding dynamic file locations rather than hard coded ones
* Adding in the option to retain certain columns from Dragon Shield if desired
* Adding support for inputs from other popular scanning apps
* Adding support for exports to other popular collection managers

# User Guide
* download the converter python script
* decide where you want your input directory to be and create the following as subfolders:
    * archive_input
    * exports
    * scryfall_oracle
* Change the hardcoded directory paths in the converter main function to reflect your changes
* Add any Dragon Shield export csv to the input directory (not in a sub folder, just in the directory)
* Run the converter script, following the input prompts as desired
* After a successful run, the exports folder will have a formatted csv ready for upload to Archidekt
* Upload the CSV to Archidekt using the importer settings specified by the tool
* Done
