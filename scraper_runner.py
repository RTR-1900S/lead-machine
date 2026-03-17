import subprocess
import os
import tempfile
from datetime import datetime


def get_timestamped_filename(prefix="leads", extension="csv"):
    """Generate a timestamped filename: leads_2026-03-12_14-32.csv"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return f"{prefix}_{timestamp}.{extension}"


def run_scraper(keyword: str, city: str, max_results: int = 20) -> dict:
    """
    Runs google-maps-scraper via subprocess with timestamped output.

    Args:
        keyword: Search keyword (e.g., "restaurant")
        city: City location (e.g., "Orlando FL")
        max_results: Maximum results to retrieve

    Returns:
        dict with keys: success (bool), count (int), filename (str), error (str or None)
    """

    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # Generate timestamped filename
    timestamped_filename = get_timestamped_filename("leads", "csv")
    output_file = os.path.join("output", timestamped_filename)

    try:
        # Create a temporary input file with the query
        # google-maps-scraper expects: one query per line in input file
        # Format: "keyword city"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write(f"{keyword} {city}\n")
            input_file = f.name

        try:
            # Build the command for google-maps-scraper
            # Correct syntax: google-maps-scraper -input input.txt -results output.csv -depth N
            # The -depth flag controls how far the scraper scrolls (more depth = more results)
            # Rough mapping: depth 1 ~ 20 results, depth 2 ~ 40, etc.
            depth = max(1, (max_results + 19) // 20)  # Convert max_results to depth
            cmd = [
                "google-maps-scraper",
                "-input", input_file,
                "-results", output_file,
                "-depth", str(depth),
            ]

            # Run the scraper
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return {
                    "success": False,
                    "count": 0,
                    "filename": None,
                    "error": f"Scraper failed: {error_msg}"
                }

            # Check if output file was created
            if not os.path.exists(output_file):
                return {
                    "success": False,
                    "count": 0,
                    "filename": None,
                    "error": "Output file was not created by scraper"
                }

            # Count rows in the CSV (excluding header)
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    count = sum(1 for line in f) - 1  # Subtract 1 for header
            except Exception:
                count = 0

            return {
                "success": True,
                "count": count,
                "filename": timestamped_filename,
                "error": None
            }

        finally:
            # Clean up temporary input file
            if os.path.exists(input_file):
                try:
                    os.remove(input_file)
                except OSError:
                    pass

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "count": 0,
            "filename": None,
            "error": "Scraper timed out after 600 seconds (10 minutes)"
        }

    except FileNotFoundError:
        return {
            "success": False,
            "count": 0,
            "filename": None,
            "error": "google-maps-scraper not found. Ensure it's installed: go install github.com/gosom/google-maps-scraper@latest"
        }

    except Exception as e:
        return {
            "success": False,
            "count": 0,
            "filename": None,
            "error": f"Unexpected error: {str(e)}"
        }
