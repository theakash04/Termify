import subprocess
import sys
import argparse

def run_streamlit():
    """Function to run Streamlit app"""
    print("Starting Streamlit...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit/app.py"])
    except KeyboardInterrupt:
        print("\nStreamlit stopped gracefully.")

def run_snowflake():
    """Function to run snowflake/main.py script"""
    print("Running snowflake main.py...")
    try:
        subprocess.run([sys.executable, "snowflake/main.py"])
    except KeyboardInterrupt:
        print("\nKeyboardInterrupted Execution stopped.")

def main():
    parser = argparse.ArgumentParser(description="Run Streamlit or Snowflake app.")
    subparsers = parser.add_subparsers(dest='command', help="Subcommands")

    # Subcommand for running Streamlit
    subparsers.add_parser('app:streamlit', help="Run Streamlit app")

    # Subcommand for running Snowflake main script
    subparsers.add_parser('app:main', help="Run snowflake main.py")

    args = parser.parse_args()
    if args.command == 'app:streamlit':
        run_streamlit()
    elif args.command == 'app:main':
        run_snowflake()
    else:
        print("Invalid command. Use 'app:streamlit' or 'app:main'.")

if __name__ == "__main__":
    main()

