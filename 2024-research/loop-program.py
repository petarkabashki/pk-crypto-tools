#%%


#%%

import subprocess

def run_script_until_match(script_name, search_string):
    while True:
        # Start the script as a subprocess
        process = subprocess.Popen(['python', script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Continuously read the output line by line
        for line in iter(process.stdout.readline, ''):
            print(line, end='')  # Print each line to the console

            # Check if the line contains the search string
            if search_string in line:
                print(f"Match found: '{search_string}'")
                process.stdout.close()  # Close the stdout pipe
                process.kill()  # Kill the subprocess
                return  # Exit the function

        process.wait()  # Wait for the process to complete in case the loop exits before the process ends

if __name__ == "__main__":
    script_to_run = '/backtest-donch-asset-timeframes.py'  # Replace with the name of the script you want to run
    search_string = 'Done asset 478'  # Replace with the string you are searching for

    run_script_until_match(script_to_run, search_string)


#%%