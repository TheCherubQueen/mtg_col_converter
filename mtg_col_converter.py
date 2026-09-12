import datetime
import os
import shutil

import pandas
import pandas as pd
import requests
import gzip
import io


class MtgColConverter:

    def __init__(self, import_path, export_path, archive_path, offline_path, offline_mode, save_oracle):
        self.import_path = import_path
        self.export_path = export_path
        self.archive_path = archive_path
        self.offline_path = offline_path
        self.offline_mode = offline_mode
        self.save_oracle = save_oracle
        self.import_cols_to_drop = [
                           "Folder Name",
                           "Trade Quantity",
                           "Condition",
                           "Price Bought",
                           "Date Bought",
                           "AVG",
                           "LOW",
                           "TREND"
                           ]
        self.scryfall_cols_to_keep = [
                            'name',
                            'layout',
                            'set',
                            'set_name',
                            'collector_number'
                            ]
        self.scryfall_layouts_to_keep = [
                            'transform',
                            'modal_dfc',
                            #'split',
                            # 'adventure', #split, adventure and prepare seem to get picked up correctly by dragon shield
                            # 'prepare',
                            'flip'
                            ]
        self.files_used = []
        self.df_list = []

        self.scryfall_oracle_df = self.create_scryfall_oracle(
            self.scryfall_cols_to_keep,
            self.scryfall_layouts_to_keep
        )

    def create_scryfall_oracle(self,cols_to_keep,layouts_to_keep):
        if not offline_mode:
            print('Creating scryfall oracle via Bulk Data API')
            bulk_url = r"https://api.scryfall.com/bulk-data"
            bulk_json = requests.get(bulk_url, headers={"User-Agent": "Cherry's Formatting Helper"}).json()
            download_uri = bulk_json["data"][1]["jsonl_download_uri"]
            try:
                response = requests.get(download_uri)
                with gzip.open(io.BytesIO(response.content),'rt',encoding='utf-8') as oracle_jsonl:
                    oracle_df = pandas.read_json(oracle_jsonl, lines = True)
                if self.save_oracle:
                    print('Saving scryfall oracle to local folder')
                    save_path = offline_path + "\\scryfall_oracle_" + datetime.datetime.now().strftime("%b-%d-%Y_%H-%M-%S") + ".csv"
                    oracle_df.to_csv(save_path, index=False)
            except Exception as e:
                print(f"Unable to download scryfall oracle via Bulk Data API due to error:\n {e}")

        if offline_mode:
            most_recent_file = None
            most_recent_time = 0
            for file in os.scandir(self.offline_path):
                if file.is_file():
                    modified_time = file.stat().st_mtime_ns
                    if modified_time > most_recent_time:
                        most_recent_file = file
                        most_recent_time = modified_time
            print(f'Using {most_recent_file.name} as local scryfall oracle file')
            oracle_df = pd.read_csv(most_recent_file, low_memory=False)

        filtered_oracle_df = oracle_df[cols_to_keep]
        filtered_oracle_df = filtered_oracle_df[filtered_oracle_df.layout.isin(layouts_to_keep)]
        return filtered_oracle_df


    def read_csvs(self):
        print(f"\nDiscovering .csv files from: {self.import_path}")
        files_list = [file for file in os.listdir(self.import_path) if file.endswith(".csv")]
        if len(files_list) == 0:
            print("No .csv files found")
            return
        print(f"Found {len(files_list)} files:")
        print(*files_list, sep='\n')
        print("Reading files into pandas dataframes")
        for file in files_list:
            file_path = self.import_path + "\\" + file
            print(f"Reading from: {file_path}")
            df = pd.read_csv(file_path, header=1, dtype= str) #header = 1 skips a delimiter printout that's included in the csv
            self.df_list.append(df)
            self.files_used.append(file_path)

    def double_faced_name_detector(self):
        print("Checking for double faced cards")
        for card, row in self.df_list[0].iterrows():
            scanned_name = row['Card Name']
            scanned_number = row['Card Number']
            scanned_code = row['Set Code']
            name_matches = self.scryfall_oracle_df[self.scryfall_oracle_df['name'].str.contains(scanned_name, case= False, na= False, regex= False)]
            if not name_matches.empty:
                full_matches = name_matches[(name_matches['collector_number'] == scanned_number) & (name_matches['set'] == scanned_code.lower())]
                if len(full_matches) == 1:
                    matched_name = full_matches['name'].iloc[0]
                    print(f"Double faced card found: {scanned_name}, replaced with {matched_name}")
                    self.df_list[0].loc[card,'Card Name'] = matched_name
                elif len(full_matches) != 1:
                    print(f'Potential double faced card found: {scanned_name}, unable to automatically verify and replace \n full matches: {len(full_matches)}')


    def transform_dfs(self):
        print(f"\nFormatting data to match Archidekt importer")
        for df in self.df_list:
            df.drop(columns = self.import_cols_to_drop, inplace = True)


    def concat_dfs(self):
        print("\nConcatenating data")
        concat_df = pd.concat(self.df_list, ignore_index=True)
        self.df_list = [concat_df]

    def write_df(self):
        print("\nTidying Columns")
        self.df_list[0].drop(columns = 'Set Code', inplace=True)
        print("Writing to exports")
        filename = self.export_path + "\\mtg_export_" + datetime.datetime.now().strftime("%b-%d-%Y_%H-%M-%S") + ".csv"
        self.df_list[0].to_csv(filename, index=False)

    def archive_inputs(self):
        print("\nArchiving inputs")
        for file in self.files_used:
            archive_file_name = self.archive_path + "\\" + file.rsplit("\\", 1)[1]
            shutil.move(file, archive_file_name)


if __name__ == "__main__":
    print("Starting Column Converter")
    import_path = r"C:\Users\Jess\Documents\MtG_Importer"
    export_path = r"C:\Users\Jess\Documents\MtG_Importer\exports"
    archive_path = r"C:\Users\Jess\Documents\MtG_Importer\archive_input"
    offline_path = r"C:\Users\Jess\Documents\MtG_Importer\scryfall_oracle"

    invalidator = True
    while invalidator:
        offline_mode = input(
            r'Run in offline mode? (this will use the latest local download in MtG_Importer\scryfall_oracle) Y/N')
        if offline_mode.lower() == 'y' or offline_mode.lower() == 'yes':
            offline_mode = True
            save_oracle = False
            invalidator = False
        elif offline_mode.lower() == 'n' or offline_mode.lower() == 'no':
            offline_mode = False
            invalidator = False
        else:
            print('Please enter Y/N')

    if not offline_mode:
        invalidator = True
        while invalidator:
            save_oracle = input(r'Save the oracle file for local use later? Y/N')
            if save_oracle.lower() == 'y' or save_oracle.lower() == 'yes':
                save_oracle = True
                invalidator = False
            elif save_oracle.lower() == 'n' or save_oracle.lower() == 'no':
                save_oracle = False
                invalidator = False
            else:
                print('Please enter Y/N')

    converter =MtgColConverter(import_path, export_path, archive_path, offline_path, offline_mode,save_oracle)

    converter.read_csvs()
    if not converter.df_list :
        print(f"No files found in {import_path}")
        exit(1)

    try:
        converter.transform_dfs()
    except Exception as e:
        print(f'Failed to transform dataframe with exception:\n {e}')
        exit(1)

    if len(converter.df_list) > 1:
      converter.concat_dfs()

    converter.double_faced_name_detector()

    unique_sets = converter.df_list[0]["Set Name"].unique()
    print("\nFound cards from sets:")
    print(*unique_sets, sep='\n')
    converter.write_df()
    try:
        converter.archive_inputs()
    except Exception as e:
        print(f'Failed to archive inputs with exception:\n {e}')
    print("\nProcess complete, upload to Archidekt.com using the following col order:\nQuantity, Card Name, Edition Name, Collector Number, Foil/Variant, Language")
