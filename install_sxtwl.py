#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_sxtwl_install():
    try:
        # Try to import sxtwl
        import sxtwl
        logging.info("sxtwl package is already installed.")
        return True
    except ImportError:
        logging.info("sxtwl package is not installed. Will try to install it.")
        return False

def install_sxtwl():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sxtwl==2.0.7"])
        logging.info("Successfully installed sxtwl.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install sxtwl: {str(e)}")
        return False

def test_sxtwl():
    try:
        import sxtwl
        
        # Get information for January 1, 2000
        day_obj = sxtwl.fromSolar(2000, 1, 1)
        
        # Print basic information
        logging.info(f"Lunar Year: {day_obj.getLunarYear()}")
        logging.info(f"Lunar Month: {day_obj.getLunarMonth()}")
        logging.info(f"Lunar Day: {day_obj.getLunarDay()}")
        logging.info(f"Is Leap Month: {day_obj.isLunarLeap()}")
        
        # Get GanZhi information
        gz_year = day_obj.getYearGZ()
        gz_month = day_obj.getMonthGZ()
        gz_day = day_obj.getDayGZ()
        
        logging.info(f"Year GanZhi: {gz_year.tg},{gz_year.dz}")
        logging.info(f"Month GanZhi: {gz_month.tg},{gz_month.dz}")
        logging.info(f"Day GanZhi: {gz_day.tg},{gz_day.dz}")
        
        # Calculate hour GanZhi
        hour = 12  # Noon
        shi_gz = sxtwl.getShiGz(gz_day.tg, hour)
        logging.info(f"Hour GanZhi (API): {shi_gz.tg},{shi_gz.dz}")
        
        logging.info("sxtwl test successful!")
        return True
        
    except Exception as e:
        logging.error(f"sxtwl test failed: {str(e)}")
        return False

def print_installation_guide():
    logging.info("\n" + "="*80)
    logging.info("SXTWL INSTALLATION GUIDE")
    logging.info("="*80)
    logging.info("\nTo install sxtwl package, you need Microsoft Visual C++ Build Tools:")
    logging.info("\n1. Download and install the Microsoft C++ Build Tools:")
    logging.info("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    logging.info("\n2. During installation, select the following:")
    logging.info("   - C++ build tools core features")
    logging.info("   - Windows 10 SDK")
    logging.info("\n3. After installation, run this script again to install sxtwl package.")
    logging.info("\nAlternatively, you can download a pre-built wheel from PyPI if available:")
    logging.info("   pip install --only-binary=:all: sxtwl==2.0.7")
    logging.info("\nIf you're using Python 64-bit, make sure to install the 64-bit build tools.")
    logging.info("="*80 + "\n")
    
if __name__ == "__main__":
    logging.info("Checking sxtwl installation...")
    
    if not check_sxtwl_install():
        logging.info("Attempting to install sxtwl...")
        if not install_sxtwl():
            logging.error("Failed to install sxtwl. You may need Microsoft Visual C++ Build Tools.")
            print_installation_guide()
            sys.exit(1)
    
    # Test if sxtwl works properly
    if test_sxtwl():
        logging.info("sxtwl is working correctly.")
    else:
        logging.error("sxtwl is not working properly.")
        sys.exit(1) 