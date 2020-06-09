import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from requests.compat import quote_plus
from . import models

BASE_CRAIGSLIST_URL = 'https://capetown.craigslist.org/search/?query={}'
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'


def home(request):
    return render(request, 'base.html')


def search_results(request):
     # get search term from the base.html search bar
    search = request.POST.get('search')
     # create new database object based on the search
    models.Search.objects.create(search=search)
    # combine the search term with the craigslist base URL  to generate the search URL
    # use the final URL to get the data from the web
    final_url = BASE_CRAIGSLIST_URL.format(quote_plus(search))
    response = requests.get(final_url)
    data = response.text
    # use BeautifulSoup to convert the raw HTML to an object
    soup = BeautifulSoup(data, features='html.parser')
    # find all the 'result-row' elements in the object, 
    post_listings = soup.find_all('li', {'class': 'result-row'})
    #generate an empty list
    final_postings = []

    # loop through all the results and filter out the data we want to display
    # save the filtered data into local variables and write those as a tupple 
    # into the final_postings list 
    for post in post_listings:
        post_title = post.find(class_='result-title').text
        post_url = post.find('a').get('href')

        if post.find(class_='result-price'):
            post_price = post.find(class_='result-price').text
        else:
            post_price = 'N/A'

        if post.find(class_='result-image').get('data-ids'):
            # BeautifulSoup cannot access the images class automatically, 
            # first image link is retrieved using the data-ids, 
            # split is used to seperate the actual image source from the string
            post_image_id = post.find(class_='result-image').get('data-ids').split(',')[0].split(':')[1]
            # combine the BASE IMAGE URL with the image source to create an image link to bedisplayed
            post_image_url = BASE_IMAGE_URL.format(post_image_id)
            print(post_image_url)
        else:
            post_image_url = 'https://craigslist.org/images/peace.jpg'

        final_postings.append((post_title, post_url, post_price, post_image_url))
        # save the data for the new_search page to display the results
    stuff_for_frontend = {
        'search': search,
        'final_postings': final_postings,
    }

    return render(request, 'app/search_results.html', stuff_for_frontend)

