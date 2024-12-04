from django.http.response import HttpResponseNotFound, JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from .chatbot import BonBot
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from UserData.models import Customer
from .models import Food, Restaurant, LLMChat
from pgvector.django import CosineDistance
import json

API_KEY = "AIzaSyCPz0WdsXp9dhYg_rWNZnGDINv11rqxi-I"

bon_bot = BonBot(api_key=API_KEY)
bon_bot_chain =  bon_bot.get_llm_chain()
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=API_KEY)


def rag_context_filter(documents: list):
    null_filtered_documents = filter(lambda doc: True if doc.distance else False, documents)
    filtered_documents = filter(lambda doc: True if doc.distance < 0.25 else False, null_filtered_documents)
    context_list = []
    for doc in filtered_documents:
        context = f'''
            Food Name: {doc.name}
            Restaurant Name: {doc.restaurant.name}
            Food Description:
            {doc.description} 
        '''
        context_list.append(context)

    strutured_filtered_context = "\n".join(context_list)
    return strutured_filtered_context



@csrf_exempt
def chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            query = data.get("query", "")
            bon_bot.chat_history.append(
                {
                    "role": "user",
                    "content": f"{query}"
                }
            )
            print(query)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        if query:
            #try:
            embedding = embeddings.embed_query(query)
            #food = Food.objects.order_by(CosineDistance('embedding', embedding))[0]
            food = Food.objects.annotate(
                distance=CosineDistance("embedding", embedding)
            ).order_by("distance")
            print([f.distance for f in food])
            context = rag_context_filter(food)
            response = bon_bot_chain.invoke({'query':query ,'context':context, 'history':bon_bot.chat_history})
            bon_bot.chat_history.append(
                {
                    "role": "user",
                    "content": f"{response}"
                }
            )
            return JsonResponse({"response": f"{response}"})
        
        else:
            return JsonResponse({"error": "No query provided."}, status=400)

    return HttpResponseNotFound("Invalid request method. Please use POST.")

@csrf_exempt
def clear_chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            action = data.get("action", "")
        except json.JSONDecodeError:
            return JsonResponse({"response": "Invalid JSON format"}, status=400)

        if action.lower() == "erase":
            bon_bot.clear_chat_history()
            return JsonResponse({"response": "Chat History Erased"}, status=200)
        else:
            return JsonResponse({"response": "Invalid Action. Read the Documentation."}, status=400)

    return HttpResponseNotFound("Invalid request method. Please use POST.")

@csrf_exempt
def insert_food(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            name = data.get("name", "")
            restaurant_id = data.get("restaurant_id", "")
            description = data.get("description", "")
           
        except json.JSONDecodeError:
            return JsonResponse({"response": "Invalid JSON format"}, status=400)
        
        try:
            restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
            context = f'''
            Food Name: {name}
            Restaurant Name: {restaurant.name}
            Food Description:
            {description} 
            '''

            embedding = embeddings.embed_query(context)

            Food.objects.create(
                name=name,
                restaurant=restaurant,
                description=description,
                embedding=embedding
            )
            return JsonResponse({"response": "Successfully Inserted"}, status=200)
        except ValueError:
            return JsonResponse({"reponse": "Failed to Insert"}, status=400)
            
    return HttpResponseNotFound("Invalid request method. Please use POST.")

@csrf_exempt
def test_vector(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            search_query = data.get("query", "")
        except json.JSONDecodeError:
                return JsonResponse({"response": "Invalid JSON format"}, status=400)
        
        try:
            embedding = embeddings.embed_query(search_query)
            print(type(embedding))
            food = Food.objects.order_by(CosineDistance('embedding', embedding))[0]
            return JsonResponse({"response": f"{food.name} - {food.description}"})
        
        except ValueError:
            return JsonResponse({"response": "Failed to retrieve the data"})
        
    return HttpResponseNotFound("Invalid request method. Please use POST.")

@csrf_exempt
def get_fooditems(request):
    if request.method == "POST":
        try:
            info = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"response": "Invalid JSON format"}, status=400)
        
        restaurant_id = info.get("restaurant_id", "")
        restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
        food_items = Food.objects.filter(restaurant = restaurant)
        food_list = []
        for food in food_items:
            food_list.append({
                'food_id': food.food_id,
                'name': food.name,
                'cuisine_type': food.cuisine_type,
                'food_category': food.food_category,
                'rating': food.rating,
                'available': food.availability
            })
        return JsonResponse(food_list, safe=False)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

@csrf_exempt
def restauarant_details(request):
    if request.method == 'POST':
        try:
            info = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"response": "Invalid JSON format"}, status=400)    
        restaurant_id = info.get("restaurant_id", "")
        restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
        if not restaurant_id:
            return JsonResponse({"response": "restaurant_id is required"}, status=400)
        try:
            restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
        except Restaurant.DoesNotExist:
            return JsonResponse({"response": "Restaurant not found"}, status=404)
        restaurant_detail = {
            'restaurant_id' : restaurant.restaurant_id,
            'name' : restaurant.name,
            'cuisine' : restaurant.cuisine,
            'rating' : restaurant.rating,
            'location' : restaurant.location,
            'contact_no' : restaurant.contact_no
            }
        return JsonResponse(restaurant_detail, safe=False)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

@csrf_exempt    
def topfive_restaurants(request):
    if request.method == "POST":
        restaurants = Restaurant.objects.order_by('-rating')[:5]
        restaurant_list = []
        for restaurant in restaurants:
            restaurant_list.append({
                'restaurant_id' : restaurant.restaurant_id,
                'name' : restaurant.name,
                'cuisine' : restaurant.cuisine,
                'rating' : restaurant.rating,
                'location' : restaurant.location,
                'contact_no' : restaurant.contact_no
            })
        return JsonResponse(restaurant_list, safe=False)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)