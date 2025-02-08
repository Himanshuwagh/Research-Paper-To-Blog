"""
EXTRACTS IMAGES AND SAVE IN OUTPUT DIRECTORY
"""
import subprocess
import os

def run_pdffigures2(pdf_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Command simplified to match pdffigures2 usage
    command = [
        "java", "-jar", 
        "pdffigures2/pdffigures2-assembly-1.0.jar", 
        pdf_path,  # PDF path as the first argument after the JAR
        "-m", f"{output_dir}/figures", 
        "-d", f"{output_dir}/data", 
        "-s", f"{output_dir}/stats.json"
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"pdffigures2 failed with error:\n{result.stdout}\n{result.stderr}")
        return
    
    # Here you would typically process the stats.json file, but since we're only trying to run it:
    print(f"Command executed. Check {output_dir} for outputs.")