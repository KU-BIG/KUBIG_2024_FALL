from django.shortcuts import HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt

nextID = 4
topics = [
    {"id": 1, "title": "routing", "body": "Routing is .."},
    {"id": 2, "title": "view", "body": "View is .."},
    {"id": 3, "title": "model", "body": "Model is .."},
]


def HTMLTemplate(articleTag, id=None):
    global topics
    contextUI = ""
    if id != None:
        contextUI = f"""
            <li>
                <form action="/delete/" method="post">
                    <input type="hidden" name="id" value={id}>
                    <input type="submit" value="delete">
                </form>
            </li>
            <li><a href="/update/{id}">update</a></li>
            """
    ol = ""
    for topic in topics:
        ol += f'<li><a href="/read/{topic["id"]}">{topic["title"]}</a></li>'
    return f"""
    <html>
    <body>
        <h1><a href="/">Django</a></h1>
        <ol>
            {ol}
        </ol>
        {articleTag}
        <ul>
            <li><a href="/create/">create</a></li>
            {contextUI}
        </ul>
    </body>
    </html>
    """


def index(request):
    article = """
    <h2>Welcome</h2>
    Hello,Django
    """
    return HttpResponse(HTMLTemplate(article))


# placeholder: 도움말
# textarea: 여러줄 입력 가능
@csrf_exempt
def create(request):
    global topics
    global nextID
    if request.method == "GET":
        article = """
            <form action="/create/" method="post">
                <p><input type="text" name="title" placeholder="title"></p>
                <p><textarea name="body" placeholder="body"></textarea></p>
                <p><input type="submit"></p>
            </form>
        """
        return HttpResponse(HTMLTemplate(article))
    elif request.method == "POST":
        title = request.POST["title"]
        body = request.POST["body"]
        newtopic = {"id": nextID, "title": title, "body": body}
        nextID += 1
        topics.append(newtopic)
        url = "/read/" + str(newtopic["id"])
        return redirect(url)


def read(request, id):
    global topics
    article = ""
    for topic in topics:
        if topic["id"] == int(id):
            article = f'<h2>{topic["title"]}</h2>{topic["body"]}'
    return HttpResponse(HTMLTemplate(article, id))


@csrf_exempt
def delete(request):
    global topics
    if request.method == "POST":
        id = request.POST["id"]
        newTopics = []
        for topic in topics:
            if topic["id"] != int(id):
                newTopics.append(topic)
        topics = newTopics
        return redirect("/")


def update(request, id):
    global topics
    if request.method == 'GET':
        for topic in topics:
            if topic['id'] == int(id):
                selectedTopic = {
                    "title":topic['title'], 
                    "body":topic['body']
                }
            article = """
                <form action="/update/{id}/" method="post">
                    <p><input type="text" name="title" placeholder="title" value={selectedTopic['title']}></p>
                    <p><textarea name="body" placeholder="body">{selectedTopic['body']}</textarea></p>
                    <p><input type="submit"></p>
                </form>
            """
        return HttpResponse(HTMLTemplate(article, id))
    elif request.method == 'POST':
        title = request.POST['title']
        body = request.POST['body']
        for topic in topics:
            if topic['id'] == int(id):
                topic['title'] = title
                topic['body'] = body
        return redirect(f'/read/{id}')
