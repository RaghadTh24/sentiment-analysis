from django.shortcuts import render
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from .models import Comment
from django.db.models import Count

model_path = "sentiment_model"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

sentiment_analyzer = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Label mapping: model labels to English
label_map = {
    "LABEL_0": "Negative",
    "LABEL_1": "Positive",
    "LABEL_2": "Neutral"
    
}

def home(request):
    sentiment = None
    score = None
    if request.method == "POST":
        comment = request.POST.get("comment")
        if comment:
            result = sentiment_analyzer(comment)[0]
            print(result)  # Example: {'label': 'LABEL_2', 'score': 0.99}
            label = result['label']
            score = round(result['score'], 2)
            sentiment = label_map.get(label, label)
            Comment.objects.create(text=comment, sentiment=sentiment)

    all_comments = Comment.objects.all().order_by('-id')
    return render(request, 'home.html', {
        'sentiment': sentiment,
        'score': score,
        'comments': all_comments
    })

def manager(request):
    comments = Comment.objects.all().order_by('-created_at')

    sentiment_counts = Comment.objects.values('sentiment').annotate(count=Count('sentiment'))

    sentiment_data = {
        'Positive': 0,
        'Neutral': 0,
        'Negative': 0
    }
    for item in sentiment_counts:
        sentiment = item['sentiment']
        count = item['count']
        sentiment_data[sentiment] = count

    return render(request, 'manager.html', {
        'comments': comments,
        'sentiment_data': sentiment_data
    })
