# IKEA Web Scraper

## CONTENTS OF THIS FILE

INTRODUCTION

REQUIREMENTS

INSTALLATION

USAGE

CREDITS

## INTRODUCTION

This is a web scraper designed based on rest api from woocomerce of you're site from ikea to retrieve information from IKEA and store it locally in a JSON file, as well as in an externally hosted S3 bucket.

## REQUIREMENTS

Make sure that you have all of these installed on the device you want to run the program on:

- php  / python 

## INSTALLATION

Use the package manager pip to install it. Type “pip install requests dotenv” into your terminal and it should download all the nassecery requirments. The main program is stored in the file “app.py” and can be run on any software capable of running Python3 code.

## USAGE

When running the __main__ program, it will open the IKEA website in a new window on Chrome, automatically navigate to the sofas page, and then identify the Xpath variable in the HTML code to find the container with all of the sofas in. Next it will click the “show more” button as many times as stipulated in the “range” variable in the “navigate_to_items” method. This loads all of the items in the subsequent pages so that all the sofas are displayed and can be accessed from the one page.

## CREDITS

MtheBest 
